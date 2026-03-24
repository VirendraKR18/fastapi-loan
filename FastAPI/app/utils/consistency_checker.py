"""
Consistency checker utility for loan documents
"""
from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


def check_consistency(
    extracted_data: Dict[str, Any],
    pdf_text: str = None
) -> Dict[str, Any]:
    """
    Check consistency of key fields across document
    
    Args:
        extracted_data: Dictionary containing extracted key details
        pdf_text: Full PDF text for additional validation (optional)
        
    Returns:
        Dictionary with status and list of inconsistencies
    """
    inconsistencies = []
    
    # Extract key details
    key_details = extracted_data.get('key_details', {})
    
    # Check for missing critical fields
    critical_fields = ['Name', 'Borrower', 'Address']
    for field in critical_fields:
        if not key_details.get(field):
            inconsistencies.append(f"Missing critical field: {field}")
    
    # Check borrower name consistency
    name = key_details.get('Name', '').strip()
    borrower = key_details.get('Borrower', '').strip()
    
    if name and borrower and name.lower() != borrower.lower():
        inconsistencies.append(
            f"Name mismatch: Name field ('{name}') differs from Borrower field ('{borrower}')"
        )
    
    # Check for additional borrower vs co-borrower consistency
    additional_borrower = key_details.get('Additional Borrower', '').strip()
    co_borrower = key_details.get('Co-Borrower', '').strip()
    
    if additional_borrower and co_borrower and additional_borrower.lower() != co_borrower.lower():
        inconsistencies.append(
            f"Co-Borrower mismatch: Additional Borrower ('{additional_borrower}') differs from Co-Borrower ('{co_borrower}')"
        )
    
    # Validate interest rate format
    interest_rate = key_details.get('Interest Rate', '')
    if interest_rate:
        # Check if interest rate is in valid format (e.g., "3.5%", "4.25%")
        if not re.match(r'^\d+(\.\d+)?%?$', interest_rate.strip()):
            inconsistencies.append(
                f"Invalid interest rate format: '{interest_rate}'"
            )
    
    # Validate closing date format
    closing_date = key_details.get('Closing Date', '')
    if closing_date:
        # Check if date is in reasonable format
        if not re.match(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', closing_date.strip()):
            logger.warning(f"Unusual closing date format: '{closing_date}'")
    
    # Determine overall status
    status = "Pass" if len(inconsistencies) == 0 else "Fail"
    
    return {
        "status": status,
        "inconsistencies": inconsistencies
    }


def validate_required_documents(bookmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate presence of required documents based on bookmarks
    
    Args:
        bookmarks: List of bookmark dictionaries
        
    Returns:
        Dictionary with required_documents_present flag and missing_documents list
    """
    required_docs = ['Note', 'Deed', 'Appraisal']
    found_docs = set()
    
    # Check bookmarks for required document types
    for bookmark in bookmarks:
        doc_type = bookmark.get('type', '').strip()
        if doc_type in required_docs:
            found_docs.add(doc_type)
    
    missing_docs = [doc for doc in required_docs if doc not in found_docs]
    
    return {
        "required_documents_present": len(missing_docs) == 0,
        "missing_documents": missing_docs
    }
