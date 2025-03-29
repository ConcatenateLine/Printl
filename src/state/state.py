from dataclasses import dataclass, field
from typing import Optional
import subprocess
import requests

@dataclass
class AppState:
    url: str = "http://127.0.0.1:9417"
    is_server_running: bool = False
    server_process: Optional[subprocess.Popen] = None
    printers: list = field(default_factory=list)
    selected_printer: Optional[dict] = None
    server_logs: list = field(default_factory=list)
    errors: dict = field(default_factory=dict)
    
    def update(self, **kwargs):
        """Update multiple state properties at once"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    def get_printers(self):
        try:
            response = requests.get(f"{self.url}/api/printers")
            if response.status_code == 200:
                data = response.json()
                self.selected_printer = data['default_printer']
                self.printers = data['printers']
                return True
            else:
                self.errors['get_printers'] = f"Failed to fetch data: {response.status_code}"
                print("Failed to fetch data:", response.status_code)
                return False
        except Exception as e:
            self.errors['get_printers'] = str(e)
            print(f"Error getting printers: {str(e)}")
            return False
        
    def update_printer_public(self, printer: dict):
        try:
            response = requests.post(f"{self.url}/api/printers/public/", json={
                "id": printer["id"],
                "name": printer["name"],
                "isPublic": not printer["isPublic"]
            })
            if response.status_code != 200:
                self.errors['update_printer_public'] = f"Failed to update printer: {response.status_code}"
                print(f"Failed to update printer: {response.status_code}")
                return False
            return True
        except Exception as e:
            self.errors['update_printer_public'] = str(e)
            print(f"Error updating printer: {str(e)}")
            return False
    
    def update_default_printer(self, printer: dict):
        try:
            response = requests.post(f"{self.url}/api/printers/", json={"name": printer["name"], "value": printer["name"]})
            
            if response.status_code != 200:
                self.errors['update_default_printer'] = f"Failed to update printer: {response.status_code}"
                print(f"Failed to update printer: {response.status_code}")
                return False
            return True
        except Exception as e:
            self.errors['update_default_printer'] = str(e)
            print(f"Error updating printer: {str(e)}")
            return False