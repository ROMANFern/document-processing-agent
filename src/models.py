from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class LineItem:
    description: str
    quantity: float
    unit_price: float
    amount: float

@dataclass
class Invoice:
    invoice_number: str
    invoice_date: str
    due_date: str
    vendor_name: str
    vendor_abn: Optional[str]
    customer_name: str
    line_items: List[LineItem]
    subtotal: float
    tax_amount: float
    total_amount: float
    raw_text: str
    
    def to_dict(self):
        return {
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "vendor_name": self.vendor_name,
            "vendor_abn": self.vendor_abn,
            "customer_name": self.customer_name,
            "line_items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "amount": item.amount
                }
                for item in self.line_items
            ],
            "subtotal": self.subtotal,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount
        }

@dataclass
class ValidationResult:
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    
    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "warnings": self.warnings
        }