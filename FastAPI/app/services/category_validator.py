"""
Category validator for loan document classification
"""
from typing import List

# 32 predefined loan categories
VALID_CATEGORIES: List[str] = [
    "Lender",
    "Loan Number",
    "Closing Date",
    "Disbursement Date",
    "Borrower(s)",
    "Co-Borrower(s)",
    "First Payment Date",
    "Maturity Date",
    "Property Address",
    "Loan Amount",
    "Loan Type",
    "Interest Rate",
    "Loan Purpose",
    "Loan Term",
    "Amortization Type",
    "Amortization Term",
    "ARM Info",
    "First P&I Amount",
    "Desc",
    "Sales Price",
    "Caps",
    "Appraised Value",
    "Index",
    "Occupancy",
    "Margin",
    "Note",
    "Deed",
    "Appraisal",
    "Title",
    "Insurance",
    "Inspection",
    "Unclassified"
]


def validate_category(category: str) -> bool:
    """
    Validate if category is in the predefined list
    
    Args:
        category: Category name to validate
        
    Returns:
        True if category is valid, False otherwise
    """
    return category in VALID_CATEGORIES


def get_valid_categories() -> List[str]:
    """
    Get list of all valid categories
    
    Returns:
        List of valid category names
    """
    return VALID_CATEGORIES.copy()
