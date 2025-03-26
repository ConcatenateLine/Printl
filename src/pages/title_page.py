import flet as ft

class TitlePage(ft.View):
    def __init__(self, page):
        super().__init__(
            "/title",
            [
                ft.AppBar(title=ft.Text("Title Printl")),
                ft.Container(
                    content=ft.Text(
                        "Welcome to the Title Page printl!",
                        size=30,
                        weight=ft.FontWeight.BOLD
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                ),
                ft.ElevatedButton(
                    "Go to Counter Page",
                    on_click=lambda _: page.go("/counter")
                ),
                ft.ElevatedButton(
                    "Go to Printers Page",
                    on_click=lambda _: page.go("/printers")
                )
            ]
        )