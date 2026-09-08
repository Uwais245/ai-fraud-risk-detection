from google import genai

API_KEY = "Api key"
client = genai.Client(api_key=API_KEY)

#Dummy Transaction Data
transaction = {
    "transaction_id": "TXN-9982",
    "amount": 6000,
    "usual_spending_max": 500,
    "is_new_device": True,
    "transactions_in_last_10_mins": 6
}

def check_fraud_rules(data):
    risk_reasons = []
    
    # Naya Rule: Agar current amount normal spending se zyada hai
    if data["amount"] > data["usual_spending_max"]:
        risk_reasons.append(f"Amount (${data['amount']}) exceeds the usual spending limit (${data['usual_spending_max']})")
        
    if data["amount"] > 5000:
        risk_reasons.append(f"High transaction amount: ${data['amount']}")
        
    # Optimized Python Syntax
    if data["is_new_device"]:
        risk_reasons.append("Login attempted from a new, unrecognized device")
        
    if data["transactions_in_last_10_mins"] > 5:
        risk_reasons.append("More than 5 transactions occurred within 10 minutes")
        
    return risk_reasons

def generate_ai_explanation(reasons):
    print("\n[Gemini AI is generating explanation, please wait...]\n")
    
    prompt = f"""
    You are a fraud analyst expert. 
    A transaction was flagged for these reasons: {reasons}. 
    Explain why this is high risk in 2 short bullet points for a business user.
    Do NOT use complex technical jargon.
    """
    
    # Naye package ka function
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text

triggered_reasons = check_fraud_rules(transaction)

print("--- Rules Triggered ---")
for reason in triggered_reasons:
    print("-", reason)

ai_result = generate_ai_explanation(triggered_reasons)
print("--- AI Explanation ---")
print(ai_result)