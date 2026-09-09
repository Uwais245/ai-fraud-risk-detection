import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

# Train Anomaly Model
def tam():
    print("Loading processed data...")
    df = pd.read_csv("pdata.csv")
    
    # Drop the target label if your dataset has one (we want the model to learn unsupervised)
    if 'is_fraud' in df.columns:
        X = df.drop(columns=['is_fraud'])
    else:
        X = df

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