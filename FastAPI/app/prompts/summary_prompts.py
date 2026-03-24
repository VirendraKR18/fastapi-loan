"""
Summary prompt templates
"""

SUMMARY_PROMPT = """
Analyze the provided PDF file and return a structured JSON output summarizing its content. Identify and categorize key components such as notes, deeds, appraisals, and other relevant sections, and generate bookmarks for easy navigation. Validate the presence of all essential documents in the file. Extract and verify key details, ensuring consistency across the document.

Content={}

Instructions:
1.Summary: "A brief textual summary of the document, highlighting its main purpose and key contents.",
Bookmarks:  [{{
      "type": "Identify the document type 'Note', 'Deed', 'Appraisal' sections on the document.",
      "page_number": "The page number where this document type is located."
    }}],
required_documents_present: {{
    "required_documents_present": "Boolean (true/false) indicating if all required documents are present in the file.",
    "missing_documents": [
      "List of any missing critical documents (e.g., ['Deed', 'Appraisal']) or an empty list if all are present."
    ]
  }},
key_details: {{
    "Name": "The primary borrower's full name extracted from the document.",
    "Address": "The property or borrower's address found in the document.",
    "Borrower": "The name of the borrower(s) listed in the document.",
    "Additional Borrower": "The name of the Additional borrower(s), if applicable.",
    "Interest Rate": "The interest rate of the loan mentioned in the document.",
    "Closing Date": "The closing date of the loan or transaction."
  }},
consistency_check: {{
    "status": "Overall status (e.g., 'Pass', 'Fail') indicating if key details are consistent across the document.",
    "inconsistencies": [
      "List of inconsistencies found (e.g., ['Borrower name mismatch between pages 2 and 5']). If all details are consistent, return an empty list."
    ]
  }}
  
Sample Output
{{
  "Summary": "Brief summary of the document",
  "Bookmarks": 
    [{{
      "type": "Note",
      "page_number": 3
    }},
    {{
      "type": "Deed",
      "page_number": 8
    }},
    {{
      "type": "Appraisal",
      "page_number": 12
    }}],
  "required_documents_present": {{
    "required_documents_present": true,
    "missing_documents": [],
  }},
  "key_details": {{
    "Name": "John Doe",
    "Address": "123 Main St, City, State, ZIP",
    "Borrower": "John Doe",
    "Co-Borrower": "Jane Doe",
    "Interest Rate": "3.5%",
    "Closing Date": "2024-03-15"
  }},
  "consistency_check": {{
    "status": "Pass",
    "inconsistencies": []
  }}
}}


Strictly Stick to the output format json 

"""
