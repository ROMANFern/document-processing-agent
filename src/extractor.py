import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from models import Invoice, LineItem

load_dotenv()

class InvoiceExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def extract_from_text(self, invoice_text: str) -> Invoice:
        """Extract structured data from invoice text using GPT-4"""
        
        prompt = f"""
Extract ALL information from this invoice and return it as a JSON object with this EXACT structure:

{{
    "invoice_number": "string",
    "invoice_date": "string",
    "due_date": "string",
    "vendor_name": "string",
    "vendor_abn": "string or null",
    "customer_name": "string",
    "line_items": [
        {{
            "description": "string",
            "quantity": number,
            "unit_price": number,
            "amount": number
        }}
    ],
    "subtotal": number,
    "tax_amount": number,
    "total_amount": number
}}

Invoice text:
{invoice_text}

Return ONLY the JSON object, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured data from invoices. Always return valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Parse JSON response
            extracted_data = json.loads(response.choices[0].message.content)
            
            # Convert to Invoice object
            line_items = [
                LineItem(
                    description=item["description"],
                    quantity=float(item["quantity"]),
                    unit_price=float(item["unit_price"]),
                    amount=float(item["amount"])
                )
                for item in extracted_data["line_items"]
            ]
            
            invoice = Invoice(
                invoice_number=extracted_data["invoice_number"],
                invoice_date=extracted_data["invoice_date"],
                due_date=extracted_data["due_date"],
                vendor_name=extracted_data["vendor_name"],
                vendor_abn=extracted_data.get("vendor_abn"),
                customer_name=extracted_data["customer_name"],
                line_items=line_items,
                subtotal=float(extracted_data["subtotal"]),
                tax_amount=float(extracted_data["tax_amount"]),
                total_amount=float(extracted_data["total_amount"]),
                raw_text=invoice_text
            )
            
            return invoice
            
        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")
    
    def extract_from_file(self, file_path: str) -> Invoice:
        """Extract from a text file"""
        with open(file_path, 'r') as f:
            invoice_text = f.read()
        return self.extract_from_text(invoice_text)