import flet as ft
import subprocess
import time

from flet.utils.files import shutil

from state.state import AppState

class ServiceManager:
    page: ft.Page | None = None
    state: AppState | None = None
    controls = {}

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = self.page.session.get("state")

    def create_view(self):
        if self.state.is_server_running:
            self.controls['server_status'] = ft.Text("Running", size=16, color=ft.Colors.GREEN)
            self.controls['start_button'] = ft.ElevatedButton(
                "Start Server",
                icon=ft.Icons.PLAY_ARROW,
                on_click=self.start_server,
                disabled=True,
                key="start_button"
            )
            self.controls['stop_button'] = ft.ElevatedButton(
                "Stop Server",
                icon=ft.Icons.STOP,
                on_click=self.stop_server,
                key="stop_button"
            )
            self.controls['logs_text'] = ft.ListView(expand=1,
                                                    spacing=10,
                                                    auto_scroll=True,
                                                    controls=[
                                                        ft.Text(log) for log in self.state.server_logs
                                                    ])
            
        else:
            self.controls['server_status'] = ft.Text("Stopped", size=16, color=ft.Colors.RED)
            self.controls['start_button'] = ft.ElevatedButton(
                "Start Server",
                icon=ft.Icons.PLAY_ARROW,
                on_click=self.start_server,
                key="start_button"
            )
            self.controls['stop_button'] = ft.ElevatedButton(
                "Stop Server",
                icon=ft.Icons.STOP,
                on_click=self.stop_server,
                disabled=True,
                key="stop_button"
            )
            self.controls['logs_text'] = ft.ListView(expand=1, spacing=10, auto_scroll=True, controls=[])
        
        return ft.View(
            "/service",
            [
                ft.AppBar(
                    title=ft.Text("Service Manager"),
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/title")
                    )
                ),
                ft.Column(
                    [
                        self.controls['server_status'],
                        ft.Row(
                            [
                                self.controls['start_button'],
                                self.controls['stop_button']
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Text("Server Logs", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.controls['logs_text'],
                            height=440,
                            padding=5,
                            bgcolor=ft.Colors.SURFACE,
                            border_radius=10,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10
                )
            ]
        )
        
    def start_server(self, e):
        if self.state.is_server_running:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Server is already running"),
                    action="OK",
                    bgcolor=ft.Colors.AMBER
                )
            )
            return

        try:
            python_path = shutil.which("python")
            if not python_path:
                raise FileNotFoundError("Python executable not found in PATH")

            self.state.server_process = subprocess.Popen(
                [python_path, "-m", "uvicorn", "src.api.server:printserver",
                    "--host", "0.0.0.0", "--port", "9417"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # For Windows
            )

            time.sleep(1)
            if self.state.server_process.poll() is not None:
                stdout, stderr = self.state.server_process.communicate()
                error_msg = stderr.strip() if stderr else stdout.strip()
                print(
                    f"Server failed to start with exit code {self.state.server_process.poll()}\nError: {error_msg}")

                raise RuntimeError(
                    f"Server failed to start with exit code {self.state.server_process.poll()}\nError: {error_msg}")

            # Verify server is running
            try:
                import requests
                response = requests.get("http://127.0.0.1:9417/api/print")
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Server started but health check failed: {response.text}")
            except Exception as e:
                self.state.server_process.terminate()
                raise RuntimeError(
                    f"Server started but failed health check: {str(e)}")

            self.state.is_server_running = True
            self.update_ui()
            self.page.open(
                ft.SnackBar(
                    ft.Text("Server started successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )
            self.update_logs()
            

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
        if self.state.is_server_running:
            try:
                self.state.server_process.terminate()
                self.state.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                raise RuntimeError("Failed to stop server")
            
            self.state.server_process = None
            self.state.is_server_running = False
            self.update_ui()

    def update_logs(self):
        if self.state.server_process and self.state.is_server_running:
            while True:
                line = self.state.server_process.stdout.readline()
                if not line:
                    break
                self.state.server_logs.append(str(line))
                logs = self.page.get_control(self.controls['logs_text'].uid)
                if logs:
                    logs.controls.append(ft.Text(str(line)))
                    logs.update()
                time.sleep(0.1)

    def update_ui(self):
        status = self.page.get_control(self.controls['server_status'].uid)
        start_button = self.page.get_control(self.controls['start_button'].uid)
        stop_button = self.page.get_control(self.controls['stop_button'].uid)

        if self.state.is_server_running:
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
    