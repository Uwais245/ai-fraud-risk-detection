import joblib
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore') # Keeps the terminal output clean

# Load your saved models and scalers
encoders = joblib.load('saved_models/label_encoders.pkl')
scaler = joblib.load('saved_models/scaler.pkl')
model = joblib.load('saved_models/isolation_forest.pkl')

def get_ml_risk_score(transaction_data: dict) -> float:
    """Processes a single live transaction and returns the 0-100 ML Score."""
    
    # 1. Convert the incoming JSON into a DataFrame
    df = pd.DataFrame([transaction_data])
    
    # 2. Apply Label Encoders safely
    for col, le in encoders.items():
        if col in df.columns:
            # Fallback for brand new, unseen data (e.g., a new device type)
            known_classes = list(le.classes_)
            df[col] = df[col].apply(lambda x: x if str(x) in known_classes else known_classes[0])
            df[col] = le.transform(df[col].astype(str))
            
    # 3. Apply StandardScaler
    numerical_cols = ['account_age_days', 'total_transactions_user', 'avg_amount_user', 'amount', 'shipping_distance_km']
    existing_num_cols = [col for col in numerical_cols if col in df.columns]
    if existing_num_cols:
        df[existing_num_cols] = scaler.transform(df[existing_num_cols])
    
    # 4. Drop metadata columns
    cols_to_drop = ['is_fraud', 'transaction_id', 'user_id', 'transaction_time']
    X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
    
    # 5. Generate the raw anomaly score and normalize it to 0-100
    raw_score = model.decision_function(X)[0]
    inverted_score = raw_score * -1
    normalized_score = np.clip(((inverted_score + 0.5) / 1.0) * 100, 0, 100)
    
    return round(normalized_score, 2)

# --- Execute the Test ---
if __name__ == "__main__":
    # Simulating a suspicious transaction (Amount is drastically higher than average)
    test_transaction = {
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
    
    print("Simulating live transaction input...")
    score = get_ml_risk_score(test_transaction)
    print(f"--> Real-time ML Risk Score: {score}/100")