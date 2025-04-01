import flet as ft
import pystray
from PIL import Image
import threading

from state.state import AppState

class TrayIcon:
    page: ft.Page = None
    state: AppState = None
    logo = Image.open("src/assets/icon.png")
    confirm_dialog = None
    icon = None
    tray_thread = None

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = self.page.session.get("state")
        
        self.state.add_event_handler('server_status_changed', self.update_ui_tray, "server_status_changed_tray")

        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to exit this app?"),
            actions=[
                ft.ElevatedButton("Yes", on_click=self.yes_click),
                ft.OutlinedButton("Minimize to tray", on_click=self.no_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.icon = pystray.Icon("Printl", self.logo, "Printl", pystray.Menu(
            pystray.MenuItem('Server', pystray.Menu(
                pystray.MenuItem('Start server', self.on_click,
                                 visible=lambda item: not self.state.is_server_running),
                pystray.MenuItem('Stop server', self.on_click,
                                 visible=lambda item: self.state.is_server_running),
            )),
            pystray.MenuItem('Show', self.on_click),
            pystray.MenuItem('Hide', self.on_click),
            pystray.MenuItem('Quit', self.on_click)
        ))

        self.tray_thread = threading.Thread(target=self.run_tray)
        self.tray_thread.daemon = True
        self.tray_thread.start()

        page.window.on_event = self.on_window_close
        page.window.prevent_close = True

    def run_tray(self):
        self.icon.run()

    def yes_click(self, e):
        self.icon.stop()

        if self.state.is_server_running:
            self.state.server_process.terminate()
            self.state.server_process.wait(timeout=5)

        self.page.window.destroy()

    def no_click(self, e):
        self.page.close(self.confirm_dialog)
        self.page.window.minimized = True
        self.page.window.visible = False
        self.page.update()

    def update_ui_tray(self, *args, **kwargs):
        print("Updating tray icon...")
        self.icon.update_menu()
        self.page.update()

    def on_click(self, icon, item):
        if str(item) == 'Start server':
            self.state.start_server()
            icon.notify("Server started successfully")
        elif str(item) == 'Stop server':
            if self.state.is_server_running:
                self.state.stop_server()
                self.page.go("/service")
                icon.notify("Server stopped successfully")
        elif str(item) == 'Show':
            self.page.window.minimized = False
            self.page.window.visible = True
        elif str(item) == 'Hide':
            self.page.window.minimized = True
            self.page.window.visible = False
        elif str(item) == 'Quit':
            self.page.window.minimized = False
            self.page.window.visible = True
            self.page.window.close()

        self.update_ui_tray()

    def on_window_close(self, e):
        if e.data == 'close':
            self.page.open(self.confirm_dialog)
