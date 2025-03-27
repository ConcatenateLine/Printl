import flet as ft
import subprocess
import os
import signal
import time

from flet.utils.files import shutil

class ServiceManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.server_process = None
        self.is_running = False

    def create_view(self):
        return ft.View(
            "/service",
            [
                ft.AppBar(
                    title=ft.Text("Service Manager"),
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/printers")
                    )
                ),
                ft.Column(
                    [
                        ft.Text("Server Status", size=20),
                        ft.Text("Stopped", size=16, color=ft.Colors.RED),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Start Server",
                                    icon=ft.Icons.PLAY_ARROW,
                                    on_click=self.start_server,
                                ),
                                ft.ElevatedButton(
                                    "Stop Server",
                                    icon=ft.Icons.STOP,
                                    on_click=self.stop_server,
                                    disabled=True
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Text("Server Logs", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            ft.Text(""),
                            height=200,
                            padding=10,
                            bgcolor=ft.Colors.SURFACE,
                            border_radius=10,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ]
        )

    # def start_server(self, e):
    #     if not self.is_running:
    #         self.server_process = subprocess.Popen(
    #             ["python", "-m", "uvicorn", "api.server:printserver", "--host", "0.0.0.0", "--port", "9417"],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.STDOUT,
    #             text=True
    #         )
    #         self.is_running = True
    #         self.update_ui()
    #         self.update_logs()
    
    #    def add_printer(self, e):
    #     # TODO: Implement printer addition dialog
    #     self.page.open(
    #         ft.SnackBar(
    #             ft.Text("Add printer feature coming soon!"),
    #             action="OK",
    #         )
    #     )
        
    def start_server(self, e):
        if self.is_running:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Server is already running"),
                    action="OK",
                    bgcolor=ft.Colors.AMBER
                )
            )
            return

        try:
            # Check if Python is in PATH
            python_path = shutil.which("python")
            if not python_path:
                raise FileNotFoundError("Python executable not found in PATH")

            # Start the server
            self.server_process = subprocess.Popen(
                [python_path, "-m", "uvicorn", "src.api.server:printserver", "--host", "0.0.0.0", "--port", "9417"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # For Windows
            )

            # Wait a moment to check if the server started successfully
            time.sleep(1)
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                error_msg = stderr.strip() if stderr else stdout.strip()
                print(f"Server failed to start with exit code {self.server_process.poll()}\nError: {error_msg}")
                
                raise RuntimeError(f"Server failed to start with exit code {self.server_process.poll()}\nError: {error_msg}")
            
                   # Verify server is running
            try:
                import requests
                response = requests.get("http://127.0.0.1:9417/api/print")
                if response.status_code != 200:
                    raise RuntimeError(f"Server started but health check failed: {response.text}")
            except Exception as e:
                self.server_process.terminate()
                raise RuntimeError(f"Server started but failed health check: {str(e)}")


            self.is_running = True
            self.update_ui()
            self.update_logs()
            self.page.open(
                ft.SnackBar(
                    ft.Text("Server started successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )

        except FileNotFoundError as e:
            self.page.open(
                ft.SnackBar(
                    ft.Text(f"Error: {str(e)}"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )
        except Exception as e:
            self.page.open(
                ft.SnackBar(
                    ft.Text(f"Failed to start server: {str(e)}"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )

    def stop_server(self, e):
        if self.is_running:
            try:
                os.kill(self.server_process.pid, signal.SIGTERM)
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.kill(self.server_process.pid, signal.SIGKILL)
            self.server_process = None
            self.is_running = False
            self.update_ui()

    def update_logs(self):
        if self.server_process and self.is_running:
            while True:
                line = self.server_process.stdout.readline()
                if not line:
                    break
                logs = self.page.get_control("logs_text")
                logs.value += line
                logs.update()
                time.sleep(0.1)

    def update_ui(self):
        status = self.page.get_control("status_text")
        start_button = self.page.get_control("start_button")
        stop_button = self.page.get_control("stop_button")

        if self.is_running:
            status.value = "Running"
            status.color = ft.Colors.GREEN
            start_button.disabled = True
            stop_button.disabled = False
        else:
            status.value = "Stopped"
            status.color = ft.Colors.RED
            start_button.disabled = False
            stop_button.disabled = True

        status.update()
        start_button.update()
        stop_button.update()