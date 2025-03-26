import win32print
import win32con

from api.models import Printer, SessionDep

def list_printers():
    try:
        # Get all printers
        # printers_info = win32print.EnumPrinters(2)
        printers_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

        printers = []
        for printer in printers_info:
            # Get printer status
            handle = win32print.OpenPrinter(printer[2])  # Use index 2 for printer name
            printer_info = win32print.GetPrinter(handle, 2)
            
            # Convert status to human-readable format
            status = "Online"
            
            # Check for multiple status conditions
            status_flags = []
            if printer_info['Status'] & win32print.PRINTER_STATUS_PAUSED:
                status_flags.append("Paused")
            if printer_info['Status'] & win32print.PRINTER_STATUS_ERROR:
                status_flags.append("Error")
            if printer_info['Status'] & win32print.PRINTER_STATUS_OFFLINE:
                status_flags.append("Offline")
            if printer_info['Status'] & win32print.PRINTER_STATUS_NOT_AVAILABLE:
                status_flags.append("Not Available")
            if printer_info['Status'] & win32print.PRINTER_STATUS_PAPER_JAM:
                status_flags.append("Paper Jam")
            if printer_info['Status'] & win32print.PRINTER_STATUS_OUT_OF_MEMORY:
                status_flags.append("Low Memory")
            if printer_info['Status'] & win32print.PRINTER_STATUS_PAPER_OUT:
                status_flags.append("Out of Paper")
            if printer_info['Status'] & win32print.PRINTER_STATUS_OUTPUT_BIN_FULL:
                status_flags.append("Output Bin Full")
            if printer_info['Status'] & win32print.PRINTER_STATUS_DOOR_OPEN:
                status_flags.append("Door Open")
            
            # Set status based on most critical condition
            if status_flags:
                status = "/".join(status_flags)
            
            # Get number of jobs
            jobs = printer_info['cJobs']
            
            # Get printer queue size
            queue_size = printer_info['cJobs'] * printer_info['AveragePPM']
            
            printers.append({
                "name": printer[2],  # Use index 2 for printer name
                "status": status,
                "jobs": jobs,
                "queue_size": queue_size,
                "port": printer_info['pPortName'],
                "driver": printer_info['pDriverName']
            })
            
            printer = Printer(name=printer[2],
                              status=status,
                              jobs=jobs,
                              queue_size=queue_size,
                              port=printer_info['pPortName'],
                              driver=printer_info['pDriverName'])
            
            session.add(printer)

        print("Printers added to database.")
        session.commit()
        
        
    except Exception as e:
        print(f"Error getting printers: {str(e)}")
        return []
