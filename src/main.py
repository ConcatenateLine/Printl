import flet as ft
from pages.title_page import TitlePage
from pages.counter_page import CounterPage
from pages.printers_page import PrintersPage
import multiprocessing
from api.server import printserver

# Run FastAPI and Flet in parallel
def run_fastapi():
    import uvicorn
    uvicorn.run(printserver, host="0.0.0.0", port=9417)

def app(page: ft.Page):
    # Set up the page
    page.title = "Printl"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.height = 640
    page.window.width = 360
    
    # Add routes
    page.views.append(TitlePage(page))
    page.views.append(CounterPage(page))
    page.views.append(PrintersPage(page).create_view())
    
    # Handle navigation
    def route_change(e):
        page.views.clear()
        if page.route == "/title":
            page.views.append(TitlePage(page))
        elif page.route == "/counter":
            page.views.append(CounterPage(page))
        elif page.route == "/printers":
            page.views.append(PrintersPage(page).create_view())
        page.update()

    page.on_route_change = route_change
    page.go("/title")
    
def run_app():
    ft.app(target=app)
    
if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_fastapi)
    client_process = multiprocessing.Process(target=run_app)
    
    server_process.start()
    client_process.start()
    
    try:
        client_process.join()
        server_process.join()
    except KeyboardInterrupt:
        print("Shutting down...")
        handle_shutdown()
    finally:
        # Ensure processes are terminated
        if server_process.is_alive():
            server_process.terminate()
        if client_process.is_alive():
            client_process.terminate()