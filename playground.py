import os
import inspect
dict = {'file_name': None}

def current_function_name():
    return inspect.currentframe().f_back.f_code.co_name

def index():
    print("Currently executing:", current_function_name())

index()

I dont want to delete the upload file if everything seems ok
I 