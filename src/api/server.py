from typing import Optional
from fastapi import Body, Depends, FastAPI, HTTPException, UploadFile, File

from .dependences import validate_source_ip

from .actions_local import get_default_printer_action, get_public_printers_action
from .actions_server import print_pdf_action, print_text_action, print_json_action, print_ticket_action

from .database import Domains, create_db_and_tables, list_printers, SessionDep, Printer, Config
from sqlmodel import select
from .examples_inputs import TicketExample, JsonExample, TextExample


async def lifespan(app: FastAPI):
    async def startup():
        create_db_and_tables()
        list_printers()
        print("Server started.")

    async def shutdown():
        print("Server shutting down.")

    await startup()
    yield
    await shutdown()

printserver = FastAPI(lifespan=lifespan, title="Print Server API",
                      description="API for managing and printing documents", version="1.0.0")

@printserver.get("/api/version", description="Get API version")
def get_version():
    return {"version": "1.0.0"}

@printserver.get("/api/domains/", description="Get all domains", dependencies=[Depends(validate_source_ip)])
def get_domains(session: SessionDep):
    domains = session.exec(select(Domains)).all()

    if not domains:
        raise HTTPException(status_code=404, detail="No domains found")

    return {"status": "success", "domains": domains}


@printserver.post("/api/domains/", description="Add new domain", dependencies=[Depends(validate_source_ip)])
def add_domain(domain: Domains, session: SessionDep):
    new_domain = Domains(domain=domain.domain)
    session.add(new_domain)
    session.commit()
    session.refresh(new_domain)
    return new_domain


@printserver.delete("/api/domains/{domain}", description="Delete domain", dependencies=[Depends(validate_source_ip)])
def delete_domain(domain: str, session: SessionDep):
    domain_result = session.exec(select(Domains).where(
        Domains.domain == domain)).one_or_none()
    if not domain_result:
        raise HTTPException(status_code=404, detail="Domain not found")
    session.delete(domain_result)
    session.commit()
    return {"status": "success", "message": "Domain deleted successfully"}


@printserver.put("/api/domains/{domain}", description="Update domain", dependencies=[Depends(validate_source_ip)])
def update_domain(domain: str, domain_body: Domains, session: SessionDep):
    domain_result = session.exec(select(Domains).where(
        Domains.domain == domain)).one_or_none()
    if not domain_result:
        raise HTTPException(status_code=404, detail="Domain not found")

    domain_result.status = domain_body.status
    session.add(domain_result)
    session.commit()
    session.refresh(domain_result)

    return domain_result


@printserver.get("/api/printers/", description="Get all printers", dependencies=[Depends(validate_source_ip)])
def get_printers(session: SessionDep):
    printers = session.exec(select(Printer)).all()
    default_printer = session.exec(
        select(Config)
        .where(Config.name == "default_printer")
        .order_by(Config.id.desc())
    ).first()

    return {"status": "success", "printers": printers, "default_printer": default_printer}


@printserver.post("/api/printers/public/", description="Update printer public status", dependencies=[Depends(validate_source_ip)])
def print_public(printer: Printer, session: SessionDep):
    printer_result = session.exec(select(Printer).where(
        Printer.name == printer.name)).one_or_none()

    if not printer_result:
        raise HTTPException(status_code=404, detail="Printer not found")

    printer_result.isPublic = printer.isPublic

    session.add(printer_result)
    session.commit()
    session.refresh(printer_result)

    return printer_result


@printserver.post("/api/printers/", description="Update default printer", dependencies=[Depends(validate_source_ip)])
def update_default_printer(config: Config, session: SessionDep):
    printer = session.exec(select(Printer).where(
        Printer.name == config.value)).one_or_none()
    new_config = Config(name="default_printer", value=config.value)
    if not printer:
        raise HTTPException(status_code=404, detail="Printer not found")

    session.add(new_config)
    session.commit()
    session.refresh(new_config)

    return new_config


@printserver.get("/api/print/", description="Get default printer", dependencies=[Depends(validate_source_ip)])
def get_default_printer(session: SessionDep):
    default_printer = get_default_printer_action(session)

    return {"printer": default_printer}


@printserver.post("/api/print/json/", description="Print JSON data", dependencies=[Depends(validate_source_ip)])
def print_json(session: SessionDep, json_data: dict = Body(..., example=JsonExample()), printer_name: Optional[str] = None):
    success = print_json_action(printer_name, json_data, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print JSON")

    return {"status": "success", "message": "JSON printed successfully"}


@printserver.post("/api/print/text/", description="Print text data", dependencies=[Depends(validate_source_ip)])
def print_text(session: SessionDep, text: str = Body(..., example=TextExample().text), printer_name: Optional[str] = None):
    success = print_text_action(printer_name, text, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print text")

    return {"status": "success", "message": "Text printed successfully"}


@printserver.post("/api/print/pdf/", description="Print PDF data", dependencies=[Depends(validate_source_ip)])
async def print_pdf(session: SessionDep, pdf_file: UploadFile = File(...), printer_name: Optional[str] = None):
    try:
        pdf_data = await pdf_file.read()

        success = print_pdf_action(printer_name, pdf_data, session)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to print PDF")

        return {"status": "success", "message": "PDF printed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@printserver.post("/api/print/ticket/", description="Print ticket data", dependencies=[Depends(validate_source_ip)])
def print_ticket(session: SessionDep, ticket_data: dict = Body(..., example=TicketExample()), printer_name: Optional[str] = None):
    success = print_ticket_action(printer_name, ticket_data, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print ticket")

    return {"status": "success", "message": "Ticket printed successfully"}


@printserver.get("/local/printers/", description="Get public printers", dependencies=[Depends(validate_source_ip)])
def get_public_printers(session: SessionDep):
    printers = get_public_printers_action(session)

    if not printers:
        raise HTTPException(status_code=404, detail="No public printers found")

    return {"status": "success", "printers": printers}


@printserver.post("/local/print/json/", description="Print JSON data", dependencies=[Depends(validate_source_ip)])
def print_json(session: SessionDep, json_data: dict = Body(..., example=JsonExample()), printer_name: Optional[str] = None):
    success = print_json_action(printer_name, json_data, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print JSON")

    return {"status": "success", "message": "JSON printed successfully"}


@printserver.post("/local/print/text/", description="Print text data", dependencies=[Depends(validate_source_ip)])
def print_text(session: SessionDep, text: str = Body(..., example=TextExample().text), printer_name: Optional[str] = None):
    success = print_text_action(printer_name, text, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print text")

    return {"status": "success", "message": "Text printed successfully"}


@printserver.post("/local/print/pdf/", description="Print PDF data", dependencies=[Depends(validate_source_ip)])
async def print_pdf(session: SessionDep, pdf_file: UploadFile = File(...), printer_name: Optional[str] = None):
    try:
        pdf_data = await pdf_file.read()

        success = print_pdf_action(printer_name, pdf_data, session)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to print PDF")

        return {"status": "success", "message": "PDF printed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@printserver.post("/local/print/ticket/", description="Print ticket data", dependencies=[Depends(validate_source_ip)])
def print_ticket(session: SessionDep, ticket_data: dict = Body(..., example=TicketExample()), printer_name: Optional[str] = None):
    success = print_ticket_action(printer_name, ticket_data, session)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to print ticket")

    return {"status": "success", "message": "Ticket printed successfully"}
