import tkinter as tk
from tkinter import messagebox
from utils.licensing import verify_license

class LicensePrompt(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileMaster - Activation Required")
        self.geometry("400x200")
        self.resizable(False, False)
        
        tk.Label(self, text="Please enter your Lifetime License Key:", pady=20).pack()
        
        self.key_entry = tk.Entry(self, width=50)
        self.key_entry.pack(pady=5)
        
        tk.Button(self, text="Activate", command=self._handle_activation).pack(pady=20)
        
    def _handle_activation(self):
        key = self.key_entry.get().strip()
        if not key:
            messagebox.showwarning("Warning", "License key cannot be empty.")
            return
            
        if verify_license(key):
            messagebox.showinfo("Success", "Activation successful! Restarting app.")
            self.destroy()
            self.activated = True
        else:
            messagebox.showerror("Error", "Invalid license key or machine mismatch.")

    def run(self):
        self.activated = False
        self.mainloop()
        return self.activated
