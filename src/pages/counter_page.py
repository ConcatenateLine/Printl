import flet as ft

class CounterPage(ft.View):
    counter = ft.Text("0", size=50, data=0)
    
    def __init__(self, page):
        super().__init__("/counter", [])
        self.page = page
        self.controls.append(
            ft.Column(
                controls=[
                    ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        on_click=self.increment_click
                    ),
                    ft.Container(
                        self.counter,
                        alignment=ft.alignment.center,
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "Go to Title Page",
                        on_click=lambda _: self.page.go("/title")
                    )
                ]
            )
        )

    def increment_click(self, e):
        self.counter.data += 1
        self.counter.value = str(self.counter.data)
        self.counter.update()
