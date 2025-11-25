import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_extraction():
    """Test basic invoice extraction with OpenAI"""
    
    # Read sample invoice
    with open("data/sample_invoice_1.txt", "r") as f:
        invoice_text = f.read()
    
    # Create prompt for extraction
    prompt = f"""
Extract the following information from this invoice and return it in a structured format:

Invoice:
{invoice_text}

Please extract:
1. Invoice Number
2. Invoice Date
3. Due Date
4. Vendor Name
5. Vendor ABN
6. Customer Name
7. Line Items (description, quantity, unit price, amount)
8. Subtotal
9. Tax Amount
10. Total Amount

Return the data in a clear, structured format.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model for testing
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured data from invoices."},
                {"role": "user", "content": prompt}
            ],
            temperature=0  # Deterministic output
        )
        
        print("✅ API Connection Successful!")
        print("\n" + "="*60)
        print("EXTRACTED DATA:")
        print("="*60)
        print(response.choices[0].message.content)
        print("\n" + "="*60)
        print(f"Tokens used: {response.usage.total_tokens}")
        print(f"Estimated cost: ${response.usage.total_tokens * 0.00015:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your .env file has: OPENAI_API_KEY=your-key-here")

if __name__ == "__main__":
    test_extraction()