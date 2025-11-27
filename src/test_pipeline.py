from extractor import InvoiceExtractor
from smart_validator import SmartValidator
import json

def test_full_pipeline():
    extractor = InvoiceExtractor()
    validator = SmartValidator()
    
    print("Testing Complete Document Processing Pipeline")
    print("="*70)
    
    invoices = ["sample_invoice_1.txt", "sample_invoice_2.txt", "sample_invoice_3.txt"]
    
    for invoice_file in invoices:
        print(f"\nProcessing: {invoice_file}")
        print("-"*70)
        
        try:
            # Step 1: Extract
            print("Extracting data...")
            invoice = extractor.extract_from_file(f"data/{invoice_file}")
            print(f"Extracted {len(invoice.line_items)} line items")
            
            # Step 2: Validate
            print("Running validation checks...")
            print("Running AI analysis...")
            validation = validator.validate(invoice)
            
            # Step 3: Report
            print(f"\nRESULTS:")
            print(f"   Invoice: {invoice.invoice_number}")
            print(f"   Vendor: {invoice.vendor_name}")
            print(f"   Total: ${invoice.total_amount:,.2f}")
            print(f"   Status: {'VALID' if validation.is_valid else 'INVALID'}")
            
            if validation.issues:
                print(f"\nISSUES ({len(validation.issues)}):")
                for issue in validation.issues:
                    print(f"   • {issue}")
            
            if validation.warnings:
                print(f"\nWARNINGS ({len(validation.warnings)}):")
                for warning in validation.warnings:
                    print(f"   • {warning}")
            
            if not validation.issues and not validation.warnings:
                print(f"\nNo issues or warnings detected")
            
            # Save results
            result = {
                "invoice": invoice.to_dict(),
                "validation": validation.to_dict()
            }
            
            output_file = f"output/processed_{invoice_file.replace('.txt', '.json')}"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nSaved results to: {output_file}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-"*70)
    
    print("\nPipeline test complete!")

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    test_full_pipeline()