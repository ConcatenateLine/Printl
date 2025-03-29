import flet as ft
from state.state import AppState

class TitlePage(ft.View):
    state: AppState | None = None
    
    def __init__(self, page):
        self.state = page.session.get("state")
        
        super().__init__(
            "/title",
            [
                ft.AppBar(title=ft.Text("Printl: Printl")),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Image("src/assets/icon.png", cache_height=150, cache_width=150),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Text(
                        "Welcome to the Printl! " + ("Server is running" if self.state.is_server_running else "Server is not running"),
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=5,
                    bgcolor=ft.Colors.GREEN if self.state.is_server_running else ft.Colors.RED,
                    border_radius=30
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Text("Server URL:", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{self.state.url}", size=20, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [
                        ft.Text("Default Printer:", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{self.state.selected_printer['value'] if self.state.selected_printer else 'Not Set'}", size=20, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.ElevatedButton(
                    "Go to Info Page",
                    on_click=lambda _: page.go("/info"),
                    width=300
                ),
                ft.ElevatedButton(
                    "Go to Printers Page",
                    on_click=lambda _: page.go("/printers"),
                    width=300
                ),
                ft.ElevatedButton(
                    "Go to Service Manager",
                    on_click=lambda _: self.page.go("/service"),
                    width=300
                ),
            ]
        )