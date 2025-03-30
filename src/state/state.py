from dataclasses import dataclass, field
from typing import Optional
import subprocess
import requests

@dataclass
class AppState:
    url: str = "http://127.0.0.1:9417"
    is_server_running: bool = False
    server_process: Optional[subprocess.Popen] = None
    domains: list = field(default_factory=list)
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
        
    def get_domains(self):
        try:
            response = requests.get(f"{self.url}/api/domains")
            if response.status_code == 200:
                data = response.json()
                self.domains = data['domains']
                return True
            else:
                self.errors['get_domains'] = f"Failed to fetch data: {response.status_code}"
                print("Failed to fetch data:", response.status_code)
                return False
        except Exception as e:
            self.errors['get_domains'] = str(e)
            print(f"Error getting domains: {str(e)}")
            return False

    def update_domain(self, domain: str, status: str):
        try:
            response = requests.put(f"{self.url}/api/domains/{domain}", json={"status": status})
            if response.status_code != 200:
                self.errors['update_domain'] = f"Failed to update domain: {response.status_code}"
                print(f"Failed to update domain: {response.status_code}")
                return False
            return True
        except Exception as e:
            self.errors['update_domain'] = str(e)
            print(f"Error updating domain: {str(e)}")
            return False
        
    def add_domain(self, domain: str):
        try:
            response = requests.post(f"{self.url}/api/domains", json={"domain": domain})
            if response.status_code != 200:
                self.errors['add_domain'] = f"Failed to add domain: {response.status_code}"
                print(f"Failed to add domain: {response.status_code}")
                return False
            return True
        except Exception as e:
            self.errors['add_domain'] = str(e)
            print(f"Error adding domain: {str(e)}")
            return False
        
    def delete_domain(self, domain: str):
        try:
            response = requests.delete(f"{self.url}/api/domains/{domain}")
            if response.status_code != 200:
                self.errors['delete_domain'] = f"Failed to delete domain: {response.status_code}"
                print(f"Failed to delete domain: {response.status_code}")
                return False
            return True
        except Exception as e:
            self.errors['delete_domain'] = str(e)
            print(f"Error deleting domain: {str(e)}")
            return False