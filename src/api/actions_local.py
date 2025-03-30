from .database import Printer, SessionDep, Config
from fastapi import HTTPException
from sqlmodel import select

def get_default_printer_action(session: SessionDep):
    default_printer = session.exec(
        select(Config)
        .where(Config.name == "default_printer")
        .order_by(Config.id.desc())
    ).first()
    
    if not default_printer:
        raise HTTPException(status_code=404, detail="Default printer not found")
    
    return default_printer

def get_public_printers_action(session: SessionDep):
    printers = session.exec(select(Printer).where(Printer.isPublic == True)).all()
    default_printer =  session.exec(
        select(Config)
        .where(Config.name == "default_printer")
        .order_by(Config.id.desc())
    ).first()    
    
    if not printers:
        raise HTTPException(status_code=404, detail="No public printers found")
    
    return {"printers": printers, "default_printer": default_printer}
