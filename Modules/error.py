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
   
class GamePathNotFoundError(BaseAppError):
    """BaseAppError raised when the expected game directory is not found."""
    def __init__(self, msg: str):
        # 1. Define the friendly info
        dev_msg = msg
        user_msg = ("The game directory could not be found.\n"
                    "Please ensure the game is installed and "
                    "has been run at least once.")
        title = "Game Not Found"

        super().__init__(dev_message=dev_msg, user_message=user_msg, title=title, app_close=True)


class ChangeDetectionError(BaseAppError):
    """BaseAppError raised when error comes up in the change detection pipeline."""
    def __init__(self, msg: str):
        dev_msg = msg
        title = "Change Detection Error"
        user_msg = ("The Change Detection Pipeline has Detected An Error")

        super().__init__(dev_message=dev_msg, user_message=user_msg, title=title, app_close=False)

class NotificationWindowError(BaseAppError):
    """BaseAppError raised when any kind of error happens in the Notificaiton Window."""

    def __init__(self, msg: str):

        title = "Error in Notification window"
        user_message = "An Error occured in the Notification Window, probably an inner module error."
        
        super().__init__(dev_message=msg, user_message=user_message, title=title, app_close=False)

class SaveFileError(BaseAppError):
    """Raised when encryption/decryption or JSON parsing of the save file fails."""
    def __init__(self, msg: str):
        title = "Save File Error"
        user_msg = "Failed to process the save file.\nIt might be corrupted, encrypted incorrectly, or empty."
        
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

class FileOperationError(BaseAppError):
    """Raised when general file IO operations fail (reading/writing/creating)."""
    def __init__(self, msg: str, context: str = "File Operation"):
        title = f"{context} Error"
        user_msg = f"An error occurred during {context}.\nPlease check file permissions and try again."
        
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)
