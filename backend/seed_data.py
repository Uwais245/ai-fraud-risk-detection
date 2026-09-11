import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionChannel
from app.models.risk_assessment import RiskAssessment
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.rule import Rule, RuleAction
from app.services.ml_integration import ml_service
from app.services.ai_integration import ai_service


# Sample data
CUSTOMERS = [f"CUST-{i:04d}" for i in range(1, 51)]
DEVICES = [f"DEV-{i:03d}" for i in range(1, 21)]
IPS = [f"192.168.{i}.{j}" for i in range(1, 10) for j in range(1, 20)]
LOCATIONS = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
MERCHANT_CATEGORIES = ["electronics", "clothing", "groceries", "entertainment", "travel", "restaurant", "gas", "pharmacy", "home", "beauty"]
CHANNELS = [TransactionChannel.WEB, TransactionChannel.MOBILE, TransactionChannel.API]


def generate_transaction_data(customer_id: str, base_amount: float = 100) -> dict:
    """Generate realistic transaction data"""
    is_suspicious = random.random() < 0.15  # 15% suspicious
    
    if is_suspicious:
        amount = round(random.uniform(500, 5000), 2)
        account_age = random.randint(1, 30)
        txn_count = random.randint(1, 5)
        avg_amount = round(random.uniform(10, 100), 2)
        channel = random.choice([TransactionChannel.WEB, TransactionChannel.API])
        avs_match = random.choice([True, False])
        cvv_result = random.choice([True, False])
    else:
        amount = round(random.uniform(10, 500), 2)
        account_age = random.randint(30, 1000)
        txn_count = random.randint(5, 100)
        avg_amount = round(random.uniform(20, 200), 2)
        channel = random.choice(CHANNELS)
        avs_match = True
        cvv_result = True
    
    return {
        "customer_id": customer_id,
        "amount": Decimal(str(amount)),
        "currency": "USD",
        "country": "US",
        "bin_country": "US" if random.random() > 0.1 else random.choice(["CA", "GB", "DE", "FR"]),
        "channel": channel,
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "promo_used": random.random() < 0.2,
        "avs_match": avs_match,
        "cvv_result": cvv_result,
        "three_ds_flag": random.random() < 0.3,
        "shipping_distance_km": Decimal(str(round(random.uniform(0, 5000), 2))),
        "account_age_days": account_age,
        "total_transactions_user": txn_count,
        "avg_amount_user": Decimal(str(avg_amount)),
        "ip_address": random.choice(IPS),
        "device_id": random.choice(DEVICES),
        "device_type": random.choice(["mobile", "desktop", "tablet"]),
        "location": random.choice(LOCATIONS),
    }


async def seed_users(db: AsyncSession):
    """Create default users"""
    users_data = [
        {"email": "admin@fraud.com", "password": "admin123", "full_name": "Admin User", "role": UserRole.ADMIN, "is_superuser": True},
        {"email": "manager@fraud.com", "password": "manager123", "full_name": "Business Manager", "role": UserRole.BUSINESS_MANAGER},
        {"email": "analyst@fraud.com", "password": "analyst123", "full_name": "Fraud Analyst", "role": UserRole.ANALYST},
        {"email": "analyst2@fraud.com", "password": "analyst123", "full_name": "Senior Analyst", "role": UserRole.ANALYST},
    ]
    
    for udata in users_data:
        stmt = select(User).where(User.email == udata["email"])
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            user = User(
                email=udata["email"],
                hashed_password=get_password_hash(udata["password"]),
                full_name=udata["full_name"],
                role=udata["role"],
                is_superuser=udata.get("is_superuser", False)
            )
            db.add(user)
    
    await db.commit()
    print("✓ Users seeded")


