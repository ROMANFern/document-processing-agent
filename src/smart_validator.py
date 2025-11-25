import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from models import Invoice, ValidationResult
from validator import InvoiceValidator

load_dotenv()

class SmartValidator:
    """Enhanced validator that combines rule-based checks with AI analysis"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.rule_validator = InvoiceValidator()
    
    def validate(self, invoice: Invoice) -> ValidationResult:
        """Run both rule-based and AI-powered validation"""
        
        # First, run traditional rule-based validation
        rule_validation = self.rule_validator.validate(invoice)
        
        # Then, run AI analysis on the raw invoice text
        ai_validation = self._ai_analyze(invoice)
        
        # Combine results
        combined_issues = rule_validation.issues + ai_validation.issues
        combined_warnings = rule_validation.warnings + ai_validation.warnings
        
        # Remove duplicates while preserving order
        combined_issues = list(dict.fromkeys(combined_issues))
        combined_warnings = list(dict.fromkeys(combined_warnings))
        
        is_valid = len(combined_issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            issues=combined_issues,
            warnings=combined_warnings
        )
    
    def _ai_analyze(self, invoice: Invoice) -> ValidationResult:
        """Use AI to analyze invoice for suspicious patterns or explicit warnings"""
    
        # Get current date for context
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"""
    You are analyzing an invoice for a finance team. Today's date is {current_date}.

    Invoice Details:
    - Number: {invoice.invoice_number}
    - Vendor: {invoice.vendor_name}
    - Total: ${invoice.total_amount:,.2f}
    - Date: {invoice.invoice_date}

    Raw Invoice Text:
    {invoice.raw_text}

    ONLY flag issues that are EXPLICITLY concerning. Look for:

    CRITICAL ISSUES (flag as issues):
    1. Explicit warnings about duplicates, errors, or fraud mentioned in the invoice text
    2. Changed bank account details mentioned in notes
    3. Requests for unusual payment methods (gift cards, cryptocurrency, etc.)
    4. Invoices marked as "VOID", "CANCELLED", or "DUPLICATE" in the text

    WARNINGS (flag as warnings):
    1. Very high individual line items (over $15,000 for a single item)
    2. Missing critical vendor information (no ABN, no address)
    3. Unusual payment terms mentioned in notes

    DO NOT FLAG:
    - Round numbers (these are normal)
    - Standard payment terms (Net 30, Net 60)
    - High but reasonable amounts for business purchases
    - Normal business transactions

    Be conservative - only flag things that would genuinely concern an experienced accountant.

    Return a JSON object:
    {{
        "has_issues": true/false,
        "critical_issues": ["only serious problems that make invoice definitely invalid"],
        "warnings": ["only genuine concerns that need human review"]
    }}

    If the invoice looks normal, return empty arrays. Return ONLY the JSON object.
    """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an experienced financial auditor. You flag issues conservatively - only when there are genuine red flags, not for normal business transactions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            issues = analysis.get("critical_issues", [])
            warnings = analysis.get("warnings", [])
            
            return ValidationResult(
                is_valid=len(issues) == 0,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            # If AI analysis fails, return empty validation (don't block the process)
            print(f"⚠️  AI validation failed: {e}")
            return ValidationResult(is_valid=True, issues=[], warnings=[])
    
    def reset(self):
        """Reset validator state"""
        self.rule_validator.reset()