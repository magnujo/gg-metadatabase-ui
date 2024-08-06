class BaseClass:
    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

class ClassA(BaseClass):
    def __init__(self):
        super().__init__("ClassA")

class ClassB(BaseClass):
    def __init__(self):
        super().__init__("ClassB")

class ClassC(BaseClass):
    def __init__(self):
        super().__init__("ClassC")

# Creating instances of the classes
a = ClassA()
b = ClassB()
c = ClassC()

# Printing the instances
print(a)  # Output: ClassA
print(b)  # Output: ClassB
print(c)  # Output: ClassC


