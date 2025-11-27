from extractor import InvoiceExtractor
import json

def test_extraction():
    extractor = InvoiceExtractor()
    
    print("Testing Invoice Extraction...")
    print("="*60)
    
    # Test both invoices
    for i in [1, 2]:
        print(f"\nProcessing sample_invoice_{i}.txt")
        print("-"*60)
        
        try:
            invoice = extractor.extract_from_file(f"data/sample_invoice_{i}.txt")
            
            print(f"Successfully extracted!")
            print(f"\nInvoice: {invoice.invoice_number}")
            print(f"Vendor: {invoice.vendor_name}")
            print(f"Total: ${invoice.total_amount:,.2f}")
            print(f"Line Items: {len(invoice.line_items)}")
            
            # Save to JSON for inspection
            output_file = f"output/extracted_invoice_{i}.json"
            with open(output_file, 'w') as f:
                json.dump(invoice.to_dict(), f, indent=2)
            print(f"Saved to: {output_file}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-"*60)

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    import os
    os.makedirs("output", exist_ok=True)
    
    test_extraction()