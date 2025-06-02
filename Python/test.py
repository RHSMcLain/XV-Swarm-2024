import customtkinter as ctk

# Global variables
lat1 = 0.0
long1 = 0.0
lat2 = 0.0
long2 = 0.0
alt = 0.0

class CoordinateEditorWindow:
    def __init__(self, parent):
        # Create coordinate editor window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Coordinate Editor")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Edit Coordinates", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(20, 30))
        
        # Create input fields
        self.create_input_fields()
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20, fill="x", padx=20)
        
        # Update button
        self.update_button = ctk.CTkButton(
            self.button_frame,
            text="Update Variables",
            command=self.update_globals,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.update_button.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.window.destroy,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="gray"
        )
        self.cancel_button.pack(side="right", fill="x", expand=True)
        
        # Load current values into entry fields
        self.load_current_values()
    
    def create_input_fields(self):
        # Latitude 1
        self.lat1_label = ctk.CTkLabel(self.main_frame, text="Latitude 1:")
        self.lat1_label.pack(pady=(10, 5))
        self.lat1_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter latitude 1")
        self.lat1_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Longitude 1
        self.long1_label = ctk.CTkLabel(self.main_frame, text="Longitude 1:")
        self.long1_label.pack(pady=(10, 5))
        self.long1_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter longitude 1")
        self.long1_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Latitude 2
        self.lat2_label = ctk.CTkLabel(self.main_frame, text="Latitude 2:")
        self.lat2_label.pack(pady=(10, 5))
        self.lat2_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter latitude 2")
        self.lat2_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Longitude 2
        self.long2_label = ctk.CTkLabel(self.main_frame, text="Longitude 2:")
        self.long2_label.pack(pady=(10, 5))
        self.long2_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter longitude 2")
        self.long2_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Altitude
        self.alt_label = ctk.CTkLabel(self.main_frame, text="Altitude:")
        self.alt_label.pack(pady=(10, 5))
        self.alt_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter altitude")
        self.alt_entry.pack(pady=(0, 10), padx=20, fill="x")
    
    def load_current_values(self):
        """Load current global values into entry fields"""
        global lat1, long1, lat2, long2, alt
        
        self.lat1_entry.insert(0, str(lat1))
        self.long1_entry.insert(0, str(long1))
        self.lat2_entry.insert(0, str(lat2))
        self.long2_entry.insert(0, str(long2))
        self.alt_entry.insert(0, str(alt))
    
    def update_globals(self):
        """Update global variables with values from entry fields"""
        global lat1, long1, lat2, long2, alt
        
        try:
            lat1 = float(self.lat1_entry.get())
            long1 = float(self.long1_entry.get())
            lat2 = float(self.lat2_entry.get())
            long2 = float(self.long2_entry.get())
            alt = float(self.alt_entry.get())
            
            # Show success message and close window
            self.show_message("Success!", "Variables updated successfully!")
            self.window.after(1500, self.window.destroy)  # Close after 1.5 seconds
            
        except ValueError:
            self.show_message("Error!", "Please enter valid numeric values for all fields.")
    
    def show_message(self, title, message):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(title)
        dialog.geometry("250x150")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Message label
        msg_label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=12))
        msg_label.pack(pady=20, padx=20)
        
        # OK button
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)

class MainApp:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Main Application")
        self.root.geometry("300x200")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Coordinate Manager", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=30)
        
        # Open coordinates button
        self.open_coords_button = ctk.CTkButton(
            self.main_frame,
            text="Edit Coordinates",
            command=self.open_coordinate_editor,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200
        )
        self.open_coords_button.pack(pady=20)
        
        # Display current values button
        self.display_button = ctk.CTkButton(
            self.main_frame,
            text="Show Current Values",
            command=self.display_values,
            font=ctk.CTkFont(size=14),
            height=40,
            width=200
        )
        self.display_button.pack(pady=10)
    
    def open_coordinate_editor(self):
        """Open the coordinate editor window"""
        CoordinateEditorWindow(self.root)
    
    def display_values(self):
        """Display current global variable values"""
        global lat1, long1, lat2, long2, alt
        
        values_text = f"""Current Values:
        
Latitude 1: {lat1}
Longitude 1: {long1}
Latitude 2: {lat2}
Longitude 2: {long2}
Altitude: {alt}"""
        
        self.show_message("Current Values", values_text)
    
    def show_message(self, title, message):
        """Show a message dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        
        # Center the dialog on the main window
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Message label
        msg_label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=12))
        msg_label.pack(pady=20, padx=20)
        
        # OK button
        ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Function to create and run the app
def create_coordinate_app():
    """Create and run the coordinate manager application"""
    app = MainApp()
    app.run()

# Run the app if this script is executed directly
if __name__ == "__main__":
    create_coordinate_app()