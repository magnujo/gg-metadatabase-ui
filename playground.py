
from db_names import db_names
import pandas as pd


d = {"edna_robot_sample": [1,3,3]}



# instance = SubClass()
# print(instance)  # This will print '1'
   
print([db_names.data.edna_robot_sample()])

print(d[db_names.data.edna_robot_sample()])

# print(str("hej"))

# class MyClass(str):
#     def __init__(self, name: str):
#         self.string = name

# my_dict = {'My Key': 1}
# print(MyClass('My Key'))

# print(my_dict[MyClass('My Key')])  # This will now print 1

