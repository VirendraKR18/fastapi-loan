"""
Comprehensive entity extraction utilities for 150+ loan document fields
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def normalize_field_name(field_name: str) -> str:
    """
    Normalize field names to match expected format
    Handles variations in field naming from LLM responses
    """
    # Remove extra spaces and convert to title case
    normalized = field_name.strip()
    return normalized


def flatten_entities(entities: Dict[str, Any]) -> Dict[str, str]:
    """
    Flatten nested entity structure into a single-level dictionary
    
    Args:
        entities: Nested dictionary of entities by category
        
    Returns:
        Flattened dictionary with all field names and values
    """
    flattened = {}
    
    for category, fields in entities.items():
        if isinstance(fields, dict):
            for field_name, field_value in fields.items():
                # Normalize the field name
                normalized_name = normalize_field_name(field_name)
                flattened[normalized_name] = field_value
        else:
            logger.warning(f"Category '{category}' does not contain a dictionary of fields")
    
    return flattened


def get_extraction_statistics(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate statistics about the extraction results
    
    Args:
        entities: Nested dictionary of entities by category
        
    Returns:
        Dictionary containing extraction statistics
    """
    stats = {
        "total_categories": 0,
        "total_fields_extracted": 0,
        "categories_with_data": [],
        "empty_categories": [],
        "field_count_by_category": {}
    }
    
    for category, fields in entities.items():
        stats["total_categories"] += 1
        
        if isinstance(fields, dict):
            field_count = len(fields)
            stats["field_count_by_category"][category] = field_count
            stats["total_fields_extracted"] += field_count
            
            if field_count > 0:
                stats["categories_with_data"].append(category)
            else:
                stats["empty_categories"].append(category)
    
    return stats


