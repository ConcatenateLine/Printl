import flet as ft
from state.state import AppState


class DomainsPage:
    state: AppState | None = None
    page: ft.Page | None = None
    controls = {}

    def __init__(self, page: ft.Page):
        self.state = page.session.get("state")
        self.page = page
        self.state.get_domains()

    def add_domain(self, domain: str):
        if not domain:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Please enter a domain"),
                    action="OK",
                    bgcolor=ft.Colors.AMBER
                )
            )
            return

        response = self.state.add_domain(domain)
        if not response:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Failed to add domain"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )
        else:
            input_domain = self.page.get_control(
                self.controls['domain_input'].uid)
            input_domain.value = ""
            input_domain.update()

            self.page.open(
                ft.SnackBar(
                    ft.Text("Domain added successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )

        self.get_domains()

    def get_domains(self):
        response = self.state.get_domains()

        if not response:
            self.page.add(ft.Text("Failed to get domains"))

        domains = self.page.get_control(self.controls['domains'].uid)
        domains.controls = [self.generate_domain(domain)
                            for domain in self.state.domains]
        domains.update()

    def delete_domain(self, domain: str):
        response = self.state.delete_domain(domain)
        if not response:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Failed to delete domain"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )
        else:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Domain deleted successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )

        self.get_domains()

    def update_domain(self, domain: str, value: bool):
        status = "Active" if value == 'true' else "Inactive"

        response = self.state.update_domain(domain, status)
        if not response:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Failed to update domain"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )
        else:
            self.page.open(
                ft.SnackBar(
                    ft.Text("Domain updated successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )

        self.get_domains()

    def generate_domain(self, domain: dict):
        return ft.Row(
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(domain['domain']),
                ft.Row(
                    [
                        ft.Checkbox(
                            label=domain['status'],
                            value=domain["status"] == "Active",
                            on_change=lambda e: self.update_domain(
                                domain['domain'], e.data),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE,
                            on_click=lambda _: self.delete_domain(
                                domain['domain'])
                        )
                    ]
                )
            ]
        )

    def create_view(self):
        self.controls['domain_input'] = ft.TextField(
            label="example.com",
        )
        self.controls['domains'] = ft.ListView(expand=1,
                                               spacing=10,
                                               auto_scroll=True,
                                               controls=[
                                                   self.generate_domain(domain) for domain in self.state.domains
                                               ])

        return ft.View(
            "/domains",
            [
                ft.AppBar(
                    title=ft.Text("Domains permissions"),
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/title")
                    )
                ),
                ft.Text("To add a new domain, enter the domain name and click 'Add Domain', this will add the domain to the list of domains that are allowed to access the server.", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        self.controls['domain_input'],
                        ft.ElevatedButton(
                            "Add Domain",
                            on_click=lambda _: self.add_domain(
                                self.controls['domain_input'].value)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Column(
                    expand=True,
                    spacing=10,
                    controls=[
                        ft.Text("Domains"),
                        ft.Container(
                            content=self.controls['domains'],
                            padding=10,
                            expand=True,
                        )
                    ]
                )
            ]
        )
