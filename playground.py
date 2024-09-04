# Using the intersection method
set1 = {"apple", "banana", "cherry"}
set2 = {"banana", "cherry", "date"}
intersection = set1.intersection(set2).union(set2.intersection(set1))
print(intersection)  # Output: {'banana', 'cherry'}

# Using the & operator
intersection = set1 & set2
print(intersection)  # Output: {'banana', 'cherry'}
