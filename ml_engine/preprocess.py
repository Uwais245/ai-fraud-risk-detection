import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

# Creating a folder to save our trained model and scalers
os.makedirs("saved_models", exist_ok=True)

def prepare_data(pathcsv):
    print("Loading dataset...")
    df = pd.read_csv(pathcsv)

    categoricalcols = ['country', 'bin_country', 'channel', 'merchant_category', 'promo_used', 'avs_match', 'cvv_result', 'three_ds_flag']
    numericalcols = ['account_age_days', 'total_transactions_user', 'avg_amount_user', 'amount', 'shipping_distance_km']
    
    # Zero filling for missed values (NaN) in the dataset
    df.fillna(0, inplace=True)

    # Encode Categorical Data (Text to Numbers)
    labelencoders = {}
    for col in categoricalcols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            labelencoders[col] = le
    
    # Saving the encoders so the backend API can use them for real-time data
    joblib.dump(labelencoders, 'saved_models/label_encoders.pkl')

    # Scaling Numerical Data(Prevents a $5,000 transaction from completely overpowering the other data)
    scaler = StandardScaler()
    if all(col in df.columns for col in numericalcols):
        df[numericalcols] = scaler.fit_transform(df[numericalcols])
        joblib.dump(scaler, 'saved_models/scaler.pkl')

    # Save the processed data for training
    df.to_csv("processed_data.csv", index=False)
    print("Preprocessing complete! Saved to processed_data.csv")
    return df

if __name__ == "__main__":
    prepare_data("transactions.csv")