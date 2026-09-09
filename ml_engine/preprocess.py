import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

# Create a folder to save our trained model and scalers
os.makedirs("saved_models", exist_ok=True)

