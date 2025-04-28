from tkinter import *


def findWindowScale():
    root = Tk()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return (height, width)

print(findWindowScale())
