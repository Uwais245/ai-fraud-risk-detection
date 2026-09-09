# ML Anomaly Detection & Risk Engine 🚀

An AI-powered risk assessment module designed for e-commerce transaction monitoring.  
This module uses **Isolation Forest (Unsupervised Machine Learning)** to detect abnormal transaction patterns and combines ML predictions with predefined business rules to generate a unified **0-100 Risk Score**.

The engine is designed for seamless integration with a **FastAPI backend** and provides structured risk analysis output that can be consumed by an **LLM Assistant** to explain risk decisions in natural language.

---

## 📌 Project Overview

### Module Name
**ML Anomaly Detection & Risk Engine**

### Purpose

This module:

- Ingests e-commerce transaction data.
- Performs data preprocessing and feature transformation.
- Detects suspicious transaction behavior using an Isolation Forest model.
- Calculates an AI-based anomaly score.
- Applies business risk rules.
- Generates a final risk score between **0-100**.
- Provides structured output for backend APIs and AI assistants.

---

# 🏗️ Architecture Overview


```ml_engine/
│
├── preprocess.py
│ └── Data cleaning, encoding & feature scaling
│
├── train.py
│ └── Trains Isolation Forest model
│
├── predict.py
│ └── Performs real-time transaction scoring
│
├── risk_engine.py
│ └── Combines ML score + business rules
│
├── init.py
│ └── Makes module accessible for backend integration
│
├── saved_models/
│ ├── isolation_forest.pkl
│ ├── label_encoders.pkl
│ └── scaler.pkl
│
└── README.md
```

---

# 🧠 Machine Learning Approach

## Algorithm Used

### Isolation Forest

Isolation Forest is an unsupervised anomaly detection algorithm that identifies unusual transactions by isolating observations that differ significantly from normal behavior.

### Workflow


Transaction Data
|
↓
Data Preprocessing
|
↓
Feature Encoding & Scaling
|
↓
Isolation Forest Model
|
↓
AI Anomaly Score
|
↓
Business Rule Evaluation
|
↓
Final Risk Score (0-100)


---

# 🛠️ Technology Stack

## Programming Language

- Python 3.10+

## Core Libraries

| Library | Purpose |
|---------|---------|
| pandas | Data processing |
| numpy | Numerical computation |
| scikit-learn | Machine Learning model |
| joblib | Model serialization |

## ML Algorithm

- Isolation Forest (Unsupervised Learning)

---

# 📂 File Description

## `preprocess.py`

Responsible for preparing transaction data.

Functions:

- Cleans raw transaction datasets.
- Handles categorical variables.
- Applies Label Encoding.
- Performs numerical feature scaling.
- Generates processed training data.

---

## `train.py`

Responsible for model training.

Functions:

- Loads processed transaction data.
- Trains Isolation Forest model.
- Saves trained artifacts.

Generated files:

saved_models/
```
    ├── isolation_forest.pkl
    ├── label_encoders.pkl
    └── scaler.pkl
```


---

## `predict.py`

Handles real-time ML prediction.

Input:

```python
transaction = {
    "amount": 1500,
    "account_age": 20,
    "location": "Unknown"
}
```

Output:
```
AI anomaly score
Prediction result
Risk probability
risk_engine.py
```
The main decision engine.

It combines:
```
Machine Learning anomaly detection
Business risk rules

Example business rules:

High transaction amount
Suspicious location
New account activity
Multiple failed attempts
```
Final output:
```
Risk Score: 0-100
Risk Level
Risk Flags

Decision Explanation
```
⚙️ Installation & Setup
1. Clone Repository
git clone <repository-url>
cd ml_engine

2. Create Virtual Environment
```
python -m venv venv
```
3. Activate Environment

***(i). Windows***
```
.\venv\Scripts\activate
```
***(ii). Linux / macOS***
```
source venv/bin/activate
```
4. Install Dependencies

```
pip install pandas numpy scikit-learn joblib
```

📊 Dataset & Model Files
```
Important Note

The following files are intentionally excluded from this repository using .gitignore:

transactions.csv

saved_models/
    ├── isolation_forest.pkl
    ├── label_encoders.pkl
    └── scaler.pkl
```

****Reason****
```
These files are excluded to:

Keep repository lightweight.
Avoid committing generated ML artifacts.
Allow developers to train models using their own datasets.
```
🔄 Retraining Instructions

If model artifacts need to be regenerated:

Step 1
```
Place your dataset inside:

ml_engine/

└── transactions.csv
```
Step 2
```
Run preprocessing:

python preprocess.py
```
Step 3
```
Train the model:

python train.py
```

**After successful training:**
```
saved_models/

├── isolation_forest.pkl
├── label_encoders.pkl
└── scaler.pkl

will be generated automatically.
```

🔌 ****Backend API Integration****

The module is designed to integrate with a FastAPI backend.

Import Function

Backend should import:
```
from ml_engine.risk_engine import generate_final_decision
```
Input Format

The function accepts a standard Python dictionary representing a single transaction.

Example:
```
transaction = {
    "amount": 2500,
    "account_age": 15,
    "location": "International",
    "transaction_type": "purchase"
}
```
Output Format

Returns a structured dictionary/JSON response:

Example:
```
{
    "risk_score": 85,
    "risk_level": "High",
    "risk_flags": [
        "High transaction amount (>$1000)",
        "Unusual transaction pattern detected"
    ],
    "decision": "Transaction requires review"
}
```

****🤖 LLM Assistant Integration****

The generated output is optimized for AI assistants.

The risk_flags array allows the LLM to explain decisions to users in simple language.

Example:
```
Input:

{
 "risk_flags": [
    "High transaction amount (>$1000)"
 ]
}
```
**LLM Explanation:**

"This transaction was flagged because the amount is significantly higher than the user's normal spending pattern."

🔐 Security Considerations
Never commit sensitive transaction data.
Keep trained model artifacts protected.
Validate API input before scoring.
Monitor model performance regularly.
🚀 Future Improvements

Possible enhancements:

Real-time model retraining pipeline.
Deep Learning anomaly detection.
User behavior profiling.
Explainable AI (SHAP/LIME).
Automated fraud investigation workflow.
👨‍💻 Developer Notes

This module is built as an independent ML component that can be plugged into backend services without modifying the core API logic.

The architecture separates:

Data processing
Model training
Prediction
Risk decision logic

making the system scalable and maintainable.