def validate_required_fields(entities: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate that required fields are present in the extraction
    
    Args:
        entities: Nested dictionary of entities by category
        required_fields: List of field names that must be present
        
    Returns:
        Dictionary with validation results
    """
    flattened = flatten_entities(entities)
    
    validation_result = {
        "is_valid": True,
        "missing_fields": [],
        "present_fields": [],
        "total_required": len(required_fields),
        "total_present": 0
    }
    
    for field in required_fields:
        if field in flattened and flattened[field]:
            validation_result["present_fields"].append(field)
            validation_result["total_present"] += 1
        else:
            validation_result["missing_fields"].append(field)
            validation_result["is_valid"] = False
    
    return validation_result


def format_extraction_response(entities: Dict[str, Any], items: List[Any] = None) -> Dict[str, Any]:
    """
    Format the extraction response with comprehensive data and metadata
    
    Args:
        entities: Nested dictionary of entities by category
        items: Optional list of extracted items
        
    Returns:
        Formatted response dictionary
    """
    stats = get_extraction_statistics(entities)
    flattened = flatten_entities(entities)
    
    response = {
        "entities_by_category": entities,
        "entities_flattened": flattened,
        "extraction_statistics": stats,
        "items": items or [],
        "total_fields_extracted": stats["total_fields_extracted"]
    }
    
    return response


# Define the comprehensive list of 150+ fields for validation
COMPREHENSIVE_FIELD_LIST = [
    # Servicing Information
    "Servicing Fee - Percentage",
    "Servicing Fee - Flat Dollar",
    "Servicing Advance Methodology",
    
    # Loan Identifiers
    "Originator",
    "Loan Group",
    "Loan Number",
    "Doc Type",
    "Sched Bal",
    "Primary Borrower ID",
    
    # Loan Details
    "Amortization Type",
    "Lien Position",
    "HELOC Indicator",
    "Loan Purpose",
    "Cash Out Amount",
    "Total Origination and Discount Points",
    "Covered/High Cost Loan Indicator",
    "Relocation Loan Indicator",
    "Broker Indicator",
    "Channel",
    "Escrow Indicator",
    "Loan Type of Most Senior Lien",
    "Hybrid Period of Most Senior Lien",
    "Neg Am Limit of Most Senior Lien",
    "Option ARM Indicator",
    "Options at Recast",
    "Chattel Indicator",
    
    # Senior & Junior Loans
    "Senior Loan Amount",
    "Junior Mortgage Balance",
    "Origination Date of Most Senior Lien",
    
    # Loan Terms
    "Origination Date",
    "Original Loan Amount",
    "Original Interest Rate",
    "Original Amortization Term",
    "Original Term to Maturity",
    "First Payment Date of Loan",
    "Interest Type Indicator",
    "Original Interest Only Term",
    "Buy Down Period",
    "HELOC Draw Period",
    
    # Current Loan Status
    "Current Loan Amount",
    "Current Interest Rate",
    "WAC",
    "Current Payment Amount Due",
    "Interest Paid Through Date",
    "Current Payment Status",
    "Current 'Other' Monthly Payment",
    
    # ARM Details
    "Index Type",
    "ARM Look-Back Days",
    "Gross Margin",
    "ARM Round Flag",
    "ARM Round Factor",
    "Initial Fixed Rate Period",
    "Initial Interest Rate Cap (Change Up)",
    "Initial Interest Rate Cap (Change Down)",
    "Subsequent Interest Rate Reset Period",
    "Subsequent Interest Rate (Change Down)",
    "Subsequent Interest Rate Cap (Change Up)",
    "Lifetime Maximum Rate",
    "Lifetime Minimum Rate",
    
    # Negative Amortization
    "Negative Amortization Limit",
    "Initial Negative Amortization Recast Period",
    "Subsequent Negative Amortization Recast Period",
    
    # Payment Details
    "Initial Fixed Payment Period",
    "Subsequent Payment Reset Period",
    "Initial Periodic Payment Cap",
    "Subsequent Periodic Payment Cap",
    "Initial Minimum Payment Reset Period",
    "Subsequent Minimum Payment Reset Period",
    "Initial Minimum Payment",
    "Current Minimum Payment",
    
    # Prepayment Penalty
    "Prepayment Penalty Calculation",
    "Prepayment Penalty Type",
    "Prepayment Penalty Total Term",
    "Prepayment Penalty Hard Term",
    
    # Borrower Information
    "Number of Mortgaged Properties",
    "Total Number of Borrowers",
    "Self-employment Flag",
    "Years in Home",
    "Borrower 1 Employment Status",
    "Borrower 2 Employment Status",
    "Borrower 3 Employment Status",
    "Borrower 4 Employment Status",
    
    # Employment
    "Length of Employment: Borrower",
    "Length of Employment: Co-borrower",
    "Borrower Employment Verification",
    "Co-borrower Employment Verification",
    
    # FICO Scores
    "FICO Model Used",
    "Most Recent FICO Date",
    "Primary Wage Earner Original FICO: Equifax",
    "Primary Wage Earner Original FICO: Experian",
    "Primary Wage Earner Original FICO: TransUnion",
    "Secondary Wage Earner Original FICO: Equifax",
    "Secondary Wage Earner Original FICO: Experian",
    "Secondary Wage Earner Original FICO: Transunion",
    "Most Recent Primary Borrower FICO",
    "Most Recent Co-Borrower FICO",
    "FICO",
    "Sched Bal for FICO",
    "WA FICO",
    "Most Recent FICO Method",
    
    # Vantage Scores
    "Vantage Score: Primary Borrower",
    "Vantage Score: Co-borrower",
    "Most Recent Vantage Score Method",
    "Vantage Score Date",
    
    # Credit Report
    "Credit Report: Longest Trade Line",
    "Credit Report: Maximum Trade Line",
    "Credit Report: Number of Trade Lines",
    "Credit Line Usage Ratio",
    "Months Bankruptcy",
    "Months Foreclosure",
    
    # Income
    "Primary Borrower Wage Income",
    "Co-Borrower Wage Income",
    "Primary Borrower Other Income",
    "Co-Borrower Other Income",
    "All Borrower Wage Income",
    "All Borrower Total Income",
    "Income Doc Summary",
    
    # Income Verification
    "4506-T Indicator",
    "Borrower Income Verification Level",
    "Co-borrower Income Verification",
    
    # Asset Verification
    "Borrower Asset Verification",
    "Co-borrower Asset Verification",
    "Liquid / Cash Reserves",
    
    # Debt & Ratios
    "Monthly Debt All Borrowers",
    "Fully Indexed Rate",
    "Qualification Method",
    "Percentage of Down Payment from borrower own funds",
    "Updated DTI (Front-end)",
    "Updated DTI (Back-end)",
    "TPR DTI",
    "QM DTI",
    "ATR DTI",
    
    # Property Information
    "City",
    "State",
    "Postal Code",
    "Property Type",
    "Occupancy",
    "Sale Price",
    
    # Property Valuation
    "Original Appraised Property Value",
    "Original Property Valuation Type",
    "Original Property Valuation Date",
    "Original Automated Valuation Model (AVM) Model Name",
    "Original AVM Confidence Score",
    "Most Recent Property Value",
    "Most Recent Property Valuation Type",
    "Most Recent Property Valuation Date",
    "Most Recent AVM Model Name",
    "Most Recent AVM Confidence Score",
    
    # LTV Ratios
    "Original CLTV",
    "WA CLTV",
    "Original LTV",
    "Original Pledged Assets",
    
    # Mortgage Insurance
    "Mortgage Insurance Company Name",
    "Mortgage Insurance Percent",
    "MI: Lender or Borrower Paid?",
    "Pool Insurance Co. Name",
    "Pool Insurance Stop Loss %",
    "MI Certification Number",
    
    # Loan Modification
    "Modification Effective Payment Date",
    "Total Capitalized Amount",
    "Total Deferred Amount",
    "Pre-Modification Interest (Note) Rate",
    "Pre-Modification P&I Payment",
    "Pre-Modification Initial Interest Rate Change Downward Cap",
    "Pre-Modification Subsequent Interest Rate Cap",
    "Pre-Modification Next Interest Rate Change Date",
    "Pre-Modification I/O Term",
    "Forgiven Principal Amount",
    "Forgiven Interest Amount",
    "Number of Modifications",
    
    # Manufactured Housing
    "Real Estate Interest",
    "Community Ownership Structure",
    "Year of Manufacture",
    "HUD Code Compliance Indicator (Y/N)",
    "Gross Manufacturer's Invoice Price",
    "LTI (Loan to Invoice) Gross",
    "Net Manufacturer's Invoice Price",
    "LTI (Net)",
    "Manufacturer's Name",
    "Model Name",
    "Down Payment Source",
    "Community/Related Party Lender (Y/N)",
    "Defined Underwriting Criteria (Y/N)",
    
    # Regulatory Compliance
    "ATR/QM Status",
]
