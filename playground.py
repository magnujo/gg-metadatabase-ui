import xlwings as xw

# Create a new workbook
wb = xw.Book()

# Add VBA code dynamically
vba_code = """
Private Sub Workbook_Open()
Application.CellDragAndDrop = False
End Sub
"""
# Add a VBA module to the workbook
wb.api.VBProject.VBComponents.Add(1).CodeModule.AddFromString(vba_code)

# Save the workbook as a macro-enabled file
wb.save("dynamic_macro.xlsm")

# Run the macro
macro = wb.macro("EnableDragFill")
macro()  # Execute the macro

# Close the workbook
wb.close()

print("Drag-fill enabled and VBA macro executed dynamically.")