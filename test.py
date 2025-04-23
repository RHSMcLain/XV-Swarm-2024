import customtkinter as ctk

def open_popup():
    popup = ctk.CTkToplevel()
    popup.title("Popup Window")
    
    label = ctk.CTkLabel(popup, text="This is a popup message.")
    label.pack(padx=20, pady=10)
    
    button = ctk.CTkButton(popup, text="Close", command=popup.destroy)
    button.pack(pady=10)
    
    popup.grab_set()  # Make the popup modal
    root.wait_window(popup) # Wait for the popup to close

root = ctk.CTk()
root.title("Main Window")

open_popup_button = ctk.CTkButton(root, text="Open Popup", command=open_popup)
open_popup_button.pack(padx=20, pady=20)

root.mainloop()