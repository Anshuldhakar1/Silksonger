class BaseAppError(Exception):
    """
    A base class for all custom exceptions in this application.
    It stores a user-friendly message and a title for popups.
    """
    def __init__(self, dev_message: str, user_message: str, title: str = "Error", app_close: bool = False):
        super().__init__(dev_message)
        self.dev_message = dev_message
        self.user_message = user_message
        self.title = title
        self.app_close = app_close
   
class GamePathNotFoundError(BaseAppError):
    def __init__(self, msg: str):
        user_msg = ("The game directory could not be found.\n"
                    "Please ensure the game is installed and "
                    "has been run at least once.")
        title = "Game Not Found"
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=True)

class ChangeDetectionError(BaseAppError):
    def __init__(self, msg: str):
        title = "Change Detection Error"
        user_msg = "The Change Detection Pipeline has Detected An Error"
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

class SaveFileError(BaseAppError):
    def __init__(self, msg: str):
        title = "Save File Error"
        user_msg = "Failed to process the save file.\nIt might be corrupted, encrypted incorrectly, or empty."
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

class FileOperationError(BaseAppError):
    def __init__(self, msg: str, context: str = "File Operation"):
        title = f"{context} Error"
        user_msg = f"An error occurred during {context}.\nPlease check file permissions and try again."
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

# --- Window Specific Errors ---

class NotificationWindowError(BaseAppError):
    """Raised when an unexpected error occurs in the Notification Window."""
    def __init__(self, msg: str):
        title = "Notification Window Error"
        user_msg = "An unexpected error occurred while displaying the notification."
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

class DashboardError(BaseAppError):
    """Raised when an unexpected error occurs in the Dashboard."""
    def __init__(self, msg: str):
        title = "Dashboard Error"
        user_msg = "An unexpected error occurred in the Dashboard interface."
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)

class ChangeWindowError(BaseAppError):
    """Raised when an unexpected error occurs in the Change Details Window."""
    def __init__(self, msg: str):
        title = "Change Window Error"
        user_msg = "An unexpected error occurred while viewing change details."
        super().__init__(dev_message=msg, user_message=user_msg, title=title, app_close=False)