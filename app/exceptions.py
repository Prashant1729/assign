class FileProcessingError(Exception):
    """Exception raised for errors in processing resume or job description files."""
    def __init__(self, message="Error processing the file."):
        self.message = message
        super().__init__(self.message)


class OpenAIProcessingError(Exception):
    """Exception raised for errors in OpenAI API processing."""
    def __init__(self, message="Error processing data with OpenAI API."):
        self.message = message
        super().__init__(self.message)
