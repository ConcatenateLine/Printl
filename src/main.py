import flet as ft

from pages.domains_page import DomainsPage
from pages.service_manager import ServiceManager
from pages.title_page import TitlePage
from pages.info_page import InfoPage
from pages.printers_page import PrintersPage

from state.state import AppState
from tray.tray import TrayIcon

def app(page: ft.Page):
    state = AppState()
    
    page.session.set("state", state)
    
    tray_icon = TrayIcon(page)
    
    page.title = "Printl"
    page.window.height = 740
    page.window.width = 700
    page.window.min_width = 700
    page.window.min_height = 740
    page.window.max_width = 700
    page.window.max_height = 740
    page.window.resizable = False
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    
    def route_change(e):
        page.views.clear()
        if page.route == "/title":
            page.views.append(TitlePage(page).create_view())
        elif page.route == "/info":
            page.views.append(InfoPage(page))
        elif page.route == "/printers":
            page.views.append(PrintersPage(page).create_view())
        elif page.route == "/service":
            page.views.append(ServiceManager(page).create_view())
        elif page.route == "/domains":
            page.views.append(DomainsPage(page).create_view())
        page.update()

    page.on_route_change = route_change
    page.go("/title")
    
ft.app(app)
    