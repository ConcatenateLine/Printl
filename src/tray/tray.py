import flet as ft
import pystray
from PIL import Image
import threading

def create_tray_icon(page: ft.Page):

    def yes_click(e):
        icon.stop()
        page.window.destroy()

    def no_click(e):
        page.close(confirm_dialog)
        page.window.minimized = True
        page.window.visible = False
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to exit this app?"),
        actions=[
            ft.ElevatedButton("Yes", on_click=yes_click),
            ft.OutlinedButton("Minimize to tray", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def on_click(icon, item):
        if str(item) == 'Show':
            page.window.minimized = False
            page.window.visible = True
        elif str(item) == 'Hide':
            page.window.minimized = True
            page.window.visible = False
        elif str(item) == 'Quit':
            page.window.minimized = False
            page.window.visible = True
            page.window.close()

        page.update()
    
    logo = Image.open("src/assets/icon.png")
    
    menu = pystray.Menu(
        pystray.MenuItem('Show', on_click),
        pystray.MenuItem('Hide', on_click),
        pystray.MenuItem('Quit', on_click)
    )
    
    icon = pystray.Icon("Printl", logo, "Printl", menu)
    
    def run_tray():
        icon.run()
    
    tray_thread = threading.Thread(target=run_tray)
    tray_thread.daemon = True
    tray_thread.start()
    
    def on_window_close(e):
        if e.data == 'close':
            page.open(confirm_dialog)
    
    page.window.on_event = on_window_close
    page.window.prevent_close = True