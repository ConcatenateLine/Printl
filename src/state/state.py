from dataclasses import dataclass, field
from typing import Optional, Dict, Callable, Tuple, Any
import subprocess
import requests
from flet.utils.files import shutil
import time
import threading
import queue
import uuid

@dataclass
class AppState:
    url: str = "http://127.0.0.1:9417"
    _is_server_running: bool = False
    _server_process: Optional[subprocess.Popen] = None
    domains: list = field(default_factory=list)
    printers: list = field(default_factory=list)
    selected_printer: Optional[dict] = None
    server_logs: list = field(default_factory=list)
    errors: dict = field(default_factory=dict)
    _log_queue: queue.Queue = field(default_factory=queue.Queue)
    _log_thread: Optional[threading.Thread] = None
    _event_handlers: Dict[str, Dict[str, Callable]] = field(default_factory=dict)
    
    def add_event_handler(self, event_name: str, handler: Callable, handler_id: str = None) -> str:
        """Add an event handler for a specific event with a unique ID
        
        Args:
            event_name: The name of the event
            handler: The function to call when the event is triggered
            handler_id: Optional custom ID for the handler. If not provided, a UUID will be generated
            
        Returns:
            str: The unique ID assigned to this handler
        """
        if handler_id is None:
            handler_id = str(uuid.uuid4())
            
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = {}
        
        self._event_handlers[event_name][handler_id] = handler
        return handler_id
    
    def remove_event_handler(self, event_name: str, handler_id: str):
        """Remove an event handler for a specific event using its ID
        
        Args:
            event_name: The name of the event
            handler_id: The ID of the handler to remove
        """
        if event_name in self._event_handlers:
            if handler_id in self._event_handlers[event_name]:
                del self._event_handlers[event_name][handler_id]
                if not self._event_handlers[event_name]:  # If no more handlers for this event
                    del self._event_handlers[event_name]
    
    def get_event_handler_id(self, event_name: str, handler: Callable) -> Optional[str]:
        """Get the ID of an existing handler for an event
        
        Args:
            event_name: The name of the event
            handler: The handler function to find
            
        Returns:
            str: The ID of the handler if found, None otherwise
        """
        if event_name in self._event_handlers:
            for handler_id, existing_handler in self._event_handlers[event_name].items():
                if existing_handler == handler:
                    return handler_id
        return None
    
    def _trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger an event with optional arguments"""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name].values():
                handler(*args, **kwargs)
    
    def _log_worker(self):
        while True:
            try:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                self.server_logs.append(str(line))
                self._log_queue.put(str(line))
                self._trigger_event('log_updated', str(line))
            except Exception as e:
                print(f"Error in log worker: {str(e)}")
                break

    def start_log_thread(self):
        if self.server_process and not self._log_thread:
            self._log_thread = threading.Thread(target=self._log_worker, daemon=True)
            self._log_thread.start()

    def stop_log_thread(self):
        if self._log_thread:
            self._log_thread = None
            self._log_queue.put(None)  # Signal the thread to stop

    def get_log(self, block=True, timeout=None):
        """Get a log line from the queue"""
        try:
            return self._log_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    @property
    def is_server_running(self) -> bool:
        return self._is_server_running
    
    @is_server_running.setter
    def is_server_running(self, value: bool):
        old_value = self._is_server_running
        self._is_server_running = value
        if value != old_value:
            self._trigger_event('server_status_changed', value)
    
    @property
    def server_process(self) -> Optional[subprocess.Popen]:
        return self._server_process
    
    @server_process.setter
    def server_process(self, value: Optional[subprocess.Popen]):
        old_value = self._server_process
        self._server_process = value
        if value != old_value:
            self._trigger_event('server_process_changed', value)
                
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
        
    def start_server(self):
        if self.is_server_running:
            print("Server is already running")
            return False
        
        try:
            python_path = shutil.which("python")
            if not python_path:
                raise FileNotFoundError("Python executable not found in PATH")

            self.server_process = subprocess.Popen(
                [python_path, "-m", "uvicorn", "src.api.server:printserver",
                    "--host", "0.0.0.0", "--port", "9417"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # For Windows
            )

            time.sleep(1)
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                error_msg = stderr.strip() if stderr else stdout.strip()
                print(
                    f"Server failed to start with exit code {self.server_process.poll()}\nError: {error_msg}")

                raise RuntimeError(
                    f"Server failed to start with exit code {self.server_process.poll()}\nError: {error_msg}")
                
            # Verify server is running
            try:
                import requests
                response = requests.get("http://127.0.0.1:9417/api/version")
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Server started but health check failed: {response.text}")
            except Exception as e:
                self.server_process.terminate()
                self.is_server_running = False
                raise RuntimeError(
                    f"Server started but failed health check: {str(e)}")

            self.is_server_running = True
            print("Server started successfully")
            self.start_log_thread()
            return True

        except FileNotFoundError as e:
            raise RuntimeError(f"Error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to start server: {str(e)}")
            
    def stop_server(self):
        if self.is_server_running:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("Server stopped successfully")
            except subprocess.TimeoutExpired:
                print("Failed to stop server")
                return False
            
            self.server_process = None
            self.is_server_running = False
            self.stop_log_thread()
            return True
        else:
            raise RuntimeError("Server is not running")