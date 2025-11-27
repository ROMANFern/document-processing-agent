from models import Invoice, ValidationResult
from typing import List, Set
import re

class InvoiceValidator:
    def __init__(self):
        self.processed_invoices: Set[str] = set()  # Track invoice numbers
        self.validation_rules = {
            "max_total": 50000.00,  # Flag invoices over $50k
            "max_line_item": 10000.00,  # Flag individual items over $10k
            "required_fields": ["invoice_number", "vendor_name", "total_amount"]
        }
    
    def validate(self, invoice: Invoice) -> ValidationResult:
        """Run all validation checks on an invoice"""
        issues = []
        warnings = []
        
        # Check 1: Required fields
        if not invoice.invoice_number:
            issues.append("Missing invoice number")
        if not invoice.vendor_name:
            issues.append("Missing vendor name")
        if not invoice.total_amount:
            issues.append("Missing total amount")
        
        # Check 2: Duplicate detection
        if invoice.invoice_number in self.processed_invoices:
            issues.append(f"DUPLICATE: Invoice {invoice.invoice_number} already processed")
        else:
            self.processed_invoices.add(invoice.invoice_number)
        
        # Check 3: Math validation
        calculated_subtotal = sum(item.amount for item in invoice.line_items)
        if abs(calculated_subtotal - invoice.subtotal) > 0.01:  # Allow 1 cent rounding
            issues.append(
                f"Subtotal mismatch: Line items sum to ${calculated_subtotal:.2f} "
                f"but subtotal is ${invoice.subtotal:.2f}"
            )
        
        # Check 4: Tax calculation (assuming 10% GST)
        expected_tax = invoice.subtotal * 0.10
        if abs(expected_tax - invoice.tax_amount) > 0.01:
            warnings.append(
                f"Tax amount ${invoice.tax_amount:.2f} doesn't match "
                f"expected 10% GST of ${expected_tax:.2f}"
            )
        
        # Check 5: Total calculation
        expected_total = invoice.subtotal + invoice.tax_amount
        if abs(expected_total - invoice.total_amount) > 0.01:
            issues.append(
                f"Total mismatch: ${invoice.subtotal:.2f} + ${invoice.tax_amount:.2f} "
                f"= ${expected_total:.2f}, but total shows ${invoice.total_amount:.2f}"
            )
        
        # Check 6: High value warnings
        if invoice.total_amount > self.validation_rules["max_total"]:
            warnings.append(
                f"HIGH VALUE: Total ${invoice.total_amount:,.2f} exceeds "
                f"${self.validation_rules['max_total']:,.2f} threshold"
            )
        
        # Check 7: Individual line item checks
        for item in invoice.line_items:
            if item.amount > self.validation_rules["max_line_item"]:
                warnings.append(
                    f"High value line item: '{item.description}' "
                    f"= ${item.amount:,.2f}"
                )
            
            # Check line item math
            expected_amount = item.quantity * item.unit_price
            if abs(expected_amount - item.amount) > 0.01:
                issues.append(
                    f"Line item math error: '{item.description}' "
                    f"- {item.quantity} x ${item.unit_price:.2f} "
                    f"= ${expected_amount:.2f}, but shows ${item.amount:.2f}"
                )
        
        # Check 8: ABN format (Australian Business Number)
        if invoice.vendor_abn:
            abn_clean = re.sub(r'[^\d]', '', invoice.vendor_abn)
            if len(abn_clean) != 11:
                warnings.append(f"ABN format may be invalid: {invoice.vendor_abn}")
        
        # Check 9: Date validation (basic)
        if not invoice.invoice_date or not invoice.due_date:
            warnings.append("Missing date information")
        
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings=warnings
        )
    
    def reset(self):
        """Reset processed invoices (for testing)"""
        self.processed_invoices.clear()