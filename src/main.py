import flet as ft

from pages.service_manager import ServiceManager
from pages.title_page import TitlePage
from pages.counter_page import CounterPage
from pages.printers_page import PrintersPage

from tray.tray import create_tray_icon

def app(page: ft.Page):
    create_tray_icon(page)
    
    page.title = "Printl"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.height = 640
    page.window.width = 360
    
    page.views.append(TitlePage(page))
    page.views.append(CounterPage(page))
    page.views.append(PrintersPage(page).create_view())
    page.views.append(ServiceManager(page).create_view())
    
    def route_change(e):
        page.views.clear()
        if page.route == "/title":
            page.views.append(TitlePage(page))
        elif page.route == "/counter":
            page.views.append(CounterPage(page))
        elif page.route == "/printers":
            page.views.append(PrintersPage(page).create_view())
        elif page.route == "/service":
            page.views.append(ServiceManager(page).create_view())
        page.update()

    page.on_route_change = route_change
    page.go("/title")
    
ft.app(app)
    