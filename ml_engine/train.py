import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# Train Anomaly Model
def tam():
    print("Loading processed data...")
    df = pd.read_csv("pdata.csv")
    
    # Storing target label AND metadata columns that are not ML features in a list to be dropped
    cols_to_drop = ['is_fraud', 'transaction_id', 'user_id', 'transaction_time']
    
    # Only drop the columns that actually exist in the dataframe
    X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    print("Training Isolation Forest...")
    # contamination = estimated percentage of fraud in the dataset (e.g., 5%)
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X)

    # Save the trained model for the FastAPI backend
    joblib.dump(model, 'saved_models/isolation_forest.pkl')
    print("Model saved to saved_models/isolation_forest.pkl")

    # --- TESTING THE ML SCORE ---
    # The model outputs a score where lower/negative numbers are anomalies
    raw_scores = model.decision_function(X)
    
    # Let's map this raw score to a 0-100 Risk Score architecture
    # Invert the scores so high anomaly = high risk
    inverted_scores = raw_scores * -1 
    
    # Normalize to 0-100 scale
    min_score = inverted_scores.min()
    max_score = inverted_scores.max()
    
    risk_scores = ((inverted_scores - min_score) / (max_score - min_score)) * 100
    
    df['ml_risk_score'] = np.round(risk_scores, 2)
    
    print("\nSample Output (0-100 ML Risk Scores):")
    print(df[['ml_risk_score']].head(10))

if __name__ == "__main__":
    tam()