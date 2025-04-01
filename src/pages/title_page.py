import flet as ft
from state.state import AppState


class TitlePage:
    page: ft.Page | None = None
    state: AppState | None = None
    state_controls = {}

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = page.session.get("state")

        self.state.add_event_handler(
            'server_status_changed', self.update_ui, "server_status_changed_title")

    def create_view(self):
        self.state_controls['container1'] = ft.Container(
            content=ft.Text(
                "Welcome to the Printl! " +
                ("Server is running" if self.state.is_server_running else "Server is not running"),
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=5,
            bgcolor=ft.Colors.GREEN if self.state.is_server_running else ft.Colors.RED,
            border_radius=30
        )
        self.state_controls['url_row'] = ft.Row(
            [
                ft.Text("Server URL:", size=20,
                        weight=ft.FontWeight.BOLD),
                ft.Text(f"{self.state.url}", size=20,
                        weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.state_controls['printers_button'] = ft.ElevatedButton(
            "Go to Printers Page",
            on_click=lambda _: self.page.go("/printers"),
            width=300,
            visible=self.state.is_server_running
        )
        self.state_controls['domains_button'] = ft.ElevatedButton(
            "Go to Domains Page",
            on_click=lambda _: self.page.go("/domains"),
            width=300,
            visible=self.state.is_server_running
        )

        return ft.View("/title",
                       [
                           ft.AppBar(
                               title=ft.Text("Printl: Printl")),
                           ft.Divider(),
                           ft.Row(
                               [
                                   ft.Image("src/assets/icon.png",
                                            cache_height=150, cache_width=150),
                               ],
                               alignment=ft.MainAxisAlignment.CENTER,
                           ),
                           ft.Column(
                               [
                                   self.state_controls['container1'],
                                   ft.Divider(),
                                   self.state_controls['url_row'],
                                   ft.ElevatedButton(
                                       "Go to Info Page",
                                       on_click=lambda _: self.page.go(
                                           "/info"),
                                       width=300
                                   )
                               ],
                               spacing=10,
                               alignment=ft.MainAxisAlignment.CENTER
                           ),
                           ft.Column(
                               [
                                   self.state_controls['printers_button'],
                                   self.state_controls['domains_button']
                               ],
                               spacing=10
                           ),
                           ft.ElevatedButton(
                               "Go to Service Manager",
                               on_click=lambda _: self.page.go("/service"),
                               width=300
                           )
                       ]
                       )

    def update_ui(self, *args, **kwargs):
        if not self.page.route == "/title":
            return
        
        container1 = self.page.get_control(
            self.state_controls['container1'].uid)
        if container1:
            container1.bgcolor = ft.Colors.GREEN if self.state.is_server_running else ft.Colors.RED
            container1.update()

        printers_button = self.page.get_control(
            self.state_controls['printers_button'].uid)
        if printers_button:
            printers_button.visible = self.state.is_server_running
            printers_button.update()

        domains_button = self.page.get_control(
            self.state_controls['domains_button'].uid)
        if domains_button:
            domains_button.visible = self.state.is_server_running
            domains_button.update()
