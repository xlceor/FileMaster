
from ui.app import FileCheckerApp
from ui.license_prompt import LicensePrompt
from utils.licensing import check_local_lease

if __name__ == "__main__":
    if not check_local_lease():
        prompt = LicensePrompt()
        if not prompt.run():
            exit("Application not activated.")
            
    app = FileCheckerApp()
    app.mainloop()
