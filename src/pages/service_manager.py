import flet as ft
import subprocess

from state.state import AppState

class ServiceManager:
    page: ft.Page | None = None
    state: AppState | None = None
    controls = {}
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = self.page.session.get("state")
        
        self.state.add_event_handler('log_updated', self.update_logs, "log_updated_service_manager")
        self.state.add_event_handler('server_status_changed', self.update_ui, "server_status_changed_service_manager")

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
            self.controls['logs_text'] = ft.ListView(expand=1, spacing=10, auto_scroll=True, controls=[],padding=5)
        
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
            result = self.state.start_server()

            if not result:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Failed to start server"),
                        action="OK",
                        bgcolor=ft.Colors.RED
                    )
                )
                return
            
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
        try:
            result = self.state.stop_server()
            self.update_logs()
            
            if not result:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Failed to stop server"),
                        action="OK",
                        bgcolor=ft.Colors.RED
                    )
                )
                return

            self.page.open(
                ft.SnackBar(
                    ft.Text("Server stopped successfully"),
                        action="OK",
                        bgcolor=ft.Colors.LIGHT_BLUE
                    )
                )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Failed to stop server")
            
        self.update_ui()

    def update_logs(self, *args, **kwargs):
        logs = self.page.get_control(self.controls['logs_text'].uid)
        if logs and args and len(args) > 0:
            logs.controls.append(ft.Text(str(args[0])))
            logs.update()

    def update_ui(self, *args, **kwargs):
        if not self.page.route == "/service":
            return
        
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