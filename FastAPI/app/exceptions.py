"""
Custom exception classes
"""


class PDFNotFoundException(Exception):
    """Raised when PDF file is not found"""
    def __init__(self, message: str = "No document uploaded. Please upload a PDF first."):
        self.message = message
        super().__init__(self.message)


class InvalidFileTypeException(Exception):
    """Raised when uploaded file is not a PDF"""
    def __init__(self, message: str = "Invalid file type. Only PDF files are supported."):
        self.message = message
        super().__init__(self.message)


class ProcessingException(Exception):
    """Raised when document processing fails"""
    def __init__(self, message: str = "Failed to process document. Please try again."):
        self.message = message
        super().__init__(self.message)


class AzureOpenAIException(Exception):
    """Raised when Azure OpenAI API call fails"""
    def __init__(self, message: str = "Failed to generate response. Please try again."):
        self.message = message
        super().__init__(self.message)


class VectorizationException(Exception):
    """Raised when vector embedding generation fails"""
    def __init__(self, message: str = "Failed to create vector embeddings. Please try again."):
        self.message = message
        super().__init__(self.message)
