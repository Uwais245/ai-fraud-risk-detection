# ai-fraud-risk-detection
An AI-powered Fraud &amp; Risk Detection Platform that analyzes business transactions, calculates real-time risk scores using Machine Learning, and provides LLM-based explainable AI insights.

# AI Fraud & Risk Detection Platform 🛡️

## Overview
This repository contains the **AI Prompts & Rules Logic** module for the AI-powered Fraud & Risk Detection Platform. The core script (`ai_logic.py`) acts as a transactional rules engine that evaluates dummy transaction data and leverages the **Google Gemini API** to generate clear, concise, and business-friendly explanations for flagged risks.

## Key Features 🚀
* **Rules Engine:** Uses Python-based conditional logic to flag suspicious activities (e.g., unusual spending amounts, new device logins, high transaction frequency).
* **Generative AI Integration:** Powered by the official `google-genai` SDK using the `gemini-3.6-flash` model.
* **Human-Readable Outputs:** Converts technical trigger points into 2-3 simple bullet points for non-technical business users and fraud analysts.

## Prerequisites 📋
Before running the code, ensure you have the following installed:
* Python 3.8+
* A valid Google Gemini API Key

## Installation & Setup ⚙️

1. **Clone the repository (or download the script):**
   ```bash
   git clone [https://github.com/your-repo-link.git](https://github.com/your-repo-link.git)
   cd your-repo-folder
