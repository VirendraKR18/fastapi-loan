"""
Entity extraction prompt templates
"""

ENTITY_EXTRACTION_PROMPT = """
Extract ALL loan information from this document. Respond with ONLY valid JSON.

Document:
{}

Extract these categories (include ANY fields you find):
- Loan_Details: loan number, original loan amount, current loan amount, rate, term, type, purpose, dates, finance charge, amount financed, total of payments, TIP (Total Interest Percentage), late fee
- Borrower_Information: names, SSN, DOB, contact, address, employment, income
- Property_Information: address, city, state, zip, type, value, price, occupancy
- Financial_Details: down payment, LTV, DTI, closing costs, fees
- Insurance_Information: hazard, flood, mortgage insurance, company, premium
- Lender_Information: lender name, address, NMLS, loan officer
- Payoffs_and_Payments: payoff amounts, payees, account numbers
- Closing_Costs_Summary: total costs, itemized fees, credits
- Escrow: escrow indicator, monthly escrow payment, property taxes, insurance reserves, total escrow amounts
- Payment_Schedule: monthly payment, principal, interest, escrow breakdown, current payment amount due, total monthly payment
- TRID_Tolerance: tolerance categories, variances, compliance
- Additional_Fields: any other loan data

**OUTPUT FORMAT** (respond with ONLY this JSON, nothing else):

{{
  "entities": {{
    "Loan_Details": {{
      "Loan Number": "value",
      "Original Loan Amount (from Loan Estimate)": "value",
      "Final Loan Amount": "value",
      "Current Loan Amount": "value",
      "Original Interest Rate": "value",
      "Original Amortization Term": "value",
      "Amortization Type": "value",
      "First Payment Date of Loan": "value",
      "Finance Charge": "value",
      "Amount Financed": "value",
      "Total of Payments": "value",
      "TIP (Total Interest Percentage)": "value",
      "Late Fee": "value",
      "Primary Loan Purpose": "value (from Closing Instructions)",
      "CD Loan Purpose": "value (from Closing Disclosure)",
      "Servicing Loan Number": "value"
    }},
    "Borrower_Information": {{
      "Borrower Name": "value",
      "Total Number of Borrowers": "value",
      "Address": "value"
    }},
    "Property_Information": {{
      "Property Address": "value",
      "City": "value",
      "State": "value",
      "Occupancy": "value",
      "Original Appraised Property Value": "value"
    }},
    "Payoffs_and_Payments": {{
      "Payoff 1 Payee": "value",
      "Payoff 1 Amount": "value",
      "Payoff 2 Payee": "value",
      "Payoff 2 Amount": "value"
    }},
    "Closing_Costs_Summary": {{
      "Total Closing Costs": "value",
      "Origination Charges Subtotal": "value",
      "Services Borrower Did Not Shop For Subtotal": "value",
      "Services Borrower Did Shop For Subtotal": "value",
      "Taxes and Government Fees Subtotal": "value",
      "Prepaids Subtotal": "value",
      "Initial Escrow Payment Subtotal": "value",
      "Other Costs Subtotal": "value"
    }},
    "Escrow": {{
      "Escrow Indicator": "value",
      "Monthly Escrow Payment": "value",
      "Property Taxes": "value",
      "Property Taxes Reserve": "value",
      "Homeowners Insurance Reserve": "value",
      "Insurance Reserves": "value",
      "Other Reserves": "value",
      "Escrow Account Details": "value"
    }},
    "Payment_Schedule": {{
      "Monthly Principal and Interest": "value",
      "Monthly Mortgage Insurance": "value",
      "Monthly Escrow": "value",
      "Current Payment Amount Due": "value",
      "Total Monthly Payment": "value"
    }}
  }},
  "topics": []
}}

**CRITICAL RULES**:
1. Response must be ONLY valid JSON - no markdown, no explanations
2. Extract EVERY field you can find in the document
3. For complex nested data (payoffs, closing costs, escrow), extract as individual fields with clear names
4. NEVER use nested objects or arrays as field values - flatten all data into string values
5. For fields appearing in multiple sections (like Loan Purpose), label the source in the field name
6. Use clear, descriptive field names that include the source when relevant
7. If you find a field, include it - don't leave categories empty
8. All field values must be strings or numbers - no objects or arrays
9. For lists (like multiple payoffs), create separate fields: "Payoff 1", "Payoff 2", etc.
10. If the document has loan information, you MUST extract it
11. For Closing Costs sections (Origination Charges, Services, Taxes, Prepaids, Other Costs, etc.), extract the SUBTOTAL amount for each section, NOT individual line items
12. Look for labels like "Subtotal", "Total", or section summary amounts when extracting closing costs
13. "Original Loan Amount (from Loan Estimate)" should be the ORIGINAL loan estimate amount (e.g., $203,000), NOT the final/current amount (e.g., $198,000)
14. "Final Loan Amount" is the final/closing loan amount, which may differ from the original estimate

"""


ITEM_EXTRACTION_PROMPT = """
You are a data analyst tasked with extracting item details from a JSON file. Your role involves identifying and organizing key information from the provided JSON data.

You must respond with valid JSON only. Do not include any explanatory text outside the JSON structure.

{}
Extract item details from the given JSON.
### Instructions:
- Identify all items that contain a `"Description"` field.
- If `"Serial Numbers"` and `"Asset Tags"` exist, pair each serial number with an asset tag while maintaining the `"Description"`.
- If multiple `"Serial Numbers"` and `"Asset Tags"` exist, create separate rows for each pair.
- If `"Serial Numbers"` or `"Asset Tags"` are missing, use `null` as a placeholder.
- If neither `"Serial Numbers"` nor `"Asset Tags"` exist for an item, return a single row with `null` values.
- If a **serial number is embedded within the `"Description"`**, extract each serial number and create separate rows for them and give the separete row Also, include a row with the description alone (without serial number).
- **Always maintain the order of the items as they appear in the input JSON**. Do not alter the order or provide any cross-output of the items.
- The output **must** be strictly in JSON format.

### **Output Format:**
```json
{{
  "items": [
    ["Description", "Serial Number", "Asset Tag"],
    ...
  ]
}}
"""
