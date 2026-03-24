"""
Entity schema definitions for 150+ field loan document extraction
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date


class LenderInformation(BaseModel):
    """Lender information fields"""
    lender_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    nmls_id: Optional[str] = None
    license_number: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class BorrowerInformation(BaseModel):
    """Borrower information fields"""
    borrower_name: Optional[str] = None
    additional_borrower_name: Optional[str] = None
    borrower_dob: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    loan_number: Optional[str] = None
    ssn: Optional[str] = None
    authorization_number: Optional[str] = None
    email: Optional[str] = None
    home_phone: Optional[str] = None
    work_phone: Optional[str] = None
    cell: Optional[str] = None
    credit_score: Optional[str] = None
    job_title: Optional[str] = None
    current_position: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class CoBorrowerInformation(BaseModel):
    """Co-borrower information fields"""
    co_borrower_name: Optional[str] = None
    dob: Optional[str] = None
    ssn: Optional[str] = None
    credit_score: Optional[str] = None
    email: Optional[str] = None
    phone_cell: Optional[str] = None
    phone_home: Optional[str] = None
    phone_work: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class LoanInformation(BaseModel):
    """Loan information fields"""
    loan_number: Optional[str] = None
    loan_type: Optional[str] = None
    loan_purpose: Optional[str] = None
    loan_amount: Optional[str] = None
    loan_term: Optional[str] = None
    loan_status: Optional[str] = None
    loan_program: Optional[str] = None
    amortization_type: Optional[str] = None
    amortization_term: Optional[str] = None
    monthly_payment: Optional[str] = None
    principal_and_interest: Optional[str] = None
    escrow_payments: Optional[str] = None
    negative_amortization: Optional[str] = None
    mortgage_insurance: Optional[str] = None
    loan_id: Optional[str] = None
    case_file_id: Optional[str] = None
    mers_min_number: Optional[str] = None
    originator_nmls: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class PropertyInformation(BaseModel):
    """Property information fields"""
    property_address: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    condition: Optional[str] = None
    size: Optional[str] = None
    number_of_units: Optional[str] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    age: Optional[str] = None
    appraised_value: Optional[str] = None
    appraisal_type: Optional[str] = None
    original_value: Optional[str] = None
    purchase_price: Optional[str] = None
    estimated_value: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class FinancialInformation(BaseModel):
    """Financial information fields"""
    cash_to_close: Optional[str] = None
    estimated_closing_costs: Optional[str] = None
    lender_credits: Optional[str] = None
    seller_credits: Optional[str] = None
    origination_charges: Optional[str] = None
    discount_points: Optional[str] = None
    finance_charge: Optional[str] = None
    apr: Optional[str] = None
    interest_rate: Optional[str] = None
    prepaid_interest: Optional[str] = None
    points: Optional[str] = None
    late_fees: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class UnderwritingInformation(BaseModel):
    """Underwriting and risk information"""
    credit_score: Optional[str] = None
    report_type: Optional[str] = None
    report_ranking: Optional[str] = None
    dti: Optional[str] = None
    ltv: Optional[str] = None
    cltv: Optional[str] = None
    hcltv: Optional[str] = None
    aus: Optional[str] = None
    aus_result: Optional[str] = None
    du_case_id: Optional[str] = None
    recommendation: Optional[str] = None
    uw_recommendation: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class InsuranceInformation(BaseModel):
    """Insurance information fields"""
    homeowners_insurance: Optional[str] = None
    escrow_waiver: Optional[str] = None
    mip: Optional[str] = None
    pmi: Optional[str] = None
    premium_rates: Optional[str] = None
    premium_amounts: Optional[str] = None
    flood_cert_number: Optional[str] = None
    flood_panel_number: Optional[str] = None
    insurance_required: Optional[str] = None
    flood_zone: Optional[str] = None
    nfip_community: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class EmploymentInformation(BaseModel):
    """Employment and income information"""
    employer_name: Optional[str] = None
    phone_verified: Optional[str] = None
    job_title: Optional[str] = None
    hire_date: Optional[str] = None
    verifier_phone: Optional[str] = None
    tracking_no: Optional[str] = None
    base_income: Optional[str] = None
    bonus: Optional[str] = None
    commission: Optional[str] = None
    overtime: Optional[str] = None
    other_income: Optional[str] = None
    net_rental: Optional[str] = None
    total_income: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class DateInformation(BaseModel):
    """Date and timeline information"""
    application_date: Optional[str] = None
    appraisal_date: Optional[str] = None
    appraisal_effective_date: Optional[str] = None
    first_payment_date: Optional[str] = None
    note_date: Optional[str] = None
    closing_date: Optional[str] = None
    lock_in_expiration: Optional[str] = None
    flood_cert_date: Optional[str] = None
    premium_due_date: Optional[str] = None
    employment_start_date: Optional[str] = None
    casefile_create_date: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True)


class EntityExtractionSchema(BaseModel):
    """Complete entity extraction schema with 150+ fields"""
    lender_information: Optional[LenderInformation] = None
    borrower_information: Optional[BorrowerInformation] = None
    co_borrower_information: Optional[CoBorrowerInformation] = None
    loan_information: Optional[LoanInformation] = None
    property_information: Optional[PropertyInformation] = None
    financial_information: Optional[FinancialInformation] = None
    underwriting_information: Optional[UnderwritingInformation] = None
    insurance_information: Optional[InsuranceInformation] = None
    employment_information: Optional[EmploymentInformation] = None
    date_information: Optional[DateInformation] = None
    additional_fields: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)
