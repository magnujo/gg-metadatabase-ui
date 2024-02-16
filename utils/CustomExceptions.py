import traceback

# class ExplicitBaseException(BaseException):
#     def __init__(self, message):
#         super().__init__(message)
#         self.custom_message = message
#         self.traceback = traceback.format_exc()

#     def __str__(self):
#         return f"{self.custom_message}\nTraceback:\n{self.traceback}"
        

class DontTriggerFileDeletion(Exception):
    def __init__(self, message):
        super().__init__(message)

        