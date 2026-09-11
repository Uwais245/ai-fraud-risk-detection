from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.models.rule import Rule
from app.models.transaction import Transaction
from app.schemas.rules import RuleCondition, RuleOperator, RuleAction


class RulesEngineService:
    """Service for evaluating configurable business rules"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_active_rules(self) -> List[Rule]:
        """Get all active rules"""
        stmt = select(Rule).where(Rule.is_active == True).order_by(Rule.id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def evaluate_rules(self, transaction_data: Dict[str, Any]) -> tuple:
        """
        Evaluate all active rules against transaction data.
        Returns (total_risk_increase, triggered_flags)
        """
        rules = await self.get_active_rules()
        total_increase = 0
        flags = []
        
        for rule in rules:
            if self._evaluate_condition(rule.condition, transaction_data):
                total_increase += rule.risk_increase
                flags.append(f"Rule triggered: {rule.name}")
        
        return total_increase, flags
    
    def _evaluate_condition(self, condition: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate a single rule condition"""
        try:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if field not in data:
                return False
            
            field_value = data[field]
            
            # Convert to comparable types
            if isinstance(value, (int, float)) and isinstance(field_value, str):
                try:
                    field_value = float(field_value)
                except ValueError:
                    return False
            
            return self._apply_operator(field_value, operator, value)
        except Exception:
            return False
    
    def _apply_operator(self, field_value: Any, operator: str, target_value: Any) -> bool:
        """Apply comparison operator"""
        if operator == RuleOperator.EQ:
            return field_value == target_value
        elif operator == RuleOperator.NE:
            return field_value != target_value
        elif operator == RuleOperator.GT:
            return field_value > target_value
        elif operator == RuleOperator.GTE:
            return field_value >= target_value
        elif operator == RuleOperator.LT:
            return field_value < target_value
        elif operator == RuleOperator.LTE:
            return field_value <= target_value
        elif operator == RuleOperator.IN:
            return field_value in target_value if isinstance(target_value, list) else False
        elif operator == RuleOperator.NOT_IN:
            return field_value not in target_value if isinstance(target_value, list) else False
        elif operator == RuleOperator.CONTAINS:
            return target_value in str(field_value)
        return False
    
    async def create_rule(self, rule_data: Dict[str, Any], created_by: int) -> Rule:
        """Create a new rule"""
        rule = Rule(
            name=rule_data["name"],
            description=rule_data.get("description"),
            condition=rule_data["condition"],
            action=rule_data["action"],
            risk_increase=rule_data.get("risk_increase", 0),
            is_active=rule_data.get("is_active", True),
            created_by=created_by
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
    
    async def update_rule(self, rule_id: int, update_data: Dict[str, Any]) -> Optional[Rule]:
        """Update an existing rule"""
        stmt = select(Rule).where(Rule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        
        if not rule:
            return None
        
        for key, value in update_data.items():
            if hasattr(rule, key) and value is not None:
                setattr(rule, key, value)
        
        await self.db.commit()
        await self.db.refresh(rule)
        return rule
    
    async def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule"""
        stmt = select(Rule).where(Rule.id == rule_id)
        result = await self.db.execute(stmt)
        rule = result.scalar_one_or_none()
        
        if not rule:
            return False
        
        await self.db.delete(rule)
        await self.db.commit()
        return True