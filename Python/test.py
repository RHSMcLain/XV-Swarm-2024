import customtkinter

global testBox, window
window = customtkinter.CTk()
window.geometry("200x200")

testBox = customtkinter.CTkTextbox(window, fg_color="orange")

testBox.pack()

testBox.insert(1.0, "Console\n")
testBox.insert(2.0, "Msg: 1\n")

def loop(c):
    global testBox, window

    testBox.delete(2.5, f"2.{c+5}")
    testBox.insert(2.5, str(c))

    window.after(100, loop, c+1)

loop(2)

window.mainloop()