async def seed_rules(db: AsyncSession):
    """Create default rules"""
    admin = (await db.execute(select(User).where(User.role == UserRole.ADMIN))).scalar_one()
    
    rules_data = [
        {
            "name": "High Amount Transaction",
            "description": "Flag transactions over $5000",
            "condition": {"field": "amount", "operator": "gt", "value": 5000},
            "action": RuleAction.INCREASE_RISK,
            "risk_increase": 40,
        },
        {
            "name": "New Account High Value",
            "description": "New account (< 14 days) making high-value transaction (> $500)",
            "condition": {"field": "account_age_days", "operator": "lt", "value": 14},
            "action": RuleAction.INCREASE_RISK,
            "risk_increase": 30,
        },
        {
            "name": "CVV/AVS Mismatch",
            "description": "CVV or AVS verification failed",
            "condition": {"field": "cvv_result", "operator": "eq", "value": 0},
            "action": RuleAction.INCREASE_RISK,
            "risk_increase": 50,
        },
        {
            "name": "High Velocity",
            "description": "More than 10 transactions in short period",
            "condition": {"field": "total_transactions_user", "operator": "gt", "value": 10},
            "action": RuleAction.INCREASE_RISK,
            "risk_increase": 20,
        },
        {
            "name": "Cross-Border New Account",
            "description": "International transaction from new account (< 30 days)",
            "condition": {"field": "account_age_days", "operator": "lt", "value": 30},
            "action": RuleAction.INCREASE_RISK,
            "risk_increase": 25,
        },
    ]
    
    for rdata in rules_data:
        stmt = select(Rule).where(Rule.name == rdata["name"])
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            rule = Rule(**rdata, created_by=admin.id)
            db.add(rule)
    
    await db.commit()
    print("✓ Rules seeded")


async def seed_transactions(db: AsyncSession, count: int = 500):
    """Generate sample transactions"""
    # Get or create a default user for transactions
    user = (await db.execute(select(User).where(User.role == UserRole.ANALYST))).scalar_one()
    
    created_count = 0
    
    for i in range(count):
        customer_id = random.choice(CUSTOMERS)
        txn_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:06d}"
        
        # Check if exists
        stmt = select(Transaction).where(Transaction.transaction_id == txn_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            continue
        
        # Generate transaction data
        txn_data = generate_transaction_data(customer_id)
        txn_data["transaction_id"] = txn_id
        
        # Create transaction
        # Add some time variation
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        transaction = Transaction(
            **txn_data,
            user_id=user.id,
            created_at=created_at
        )
        db.add(transaction)
        await db.flush()
        
        # Score with ML
        risk_result = ml_service.score_transaction(txn_data)
        
        # AI explanation
        ai_explanation = None
        if risk_result.get("risk_flags"):
            ai_explanation = ai_service.generate_explanation(
                risk_result["risk_flags"],
                {"amount": txn_data["amount"], "customer_id": customer_id}
            )
        
        # Create risk assessment
        risk_assessment = RiskAssessment(
            transaction_id=txn_id,
            ml_anomaly_score=risk_result.get("ml_anomaly_score", 0),
            rule_engine_score=risk_result.get("rule_engine_score", 0),
            final_risk_score=risk_result["final_risk_score"],
            risk_level=risk_result["risk_level"],
            decision=risk_result["decision"],
            risk_flags=risk_result["risk_flags"],
            ai_explanation=ai_explanation,
            assessed_at=created_at + timedelta(seconds=1)
        )
        db.add(risk_assessment)
        
        # Create alert if high risk
        if risk_result["risk_level"] == "HIGH":
            alert = Alert(
                transaction_id=txn_id,
                severity=AlertSeverity.HIGH,
                reason="; ".join(risk_result["risk_flags"][:3]),
                status=AlertStatus.NEW,
                risk_score=int(risk_result["final_risk_score"]),
                risk_flags=risk_result["risk_flags"],
                ai_explanation=ai_explanation,
                created_at=created_at + timedelta(seconds=2)
            )
            db.add(alert)
        
        created_count += 1
        
        if created_count % 50 == 0:
            await db.commit()
            print(f"  Created {created_count} transactions...")
    
    await db.commit()
    print(f"✓ {created_count} transactions seeded")


async def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    await init_db()
    
    async with AsyncSessionLocal() as db:
        await seed_users(db)
        await seed_rules(db)
        await seed_transactions(db, count=500)
    
    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())