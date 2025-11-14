class BaseAppError(Exception):
    """
    A base class for all custom exceptions in this application.
    It stores a user-friendly message and a title for popups.
    """
    def __init__(self, dev_message: str, user_message: str, title: str = "Error", app_close: bool = False):
        # The 'dev_message' is the standard technical error message
        super().__init__(dev_message)
        
        # These are your custom attributes for the popup
        self.dev_message = dev_message
        self.user_message = user_message
        self.title = title
        self.app_close = app_close