from dataclasses import dataclass
from typing import Optional

@dataclass
class AppState:
    is_server_running: bool = False
    server_process: Optional[subprocess.Popen] = None
    printers: list = None
    selected_printer: Optional[dict] = None
    logs: list = []
    current_view: str = "title"
    
    def update(self, **kwargs):
        """Update multiple state properties at once"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)