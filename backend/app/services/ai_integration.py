import os
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Google GenAI
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai not installed. AI explanations will not be available.")


class AIIntegrationService:
    """Service to generate AI explanations using Google Gemini API"""
    
    def __init__(self):
        self.client = None
        if GENAI_AVAILABLE and settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Gemini AI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
    
    def generate_explanation(self, risk_flags: List[str], transaction_context: Optional[dict] = None) -> Optional[str]:
        """
        Generate a human-readable explanation for why a transaction was flagged.
        
        Args:
            risk_flags: List of risk flags triggered
            transaction_context: Additional context about the transaction
            
        Returns:
            AI-generated explanation or None if unavailable
        """
        if not self.client or not risk_flags:
            return None
        
        try:
            prompt = self._build_prompt(risk_flags, transaction_context)
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            return response.text.strip() if response.text else None
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_explanation(risk_flags)
    
    def _build_prompt(self, risk_flags: List[str], transaction_context: Optional[dict] = None) -> str:
        """Build the prompt for Gemini"""
        flags_text = "\n".join([f"• {flag}" for flag in risk_flags])
        
        context_text = ""
        if transaction_context:
            ctx_parts = []
            if transaction_context.get("amount"):
                ctx_parts.append(f"Transaction amount: ${transaction_context['amount']}")
            if transaction_context.get("customer_id"):
                ctx_parts.append(f"Customer: {transaction_context['customer_id']}")
            if transaction_context.get("account_age_days") is not None:
                ctx_parts.append(f"Account age: {transaction_context['account_age_days']} days")
            context_text = "\n".join(ctx_parts)
        
        return f"""You are a fraud analyst expert. 
A transaction was flagged for these reasons:
{flags_text}

{f"Transaction context:\n{context_text}" if context_text else ""}

Explain why this is high risk in 2-3 short bullet points for a business user.
Do NOT use complex technical jargon. Keep it simple and actionable.
Focus on what the business user needs to know to make a decision."""
    
    def _fallback_explanation(self, risk_flags: List[str]) -> str:
        """Generate a basic explanation without AI"""
        if not risk_flags:
            return "No specific risk factors identified."
        
        explanations = []
        for flag in risk_flags[:3]:  # Limit to top 3
            if "amount" in flag.lower():
                explanations.append("The transaction amount is unusually high compared to normal spending patterns.")
            elif "new account" in flag.lower() or "account age" in flag.lower():
                explanations.append("The account is relatively new, which increases risk for high-value transactions.")
            elif "cvv" in flag.lower() or "avs" in flag.lower():
                explanations.append("Payment verification failed (CVV or address mismatch).")
            elif "velocity" in flag.lower():
                explanations.append("Multiple transactions occurred in a short time period.")
            elif "cross-border" in flag.lower():
                explanations.append("Transaction originates from a different country than the card issuer.")
            elif "device" in flag.lower():
                explanations.append("Transaction from a new or unrecognized device.")
            elif "location" in flag.lower():
                explanations.append("Transaction from an unusual or high-risk location.")
            else:
                explanations.append(f"Risk factor detected: {flag}")
        
        return "\n".join([f"• {exp}" for exp in explanations])
    
    def generate_investigation_summary(self, investigation_data: dict) -> Optional[str]:
        """Generate a summary for an investigation case"""
        if not self.client:
            return None
        
        try:
            prompt = f"""You are a fraud investigation assistant.
Summarize this investigation case for a fraud analyst:

Customer: {investigation_data.get('customer_id', 'Unknown')}
Risk Score: {investigation_data.get('risk_score', 'N/A')}
Risk Level: {investigation_data.get('risk_level', 'N/A')}
Risk Flags: {', '.join(investigation_data.get('risk_flags', []))}
AI Explanation: {investigation_data.get('ai_explanation', 'N/A')}
Related Alerts: {investigation_data.get('alert_count', 0)}
Transaction Count: {investigation_data.get('transaction_count', 0)}

Provide a concise 3-4 sentence summary highlighting the key findings and recommended next steps."""
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            return response.text.strip() if response.text else None
            
        except Exception as e:
            logger.error(f"Gemini API error for investigation summary: {e}")
            return None
    
    def answer_investigation_question(self, question: str, context: dict) -> Optional[str]:
        """Answer a specific question from an analyst during investigation"""
        if not self.client:
            return None
        
        try:
            prompt = f"""You are a fraud investigation assistant with access to transaction data.
Answer the analyst's question based on the provided context.

Context:
- Customer: {context.get('customer_id', 'Unknown')}
- Risk Profile: {context.get('risk_profile', {})}
- Recent Transactions: {context.get('recent_transactions', [])}
- Devices: {context.get('devices', [])}
- IPs: {context.get('ips', [])}
- Alerts: {context.get('alerts', [])}

Question: {question}

Provide a clear, concise answer based only on the provided context. If the information is not available, say so."""
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            return response.text.strip() if response.text else None
            
        except Exception as e:
            logger.error(f"Gemini API error for investigation question: {e}")
            return None


# Singleton instance
ai_service = AIIntegrationService()