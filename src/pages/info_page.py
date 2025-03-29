import flet as ft

class InfoPage(ft.View):
    def __init__(self, page):
        super().__init__("/info", [])
        self.page = page
        
        # Create the content
        self.controls.extend([
            ft.AppBar(
                title=ft.Text("Printl - About"),
                leading=ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    on_click=lambda _: self.page.go("/title")
                )
            ),
            ft.Container(
                content=ft.ListView(
                    spacing=10,
                    expand=1,
                    controls=[
                        # Title Section
                        ft.Container(
                            content=ft.Text(
                                "Printl: Network Printer Management Application",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=10
                        ),
                        
                        # Description Section
                        ft.Container(
                            content=ft.Text(
                                "Printl is a desktop application designed to manage and expose local printers to the network. It provides a user-friendly interface for printer management and network printing capabilities.",
                                size=16,
                                text_align=ft.TextAlign.JUSTIFY
                            ),
                            padding=10
                        ),
                        
                        # Features Section
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Key Features", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text("Network Printer Management", weight=ft.FontWeight.BOLD),
                                    ft.Text("- Expose local printers to the network"),
                                    ft.Text("- Manage printer access permissions"),
                                    ft.Text("User Interface (Flet App)", weight=ft.FontWeight.BOLD),
                                    ft.Text("- UI for printer management"),
                                    ft.Text("- Intuitive printer selection and configuration"),
                                    ft.Text("- System tray integration for quick access"),
                                    ft.Text("Server Components (FastAPI)", weight=ft.FontWeight.BOLD),
                                    ft.Text("- RESTful API for printer management"),
                                    ft.Text("Printer Management", weight=ft.FontWeight.BOLD),
                                    ft.Text("- Set default printers"),
                                    ft.Text("- Manage printer permissions"),
                                    ft.Text("System Integration", weight=ft.FontWeight.BOLD),
                                    ft.Text("- System tray icon for quick access"),
                                    ft.Text("- Background server operation"),
                                    ft.Text("- Minimal system resource usage"),
                                    ft.Text("- Automatic printer discovery"),
                                ],
                                spacing=5
                            ),
                            padding=10
                        ),
                        
                        # Technical Architecture Section
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Technical Architecture", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text("- Frontend: Flet (Python GUI framework)"),
                                    ft.Text("- Backend: FastAPI (Python web framework)"),
                                    ft.Text("- Database: SQLite (for printer configurations)"),
                                    ft.Text("- System Integration: Windows system tray support"),
                                ],
                                spacing=5
                            ),
                            padding=10
                        ),
                        
                        # Back Button
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "Back to Home Page",
                                        on_click=lambda _: self.page.go("/title"),
                                        icon=ft.Icons.HOME
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            padding=10
                        )
                    ],
                ),
                padding=5,
                expand=True,
                height=440,
                bgcolor=ft.Colors.SURFACE,
                border_radius=10,
                
            )
        ])