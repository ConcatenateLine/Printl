from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine, Field
import win32print
from typing import Annotated

class Config(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(default="")
    value: str = Field(default="")
    secret: str = Field(default="")

class Printer(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(default="")
    status: str = Field(default="")
    jobs: int = Field(default=0)
    queue_size: int = Field(default=0)
    port: str = Field(default="")
    driver: str = Field(default="")
    
class PrintJob(SQLModel, table=True):
    id: int = Field(primary_key=True)
    document: str = Field(default="")
    timestamp: int = Field(default=0)
    status: str = Field(default="")

sqlite_file_name = "printl.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    # Drop all tables
    SQLModel.metadata.drop_all(engine)
    # Create tables
    SQLModel.metadata.create_all(engine)
    
def list_printers():
    try:
        # Get all printers
        # printers_info = win32print.EnumPrinters(2)
        printers_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)

        printers = []
        with Session(engine) as session:
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
                
                printer = Printer(name=printer[2], status=status, jobs=jobs, queue_size=queue_size, port=printer_info['pPortName'], driver=printer_info['pDriverName'])
                
                session.add(printer)

            session.commit()
            print("Printers added to database.")
        
    except Exception as e:
        print(f"Error getting printers: {str(e)}")

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
