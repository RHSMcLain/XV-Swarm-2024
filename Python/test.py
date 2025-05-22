import customtkinter

global testBox, window
window = customtkinter.CTk()
window.geometry("200x300")

testBox = customtkinter.CTkTextbox(window, fg_color="orange")
testButton = customtkinter.CTkButton(window, command=lambda:testBox.insert(2.0, "testing\n"))

testBox.pack()
testButton.pack()

testBox.insert(1.0, "Console\n")
testBox.insert(2.0, "\nhello world")

print("message: " in "\nmessage: 212408")

def loop(c):
    global testBox, window

    if testBox.get(2.0, 3.0)[:5] == "Msg: ":
        testBox.delete(2.5, f"2.{len(str(c))+7}")
        testBox.insert(2.5, c)
        print(len(str(c))+7)
    else:
        testBox.insert(2.0, f"Msg: {c}\n")

    window.after(100, loop, c+1)

loop(2)

window.mainloop()
