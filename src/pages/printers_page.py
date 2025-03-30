import flet as ft
from state.state import AppState


class PrintersPage:
    page: ft.Page | None = None
    state: AppState | None = None
    controls = {}

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = self.page.session.get("state")
        self.state.get_printers()

    def select_printer(self, printer):
        self.state.selected_printer = printer

        try:
            response = self.state.update_default_printer(printer)

            if not response:
                print(f"Failed to update default printer")
                return

            self.refresh_printers()
            
            self.page.open(
                ft.SnackBar(
                    ft.Text("Printer selected successfully (Public printer)"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )
        except Exception as e:
            print(f"Error selecting printer: {str(e)}")
            self.page.open(
                ft.SnackBar(
                    ft.Text("Failed to select printer"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )

    def checkbox_changed(self, printer):
        try:
            response = self.state.update_printer_public(printer)

            if not response:
                print(f"Failed to update printer")
                return

            self.refresh_printers()
            
            self.page.open(
                ft.SnackBar(
                    ft.Text("Printer updated successfully"),
                    action="OK",
                    bgcolor=ft.Colors.GREEN
                )
            )
        except Exception as e:
            print(f"Error updating printer: {str(e)}")
            self.page.open(
                ft.SnackBar(
                    ft.Text("Failed to update printer"),
                    action="OK",
                    bgcolor=ft.Colors.RED
                )
            )
    
    def create_printer_card(self, printer):
        status_color = {
            "Online": ft.Colors.GREEN,
            "Offline": ft.Colors.RED,
            "Paused": ft.Colors.YELLOW,
            "Error": ft.Colors.RED,
            "Not Available": ft.Colors.GREY,
            "Paper Jam": ft.Colors.ORANGE,
            "Low Memory": ft.Colors.YELLOW,
            "Out of Paper": ft.Colors.YELLOW,
            "Output Bin Full": ft.Colors.YELLOW,
            "Door Open": ft.Colors.YELLOW,
        }

        # Determine color based on most critical status
        status_parts = printer["status"].split("/")
        status_color = next((color for status, color in status_color.items()
                             if any(s in status_parts for s in status)), ft.Colors.GREEN)

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(printer["name"], size=20,
                                weight=ft.FontWeight.BOLD),
                        ft.Row(
                            [
                                ft.Text(f"Status: {printer['status']}",
                                        color=status_color,
                                        weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(f"Jobs: {printer['jobs']}",
                                        color=ft.Colors.BLUE,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(f"Port: {printer['port']}",
                                        color=ft.Colors.GREY,
                                        weight=ft.FontWeight.NORMAL),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(f"Queue: {printer['queue_size']} pages",
                                        color=ft.Colors.BLUE,
                                        weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Set Default",
                                    on_click=lambda e: self.select_printer(printer),
                                    visible=not self.state.selected_printer or self.state.selected_printer['value'] != printer['name']
                                ),
                                ft.Checkbox(
                                    label="Public",
                                    value=printer["isPublic"],
                                    on_change=lambda e: self.checkbox_changed(printer),
                                    visible=not self.state.selected_printer or self.state.selected_printer['value'] != printer['name']
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                    ],
                    spacing=10,
                ),
                padding=5,
                expand=True,
                border=ft.border.all(2 if self.state.selected_printer and self.state.selected_printer['value'] == printer['name'] else 0, ft.Colors.ORANGE if self.state.selected_printer and self.state.selected_printer['value'] == printer['name'] else ft.Colors.TRANSPARENT),
            ),
            elevation=4,
        )

    def create_view(self):
        self.controls['refresh_button'] = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh printers list",
            on_click=self.refresh_printers,
            data={"loading": False}
        )
        self.controls['printers_grid'] = ft.GridView(
            controls=[
                self.create_printer_card(printer)
                for printer in self.state.printers
            ],
            spacing=5,
            run_spacing=5,
            max_extent=300,
            adaptive=True,
            child_aspect_ratio=1.0,
            expand=True
        )
        self.controls['selected_printer'] = ft.Text(
            f"Default Printer: {self.state.selected_printer['value'] if self.state.selected_printer else 'None'}",
        )

        return ft.View(
            "/printers",
            [
                ft.AppBar(
                    title=ft.Text("Printers"),
                    leading=ft.IconButton(
                        ft.Icons.ARROW_BACK,
                        on_click=lambda _: self.page.go("/title")
                    )
                ),
                ft.Container(
                    content=self.controls['printers_grid'],
                    padding=10,
                    expand=True,
                ),
                ft.Row(
                    [
                        self.controls['refresh_button'],
                        self.controls['selected_printer']
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ]
        )

    def refresh_printers(self, e=None):
        try:
            get_printers_result = self.state.get_printers()

            if not get_printers_result:
                self.page.open(
                    ft.SnackBar(
                        ft.Text("Failed to fetch printers"),
                        action="OK",
                        bgcolor=ft.Colors.RED
                    )
                )
            else:
                grid_control = self.page.get_control(self.controls['printers_grid'].uid)
                selected_printer = self.page.get_control(self.controls['selected_printer'].uid)
                grid_control.controls = [
                    self.create_printer_card(printer)
                    for printer in self.state.printers
                ]
                selected_printer.value = f"Default Printer: {self.state.selected_printer['value'] if self.state.selected_printer else 'None'}"

                selected_printer.update()
                grid_control.update()
                print("Printers fetched successfully")

        except Exception as e:
            print(f"Error refreshing printers: {str(e)}")
