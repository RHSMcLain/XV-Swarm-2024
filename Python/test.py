import customtkinter, random

global testBox, testBox2, window
window = customtkinter.CTk()
window.geometry("350x420")


testBox2 = customtkinter.CTkTextbox(window, activate_scrollbars=False, font=("Monaco", 20), text_color="black", width=320, height=400, spacing3=17, spacing1=19, fg_color="orange")

testBox2.pack()

displayText = f"Yaw:      {1500}\nPitch:    {1500}\nRoll:     {1500}\nThrottle: {1000}\nArmVar:   {1500}\nNavHold:  {1000}"

testBox2.tag_config("center", justify="center")
testBox2.insert(1.0, displayText)
testBox2.tag_add("center", 0.0, customtkinter.END)

def loop2():
    yaw      = random.randint(1000, 2000)
    pitch    = random.randint(1000, 2000)
    roll     = random.randint(1000, 2000)
    throttle = random.randint(1000, 2000)
    armVar   = random.randint(1000, 2000)
    navHold  = random.randint(1000, 2000)

    testBox2.delete("1.10", 1.14)
    testBox2.insert("1.10", yaw)

    testBox2.delete("2.10", 2.14)
    testBox2.insert("2.10", pitch)

    window.after(500, loop2)

loop2()




# testBox = customtkinter.CTkTextbox(window, fg_color="orange")
# testButton = customtkinter.CTkButton(window, command=lambda:testBox.insert(2.0, "testing\n"))

# testBox.pack()
# testButton.pack()

# testBox.insert(1.0, "Console\n")
# testBox.insert(2.0, "\nhello world")

# print("message: " in "\nmessage: 212408")

# def loop(c):
#     global testBox, window

#     if testBox.get(2.0, 3.0)[:5] == "Msg: ":
#         testBox.delete(2.5, f"2.{len(str(c))+7}")
#         testBox.insert(2.5, c)
#         print(len(str(c))+7)
#     else:
#         testBox.insert(2.0, f"Msg: {c}\n")

#     window.after(100, loop, c+1)

# loop(2)

window.mainloop()
