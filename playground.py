
try:
    raise FileExistsError("he")
    raise Exception("hej")

except FileExistsError as e:
    print(e)
    print("file not deleted")                    

except Exception as e:
    print("file deleted")