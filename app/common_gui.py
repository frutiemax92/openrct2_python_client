from tkinter import filedialog, Tk

def get_file_path():
    # put the tkinter as topmost for the file dialogs
    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.withdraw()

    file_path = filedialog.askdirectory()
    root.destroy()
    return file_path
