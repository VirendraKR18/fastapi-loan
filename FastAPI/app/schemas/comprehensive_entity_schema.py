"""
Comprehensive entity schema definitions for 150+ field loan document extraction
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


class ServicingInformation(BaseModel):
    """Servicing fees and methodology"""
    servicing_fee_percentage: Optional[str] = Field(None, alias="Servicing Fee - Percentage")
    servicing_fee_flat_dollar: Optional[str] = Field(None, alias="Servicing Fee - Flat Dollar")
    servicing_advance_methodology: Optional[str] = Field(None, alias="Servicing Advance Methodology")
    
    model_config = ConfigDict(populate_by_name=True)


class LoanIdentifiers(BaseModel):
    """Loan identification fields"""
    originator: Optional[str] = Field(None, alias="Originator")
    loan_group: Optional[str] = Field(None, alias="Loan Group")
    loan_number: Optional[str] = Field(None, alias="Loan Number")
    doc_type: Optional[str] = Field(None, alias="Doc Type")
    sched_bal: Optional[str] = Field(None, alias="Sched Bal")
    primary_borrower_id: Optional[str] = Field(None, alias="Primary Borrower ID")
    
    model_config = ConfigDict(populate_by_name=True)


class LoanDetails(BaseModel):
    """Detailed loan characteristics"""
    amortization_type: Optional[str] = Field(None, alias="Amortization Type")
    lien_position: Optional[str] = Field(None, alias="Lien Position")
    heloc_indicator: Optional[str] = Field(None, alias="HELOC Indicator")
    loan_purpose: Optional[str] = Field(None, alias="Loan Purpose")
    cash_out_amount: Optional[str] = Field(None, alias="Cash Out Amount")
    total_origination_and_discount_points: Optional[str] = Field(None, alias="Total Origination and Discount Points")
    covered_high_cost_loan_indicator: Optional[str] = Field(None, alias="Covered/High Cost Loan Indicator")
    relocation_loan_indicator: Optional[str] = Field(None, alias="Relocation Loan Indicator")
    broker_indicator: Optional[str] = Field(None, alias="Broker Indicator")
    channel: Optional[str] = Field(None, alias="Channel")
    escrow_indicator: Optional[str] = Field(None, alias="Escrow Indicator")
    loan_type_of_most_senior_lien: Optional[str] = Field(None, alias="Loan Type of Most Senior Lien")
    hybrid_period_of_most_senior_lien: Optional[str] = Field(None, alias="Hybrid Period of Most Senior Lien")
    neg_am_limit_of_most_senior_lien: Optional[str] = Field(None, alias="Neg Am Limit of Most Senior Lien")
    option_arm_indicator: Optional[str] = Field(None, alias="Option ARM Indicator")
    options_at_recast: Optional[str] = Field(None, alias="Options at Recast")
    chattel_indicator: Optional[str] = Field(None, alias="Chattel Indicator")
    
    model_config = ConfigDict(populate_by_name=True)


class SeniorJuniorLoans(BaseModel):
    """Senior and junior loan information"""
    senior_loan_amount: Optional[str] = Field(None, alias="Senior Loan Amount")
    junior_mortgage_balance: Optional[str] = Field(None, alias="Junior Mortgage Balance")
    origination_date_of_most_senior_lien: Optional[str] = Field(None, alias="Origination Date of Most Senior Lien")
    
    model_config = ConfigDict(populate_by_name=True)


class LoanTerms(BaseModel):
    """Original loan terms"""
    origination_date: Optional[str] = Field(None, alias="Origination Date")
    original_loan_amount: Optional[str] = Field(None, alias="Original Loan Amount")
    original_interest_rate: Optional[str] = Field(None, alias="Original Interest Rate")
    original_amortization_term: Optional[str] = Field(None, alias="Original Amortization Term")
    original_term_to_maturity: Optional[str] = Field(None, alias="Original Term to Maturity")
    first_payment_date_of_loan: Optional[str] = Field(None, alias="First Payment Date of Loan")
    interest_type_indicator: Optional[str] = Field(None, alias="Interest Type Indicator")
    original_interest_only_term: Optional[str] = Field(None, alias="Original Interest Only Term")
    buy_down_period: Optional[str] = Field(None, alias="Buy Down Period")
    heloc_draw_period: Optional[str] = Field(None, alias="HELOC Draw Period")
    
    model_config = ConfigDict(populate_by_name=True)


class CurrentLoanStatus(BaseModel):
    """Current loan status and payment information"""
    current_loan_amount: Optional[str] = Field(None, alias="Current Loan Amount")
    current_interest_rate: Optional[str] = Field(None, alias="Current Interest Rate")
    wac: Optional[str] = Field(None, alias="WAC")
    current_payment_amount_due: Optional[str] = Field(None, alias="Current Payment Amount Due")
    interest_paid_through_date: Optional[str] = Field(None, alias="Interest Paid Through Date")
    current_payment_status: Optional[str] = Field(None, alias="Current Payment Status")
    current_other_monthly_payment: Optional[str] = Field(None, alias="Current 'Other' Monthly Payment")
    
    model_config = ConfigDict(populate_by_name=True)


class ARMDetails(BaseModel):
    """Adjustable Rate Mortgage details"""
    index_type: Optional[str] = Field(None, alias="Index Type")
    arm_look_back_days: Optional[str] = Field(None, alias="ARM Look-Back Days")
    gross_margin: Optional[str] = Field(None, alias="Gross Margin")
    arm_round_flag: Optional[str] = Field(None, alias="ARM Round Flag")
    arm_round_factor: Optional[str] = Field(None, alias="ARM Round Factor")
    initial_fixed_rate_period: Optional[str] = Field(None, alias="Initial Fixed Rate Period")
    initial_interest_rate_cap_change_up: Optional[str] = Field(None, alias="Initial Interest Rate Cap (Change Up)")
    initial_interest_rate_cap_change_down: Optional[str] = Field(None, alias="Initial Interest Rate Cap (Change Down)")
    subsequent_interest_rate_reset_period: Optional[str] = Field(None, alias="Subsequent Interest Rate Reset Period")
    subsequent_interest_rate_change_down: Optional[str] = Field(None, alias="Subsequent Interest Rate (Change Down)")
    subsequent_interest_rate_cap_change_up: Optional[str] = Field(None, alias="Subsequent Interest Rate Cap (Change Up)")
    lifetime_maximum_rate: Optional[str] = Field(None, alias="Lifetime Maximum Rate")
    lifetime_minimum_rate: Optional[str] = Field(None, alias="Lifetime Minimum Rate")
    
    model_config = ConfigDict(populate_by_name=True)


class NegativeAmortization(BaseModel):
    """Negative amortization details"""
    negative_amortization_limit: Optional[str] = Field(None, alias="Negative Amortization Limit")
    initial_negative_amortization_recast_period: Optional[str] = Field(None, alias="Initial Negative Amortization Recast Period")
    subsequent_negative_amortization_recast_period: Optional[str] = Field(None, alias="Subsequent Negative Amortization Recast Period")
    
    model_config = ConfigDict(populate_by_name=True)


class PaymentDetails(BaseModel):
    """Payment schedule and cap details"""
    initial_fixed_payment_period: Optional[str] = Field(None, alias="Initial Fixed Payment Period")
    subsequent_payment_reset_period: Optional[str] = Field(None, alias="Subsequent Payment Reset Period")
    initial_periodic_payment_cap: Optional[str] = Field(None, alias="Initial Periodic Payment Cap")
    subsequent_periodic_payment_cap: Optional[str] = Field(None, alias="Subsequent Periodic Payment Cap")
    initial_minimum_payment_reset_period: Optional[str] = Field(None, alias="Initial Minimum Payment Reset Period")
    subsequent_minimum_payment_reset_period: Optional[str] = Field(None, alias="Subsequent Minimum Payment Reset Period")
    initial_minimum_payment: Optional[str] = Field(None, alias="Initial Minimum Payment")
    current_minimum_payment: Optional[str] = Field(None, alias="Current Minimum Payment")
    
    model_config = ConfigDict(populate_by_name=True)


class PrepaymentPenalty(BaseModel):
    """Prepayment penalty information"""
    prepayment_penalty_calculation: Optional[str] = Field(None, alias="Prepayment Penalty Calculation")
    prepayment_penalty_type: Optional[str] = Field(None, alias="Prepayment Penalty Type")
    prepayment_penalty_total_term: Optional[str] = Field(None, alias="Prepayment Penalty Total Term")
    prepayment_penalty_hard_term: Optional[str] = Field(None, alias="Prepayment Penalty Hard Term")
    
    model_config = ConfigDict(populate_by_name=True)


class BorrowerInformation(BaseModel):
    """Borrower information and employment status"""
    number_of_mortgaged_properties: Optional[str] = Field(None, alias="Number of Mortgaged Properties")
    total_number_of_borrowers: Optional[str] = Field(None, alias="Total Number of Borrowers")
    self_employment_flag: Optional[str] = Field(None, alias="Self-employment Flag")
    years_in_home: Optional[str] = Field(None, alias="Years in Home")
    borrower_1_employment_status: Optional[str] = Field(None, alias="Borrower 1 Employment Status")
    borrower_2_employment_status: Optional[str] = Field(None, alias="Borrower 2 Employment Status")
    borrower_3_employment_status: Optional[str] = Field(None, alias="Borrower 3 Employment Status")
    borrower_4_employment_status: Optional[str] = Field(None, alias="Borrower 4 Employment Status")
    
    model_config = ConfigDict(populate_by_name=True)


class EmploymentInformation(BaseModel):
    """Employment verification and duration"""
    length_of_employment_borrower: Optional[str] = Field(None, alias="Length of Employment: Borrower")
    length_of_employment_co_borrower: Optional[str] = Field(None, alias="Length of Employment: Co-borrower")
    borrower_employment_verification: Optional[str] = Field(None, alias="Borrower Employment Verification")
    co_borrower_employment_verification: Optional[str] = Field(None, alias="Co-borrower Employment Verification")
    
    model_config = ConfigDict(populate_by_name=True)


class FICOScores(BaseModel):
    """FICO credit score information"""
    fico_model_used: Optional[str] = Field(None, alias="FICO Model Used")
    most_recent_fico_date: Optional[str] = Field(None, alias="Most Recent FICO Date")
    primary_wage_earner_original_fico_equifax: Optional[str] = Field(None, alias="Primary Wage Earner Original FICO: Equifax")
    primary_wage_earner_original_fico_experian: Optional[str] = Field(None, alias="Primary Wage Earner Original FICO: Experian")
    primary_wage_earner_original_fico_transunion: Optional[str] = Field(None, alias="Primary Wage Earner Original FICO: TransUnion")
    secondary_wage_earner_original_fico_equifax: Optional[str] = Field(None, alias="Secondary Wage Earner Original FICO: Equifax")
    secondary_wage_earner_original_fico_experian: Optional[str] = Field(None, alias="Secondary Wage Earner Original FICO: Experian")
    secondary_wage_earner_original_fico_transunion: Optional[str] = Field(None, alias="Secondary Wage Earner Original FICO: Transunion")
    most_recent_primary_borrower_fico: Optional[str] = Field(None, alias="Most Recent Primary Borrower FICO")
    most_recent_co_borrower_fico: Optional[str] = Field(None, alias="Most Recent Co-Borrower FICO")
    fico: Optional[str] = Field(None, alias="FICO")
    sched_bal_for_fico: Optional[str] = Field(None, alias="Sched Bal for FICO")
    wa_fico: Optional[str] = Field(None, alias="WA FICO")
    most_recent_fico_method: Optional[str] = Field(None, alias="Most Recent FICO Method")
    
    model_config = ConfigDict(populate_by_name=True)


class VantageScores(BaseModel):
    """VantageScore credit information"""
    vantage_score_primary_borrower: Optional[str] = Field(None, alias="Vantage Score: Primary Borrower")
    vantage_score_co_borrower: Optional[str] = Field(None, alias="Vantage Score: Co-borrower")
    most_recent_vantage_score_method: Optional[str] = Field(None, alias="Most Recent Vantage Score Method")
    vantage_score_date: Optional[str] = Field(None, alias="Vantage Score Date")
    
    model_config = ConfigDict(populate_by_name=True)


class CreditReport(BaseModel):
    """Credit report details"""
    credit_report_longest_trade_line: Optional[str] = Field(None, alias="Credit Report: Longest Trade Line")
    credit_report_maximum_trade_line: Optional[str] = Field(None, alias="Credit Report: Maximum Trade Line")
    credit_report_number_of_trade_lines: Optional[str] = Field(None, alias="Credit Report: Number of Trade Lines")
    credit_line_usage_ratio: Optional[str] = Field(None, alias="Credit Line Usage Ratio")
    months_bankruptcy: Optional[str] = Field(None, alias="Months Bankruptcy")
    months_foreclosure: Optional[str] = Field(None, alias="Months Foreclosure")
    
    model_config = ConfigDict(populate_by_name=True)


class IncomeInformation(BaseModel):
    """Income details for all borrowers"""
    primary_borrower_wage_income: Optional[str] = Field(None, alias="Primary Borrower Wage Income")
    co_borrower_wage_income: Optional[str] = Field(None, alias="Co-Borrower Wage Income")
    primary_borrower_other_income: Optional[str] = Field(None, alias="Primary Borrower Other Income")
    co_borrower_other_income: Optional[str] = Field(None, alias="Co-Borrower Other Income")
    all_borrower_wage_income: Optional[str] = Field(None, alias="All Borrower Wage Income")
    all_borrower_total_income: Optional[str] = Field(None, alias="All Borrower Total Income")
    income_doc_summary: Optional[str] = Field(None, alias="Income Doc Summary")
    
    model_config = ConfigDict(populate_by_name=True)


class IncomeVerification(BaseModel):
    """Income verification details"""
    indicator_4506_t: Optional[str] = Field(None, alias="4506-T Indicator")
    borrower_income_verification_level: Optional[str] = Field(None, alias="Borrower Income Verification Level")
    co_borrower_income_verification: Optional[str] = Field(None, alias="Co-borrower Income Verification")
    
    model_config = ConfigDict(populate_by_name=True)


class AssetVerification(BaseModel):
    """Asset verification details"""
    borrower_asset_verification: Optional[str] = Field(None, alias="Borrower Asset Verification")
    co_borrower_asset_verification: Optional[str] = Field(None, alias="Co-borrower Asset Verification")
    liquid_cash_reserves: Optional[str] = Field(None, alias="Liquid / Cash Reserves")
    
    model_config = ConfigDict(populate_by_name=True)


class DebtRatios(BaseModel):
    """Debt-to-income and qualification ratios"""
    monthly_debt_all_borrowers: Optional[str] = Field(None, alias="Monthly Debt All Borrowers")
    fully_indexed_rate: Optional[str] = Field(None, alias="Fully Indexed Rate")
    qualification_method: Optional[str] = Field(None, alias="Qualification Method")
    percentage_of_down_payment_from_borrower_own_funds: Optional[str] = Field(None, alias="Percentage of Down Payment from borrower own funds")
    updated_dti_front_end: Optional[str] = Field(None, alias="Updated DTI (Front-end)")
    updated_dti_back_end: Optional[str] = Field(None, alias="Updated DTI (Back-end)")
    tpr_dti: Optional[str] = Field(None, alias="TPR DTI")
    qm_dti: Optional[str] = Field(None, alias="QM DTI")
    atr_dti: Optional[str] = Field(None, alias="ATR DTI")
    
    model_config = ConfigDict(populate_by_name=True)


class PropertyInformation(BaseModel):
    """Property location and details"""
    city: Optional[str] = Field(None, alias="City")
    state: Optional[str] = Field(None, alias="State")
    postal_code: Optional[str] = Field(None, alias="Postal Code")
    property_type: Optional[str] = Field(None, alias="Property Type")
    occupancy: Optional[str] = Field(None, alias="Occupancy")
    sale_price: Optional[str] = Field(None, alias="Sale Price")
    
    model_config = ConfigDict(populate_by_name=True)


class PropertyValuation(BaseModel):
    """Property valuation and appraisal information"""
    original_appraised_property_value: Optional[str] = Field(None, alias="Original Appraised Property Value")
    original_property_valuation_type: Optional[str] = Field(None, alias="Original Property Valuation Type")
    original_property_valuation_date: Optional[str] = Field(None, alias="Original Property Valuation Date")
    original_avm_model_name: Optional[str] = Field(None, alias="Original Automated Valuation Model (AVM) Model Name")
    original_avm_confidence_score: Optional[str] = Field(None, alias="Original AVM Confidence Score")
    most_recent_property_value: Optional[str] = Field(None, alias="Most Recent Property Value")
    most_recent_property_valuation_type: Optional[str] = Field(None, alias="Most Recent Property Valuation Type")
    most_recent_property_valuation_date: Optional[str] = Field(None, alias="Most Recent Property Valuation Date")
    most_recent_avm_model_name: Optional[str] = Field(None, alias="Most Recent AVM Model Name")
    most_recent_avm_confidence_score: Optional[str] = Field(None, alias="Most Recent AVM Confidence Score")
    
    model_config = ConfigDict(populate_by_name=True)


class LTVRatios(BaseModel):
    """Loan-to-value ratios"""
    original_cltv: Optional[str] = Field(None, alias="Original CLTV")
    wa_cltv: Optional[str] = Field(None, alias="WA CLTV")
    original_ltv: Optional[str] = Field(None, alias="Original LTV")
    original_pledged_assets: Optional[str] = Field(None, alias="Original Pledged Assets")
    
    model_config = ConfigDict(populate_by_name=True)


class MortgageInsurance(BaseModel):
    """Mortgage insurance details"""
    mortgage_insurance_company_name: Optional[str] = Field(None, alias="Mortgage Insurance Company Name")
    mortgage_insurance_percent: Optional[str] = Field(None, alias="Mortgage Insurance Percent")
    mi_lender_or_borrower_paid: Optional[str] = Field(None, alias="MI: Lender or Borrower Paid?")
    pool_insurance_co_name: Optional[str] = Field(None, alias="Pool Insurance Co. Name")
    pool_insurance_stop_loss_percent: Optional[str] = Field(None, alias="Pool Insurance Stop Loss %")
    mi_certification_number: Optional[str] = Field(None, alias="MI Certification Number")
    
    model_config = ConfigDict(populate_by_name=True)


class LoanModification(BaseModel):
    """Loan modification details"""
    modification_effective_payment_date: Optional[str] = Field(None, alias="Modification Effective Payment Date")
    total_capitalized_amount: Optional[str] = Field(None, alias="Total Capitalized Amount")
    total_deferred_amount: Optional[str] = Field(None, alias="Total Deferred Amount")
    pre_modification_interest_note_rate: Optional[str] = Field(None, alias="Pre-Modification Interest (Note) Rate")
    pre_modification_pi_payment: Optional[str] = Field(None, alias="Pre-Modification P&I Payment")
    pre_modification_initial_interest_rate_change_downward_cap: Optional[str] = Field(None, alias="Pre-Modification Initial Interest Rate Change Downward Cap")
    pre_modification_subsequent_interest_rate_cap: Optional[str] = Field(None, alias="Pre-Modification Subsequent Interest Rate Cap")
    pre_modification_next_interest_rate_change_date: Optional[str] = Field(None, alias="Pre-Modification Next Interest Rate Change Date")
    pre_modification_io_term: Optional[str] = Field(None, alias="Pre-Modification I/O Term")
    forgiven_principal_amount: Optional[str] = Field(None, alias="Forgiven Principal Amount")
    forgiven_interest_amount: Optional[str] = Field(None, alias="Forgiven Interest Amount")
    number_of_modifications: Optional[str] = Field(None, alias="Number of Modifications")
    
    model_config = ConfigDict(populate_by_name=True)


class ManufacturedHousing(BaseModel):
    """Manufactured housing specific fields"""
    real_estate_interest: Optional[str] = Field(None, alias="Real Estate Interest")
    community_ownership_structure: Optional[str] = Field(None, alias="Community Ownership Structure")
    year_of_manufacture: Optional[str] = Field(None, alias="Year of Manufacture")
    hud_code_compliance_indicator: Optional[str] = Field(None, alias="HUD Code Compliance Indicator (Y/N)")
    gross_manufacturers_invoice_price: Optional[str] = Field(None, alias="Gross Manufacturer's Invoice Price")
    lti_loan_to_invoice_gross: Optional[str] = Field(None, alias="LTI (Loan to Invoice) Gross")
    net_manufacturers_invoice_price: Optional[str] = Field(None, alias="Net Manufacturer's Invoice Price")
    lti_net: Optional[str] = Field(None, alias="LTI (Net)")
    manufacturers_name: Optional[str] = Field(None, alias="Manufacturer's Name")
    model_name: Optional[str] = Field(None, alias="Model Name")
    down_payment_source: Optional[str] = Field(None, alias="Down Payment Source")
    community_related_party_lender: Optional[str] = Field(None, alias="Community/Related Party Lender (Y/N)")
    defined_underwriting_criteria: Optional[str] = Field(None, alias="Defined Underwriting Criteria (Y/N)")
    
    model_config = ConfigDict(populate_by_name=True)


class RegulatoryCompliance(BaseModel):
    """Regulatory compliance information"""
    atr_qm_status: Optional[str] = Field(None, alias="ATR/QM Status")
    
    model_config = ConfigDict(populate_by_name=True)


class ComprehensiveEntityExtractionSchema(BaseModel):
    """Complete entity extraction schema with 150+ fields organized by category"""
    servicing_information: Optional[ServicingInformation] = None
    loan_identifiers: Optional[LoanIdentifiers] = None
    loan_details: Optional[LoanDetails] = None
    senior_junior_loans: Optional[SeniorJuniorLoans] = None
    loan_terms: Optional[LoanTerms] = None
    current_loan_status: Optional[CurrentLoanStatus] = None
    arm_details: Optional[ARMDetails] = None
    negative_amortization: Optional[NegativeAmortization] = None
    payment_details: Optional[PaymentDetails] = None
    prepayment_penalty: Optional[PrepaymentPenalty] = None
    borrower_information: Optional[BorrowerInformation] = None
    employment_information: Optional[EmploymentInformation] = None
    fico_scores: Optional[FICOScores] = None
    vantage_scores: Optional[VantageScores] = None
    credit_report: Optional[CreditReport] = None
    income_information: Optional[IncomeInformation] = None
    income_verification: Optional[IncomeVerification] = None
    asset_verification: Optional[AssetVerification] = None
    debt_ratios: Optional[DebtRatios] = None
    property_information: Optional[PropertyInformation] = None
    property_valuation: Optional[PropertyValuation] = None
    ltv_ratios: Optional[LTVRatios] = None
    mortgage_insurance: Optional[MortgageInsurance] = None
    loan_modification: Optional[LoanModification] = None
    manufactured_housing: Optional[ManufacturedHousing] = None
    regulatory_compliance: Optional[RegulatoryCompliance] = None
    additional_fields: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)
