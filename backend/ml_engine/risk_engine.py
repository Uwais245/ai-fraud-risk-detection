from predict import get_ml_risk_score, is_model_available

def evaluate_business_rules(transaction: dict) -> tuple[int, list]:
    """Applies hard business rules and returns a rule score (0-100) and triggered alerts."""
    rule_score = 0
    flags = []

    # Rule 1: Unusually high amount
    if transaction.get('amount', 0) > 1000:
        rule_score += 40
        flags.append("High transaction amount (>$1000)")

    # Rule 2: New account making large purchase
    if transaction.get('account_age_days', 999) < 14 and transaction.get('amount', 0) > 500:
        rule_score += 30
        flags.append("New account high-value transaction")

    # Rule 3: CVV or AVS mismatch
    if transaction.get('cvv_result') == 0 or transaction.get('avs_match') == 0:
        rule_score += 50
        flags.append("CVV or Address Verification failure")

    # Cap rule score at 100
    rule_score = min(rule_score, 100)
    return rule_score, flags


def generate_final_decision(transaction: dict) -> dict:
    """Combines ML and Rules to generate the final risk payload for the backend."""
    
    # 1. Get the ML Anomaly Score (if model available)
    ml_score = 0.0
    if is_model_available():
        try:
            ml_score = get_ml_risk_score(transaction)
        except Exception:
            ml_score = 0.0
    
    # 2. Get the Business Rules Score
    rule_score, flags = evaluate_business_rules(transaction)
    
    # 3. Calculate Final Weighted Score (e.g., 60% ML, 40% Rules)
    # If ML not available, use 100% rules
    if is_model_available():
        final_score = (ml_score * 0.6) + (rule_score * 0.4)
    else:
        final_score = float(rule_score)
    final_score = round(final_score, 2)
    
    # 4. Determine Risk Category
    if final_score >= 71:
        risk_level = "HIGH"
        decision = "REVIEW"
    elif final_score >= 31:
        risk_level = "MEDIUM"
        decision = "APPROVE"
    else:
        risk_level = "LOW"
        decision = "APPROVE"
        
    # 5. Return the exact JSON structure the backend and AI Prompt dev need
    return {
        "transaction_id": transaction.get("transaction_id", "UNKNOWN"),
        "ml_anomaly_score": ml_score,
        "rule_engine_score": rule_score,
        "final_risk_score": final_score,
        "risk_level": risk_level,
        "decision": decision,
        "risk_flags": flags
    }


# --- Test the Full Engine ---
if __name__ == "__main__":
    test_transaction = {
        "transaction_id": "TXN-998877",
        "account_age_days": 12,
        "total_transactions_user": 3,
        "avg_amount_user": 45.50,
        "amount": 1200.00, 
        "country": "US",
        "bin_country": "US",
        "channel": "web",
        "merchant_category": "electronics",
        "promo_used": 0,
        "avs_match": 1,
        "cvv_result": 1,
        "three_ds_flag": 0,
        "shipping_distance_km": 500
    }
    
    print("Running Full Risk Analysis...")
    result = generate_final_decision(test_transaction)
    
    import json
    print(json.dumps(result, indent=4))