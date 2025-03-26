import flet as ft
import requests

class PrintersPage:
    selected_printer = None
    printers = [
        {'name': 'printer 1', 'status': 'Online', 'jobs': 0, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        {'name': 'printer 2', 'status': 'Offline', 'jobs': 3, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        {'name': 'printer 3', 'status': 'Online', 'jobs': 1, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        {'name': 'printer 4', 'status': 'Online', 'jobs': 2, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        {'name': 'printer 5', 'status': 'Offline', 'jobs': 0, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        {'name': 'printer 6', 'status': 'Online', 'jobs': 0, 'queue_size': 0, 'port': 'unavailable', 'driver': 'unavailable'},
        ]
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.printers = self.get_system_printers()
        
    def get_system_printers(self):
        try:
            response = requests.get("http://127.0.0.1:9417/api/printers")  # Replace 'your-endpoint' with your API route
            if response.status_code == 200:
                data = response.json()
                print("Data from API:", data)
                
                self.selected_printer = data['default_printer']
                return data['printers']
            else:
                print("Failed to fetch data:", response.status_code)
                return []
        except Exception as e:
            print(f"Error getting printers: {str(e)}")
            return []

    def load_selected_printer(self):
        """Load the selected printer from storage"""
        printer_name = self.page.client_storage.get("selected_printer")
        if printer_name:
            # Find the printer with the matching name
            self.selected_printer = next((p for p in self.printers if p["name"] == printer_name), None)
            self.page.update()
            
    def select_printer(self, printer):
        """Select a printer and update the UI"""
        self.selected_printer = printer
        
        response = requests.post("http://127.0.0.1:9417/api/printers/", json={"name": printer["name"], "value": printer["name"]})

        if response.status_code != 200:
            print(f"Failed to update default printer: {response.status_code}")
            return
        
        # Store the selected printer's name
        self.page.client_storage.set("selected_printer", printer["name"])
        self.page.update()

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
                        ft.Text(printer["name"], size=20, weight=ft.FontWeight.BOLD),
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
                                ft.Text(f"Queue: {printer['queue_size']} pages", 
                                        color=ft.Colors.BLUE,
                                        weight=ft.FontWeight.BOLD),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Text(f"Port: {printer['port']}", 
                                        color=ft.Colors.GREY,
                                        weight=ft.FontWeight.NORMAL),
                                ft.Text(f"Driver: {printer['driver']}", 
                                        color=ft.Colors.GREY,
                                        weight=ft.FontWeight.NORMAL),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.ElevatedButton(
                            "Select",
                            on_click=lambda e: self.select_printer(printer)
                        )
                    ],
                    spacing=10,
                ),
                padding=10,
            ),
            elevation=4,
        )

    def create_view(self):
        return ft.View(
            "/printers",
            [
                ft.AppBar(
                    title=ft.Text("Printers"),
                    actions=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh printers list",
                            on_click=self.refresh_printers,
                        )
                    ]
                ),
                ft.Container(
                    content=ft.GridView(
                        controls=[
                            self.create_printer_card(printer)
                            for printer in self.printers
                        ],
                        spacing=10,
                        run_spacing=10,
                        max_extent=200,
                    ),
                    padding=10,
                    expand=True,
                ),
                ft.ElevatedButton(
                    "Go to Title Page",
                    on_click=lambda _: self.page.go("/title")
                ),
                ft.Text(f"Selected Printer: {self.selected_printer['value'] if self.selected_printer else 'None'}")
            ]
        )

    def refresh_printers(self, e=None):
        try:
            self.printers = self.get_system_printers()
            self.page.update()
        except Exception as e:
            print(f"Error refreshing printers: {str(e)}")