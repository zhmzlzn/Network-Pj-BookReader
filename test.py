from tkinter.filedialog import askdirectory # 选择路径

path = askdirectory()
print(type(path), path)