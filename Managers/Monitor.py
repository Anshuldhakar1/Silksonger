class Monitor():
    def __init__(self):
        print("Created an instance of the monitor")
        self.is_target_set = False

    def set_target(self, filepath: str):
        self.target_file = filepath
        self.is_target_set = True

    def release_target(self):
        self.is_target_set = False