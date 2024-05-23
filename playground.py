from validation_tools import validate
import pandas as pd
s = pd.read_csv(r"c:\Users\glj523\Downloads\test7.txt", sep='\t', encoding='utf_16', dtype=str)
res = validate.validate_enums_exp(s, "field_sample")
print(res)