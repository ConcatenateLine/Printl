from fastapi import FastAPI, HTTPException

from .database import create_db_and_tables, list_printers, SessionDep, Printer, Config
from sqlmodel import select

printserver = FastAPI()

@printserver.on_event("startup")
def on_startup():
    create_db_and_tables()
    list_printers()
    
@printserver.get("/api/printers/")
def get_printers(session: SessionDep):
    printers = session.exec(select(Printer)).all()
    default_printer = session.exec(
        select(Config)
        .where(Config.name == "default_printer")
        .order_by(Config.id.desc())
    ).first()
    
    return {"status": "success", "printers": printers, "default_printer": default_printer}

@printserver.get("/api/printers/{printer_id}")
def read_printer(printer_id: int, q: str = None):
    return {"printer_id": printer_id, "q": q}

@printserver.post("/api/printers/")
def update_default_printer(config: Config, session: SessionDep):
    printer = session.exec(select(Printer).where(Printer.name == config.value)).one_or_none()
    new_config = Config(name="default_printer", value=config.value)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")
    
    session.add(new_config)
    session.commit()
    session.refresh(new_config)
    
    return new_config

@printserver.get("/api/print/")
def get_default_printer():
    return {"printer": "default_printer"}

@printserver.post("/api/print/json/")
def print_json(json_data: dict):
    return {"json_data": json_data}

@printserver.post("/api/print/text/")
def print_text(text: str):
    return {"text": text}
