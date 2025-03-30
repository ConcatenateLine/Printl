import json
import tempfile
import os
import win32api
import win32print
from fastapi import HTTPException
from sqlmodel import select
from .database import Config, SessionDep

def print_pdf_action(input_printer_name: str, pdf_data: bytes, session: SessionDep):
    try:
        printer_name = input_printer_name
        if not printer_name:
            result_printer = session.exec(
                select(Config)
                .where(Config.name == "default_printer")
                .order_by(Config.id.desc())
            ).first()

            if not result_printer:
                raise HTTPException(
                    status_code=404, detail="Default printer not found")

            printer_name = result_printer.value

        # Verify printer exists and is ready
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        found = False
        for printer in printers:
            if printer[2].lower() == printer_name.lower():
                found = True
                break

        if not found:
            raise HTTPException(
                status_code=404, detail=f"Printer '{printer_name}' not found")

        # Get printer status
        handle = win32print.OpenPrinter(printer_name)
        info = win32print.GetPrinter(handle, 2)
        win32print.ClosePrinter(handle)

        if info['Status'] & win32print.PRINTER_STATUS_ERROR:
            raise HTTPException(
                status_code=500, detail=f"Printer '{printer_name}' is in error state")

        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        print(f"Attempting to print to: {printer_name}")
        print(f"Temp file: {temp_file_path}")

        # Try different printing methods
        try:
            # Method 1: Using ShellExecute
            win32api.ShellExecute(
                0,
                "print",
                temp_file_path,
                f'/p /q /h /t "{temp_file_path}" "{printer_name}"',
                ".",
                0
            )
            print("Print attempt 1 successful using PDF2Printer")
        except Exception as e1:
            print(f"PDF2Printer attempt failed: {str(e1)}")
            try:
                # Method 2: Using win32print
                handle = win32print.OpenPrinter(printer_name)

                # Create DOCINFO structure
                doc_info = ("PDF Document", None, "XPS_PASS")

                # Start print job
                job_id = win32print.StartDocPrinter(handle, 1, doc_info)

                if job_id:
                    try:
                        win32print.StartPagePrinter(handle)
                        with open(temp_file_path, 'rb') as f:
                            data = f.read()
                            # Add PDF header if needed
                            if not data.startswith(b'%PDF-'):
                                data = b'%PDF-1.7\n' + data
                            win32print.WritePrinter(handle, data)
                        win32print.EndPagePrinter(handle)
                        win32print.EndDocPrinter(handle)
                        print("Print attempt 2 successful using win32print")
                    except Exception as e2:
                        print(f"win32print attempt failed: {str(e2)}")
                        raise HTTPException(
                            status_code=500, detail=f"Failed to print: {str(e2)}")
                    finally:
                        win32print.ClosePrinter(handle)
                else:
                    raise HTTPException(
                        status_code=500, detail="Failed to start print job")
            except Exception as e2:
                print(f"Print attempt 2 failed: {str(e2)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to print: {str(e2)}")

        # Clean up
        os.unlink(temp_file_path)
        return True
    except Exception as e:
        print(f"Error printing PDF: {str(e)}")
        return False

def print_text_action(input_printer_name: str, text: str, session: SessionDep):
    try:
        printer_name = input_printer_name
        if not printer_name:
            result_printer = session.exec(
                select(Config)
                .where(Config.name == "default_printer")
                .order_by(Config.id.desc())
            ).first()
            
            if not result_printer:
                raise HTTPException(status_code=404, detail="Default printer not found")
            
            printer_name = result_printer.value
            
        # Verify printer exists and is ready
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        found = False
        for printer in printers:
            if printer[2].lower() == printer_name.lower():
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Printer '{printer_name}' not found")
        
        # Get printer status
        handle = win32print.OpenPrinter(printer_name)
        info = win32print.GetPrinter(handle, 2)
        win32print.ClosePrinter(handle)
        
        if info['Status'] & win32print.PRINTER_STATUS_ERROR:
            raise HTTPException(status_code=500, detail=f"Printer '{printer_name}' is in error state")
        
         # Create a temporary RTF file with formatted text
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rtf') as temp_file:
            # Create RTF content with formatting
            rtf_content = (
                "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\n"
                "{\\colortbl ;\\red0\\green0\\blue0;\\red255\\green0\\blue0;\\red0\\green0\\blue255;}\n"
                "\\viewkind4\\uc1\\pard\\f0\\fs24\\b\\cf1\\par\n"
                f"{text}\\par\n"
                "\\par\n"
                "\\cf0\\f0\\fs24\\b0\\par\n"
            )
            temp_file.write(rtf_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Try to print using ShellExecute
            win32api.ShellExecute(
                0,
                "print",
                temp_file_path,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print("Text print attempt successful using formatted RTF")
            return True
        except Exception as e:
            print(f"RTF print attempt failed: {str(e)}")
            # Fallback to raw text printing
            doc_info = ("Text Document", None, "RAW")
            handle = win32print.OpenPrinter(printer_name)
            
            job_id = win32print.StartDocPrinter(handle, 1, doc_info)
            
            if job_id:
                try:
                    win32print.StartPagePrinter(handle)
                    formatted_text = f"{text}\r\n"
                    win32print.WritePrinter(handle, formatted_text.encode('utf-8'))
                    win32print.EndPagePrinter(handle)
                    win32print.EndDocPrinter(handle)
                    print("Text print attempt successful using raw text")
                    return True
                except Exception as e:
                    print(f"Raw text print attempt failed: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Failed to print text: {str(e)}")
                finally:
                    win32print.ClosePrinter(handle)
            else:
                raise HTTPException(status_code=500, detail="Failed to start print job")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Error printing text: {str(e)}")
        return False
    
def print_json_action(input_printer_name: str, json_data: dict, session: SessionDep):
    try:
        printer_name = input_printer_name
        if not printer_name:
            result_printer = session.exec(
                select(Config)
                .where(Config.name == "default_printer")
                .order_by(Config.id.desc())
            ).first()
            
            if not result_printer:
                raise HTTPException(status_code=404, detail="Default printer not found")
            
            printer_name = result_printer.value
            
        # Verify printer exists and is ready
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        found = False
        for printer in printers:
            if printer[2].lower() == printer_name.lower():
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Printer '{printer_name}' not found")
        
        # Get printer status
        handle = win32print.OpenPrinter(printer_name)
        info = win32print.GetPrinter(handle, 2)
        
        if info['Status'] & win32print.PRINTER_STATUS_ERROR:
            raise HTTPException(status_code=500, detail=f"Printer '{printer_name}' is in error state")
        
        # Convert JSON to formatted text
        formatted_text = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Create a temporary RTF file with formatted text
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rtf') as temp_file:
            # Create RTF content with formatting
            rtf_content = (
                "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\n"
                "{\\colortbl ;\\red0\\green0\\blue0;\\red255\\green0\\blue0;\\red0\\green0\\blue255;}\n"
                "\\viewkind4\\uc1\\pard\\f0\\fs24\\b\\cf1\\par\n"
                "JSON Data:\\par\n"
                "\\par\n"
                f"{formatted_text}\\par\n"
                "\\par\n"
                "\\cf0\\f0\\fs24\\b0\\par\n"
            )
            temp_file.write(rtf_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Try to print using ShellExecute
            win32api.ShellExecute(
                0,
                "print",
                temp_file_path,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print("JSON print attempt successful using formatted RTF")
            return True
        except Exception as e:
            print(f"RTF print attempt failed: {str(e)}")
            # Fallback to raw text printing
            doc_info = ("JSON Document", None, "RAW")
            handle = win32print.OpenPrinter(printer_name)
            
            job_id = win32print.StartDocPrinter(handle, 1, doc_info)
            
            if job_id:
                try:
                    win32print.StartPagePrinter(handle)
                    formatted_text = f"JSON Data:\n\n{formatted_text}\n"
                    win32print.WritePrinter(handle, formatted_text.encode('utf-8'))
                    win32print.EndPagePrinter(handle)
                    win32print.EndDocPrinter(handle)
                    print("JSON print attempt successful using raw text")
                    return True
                except Exception as e:
                    print(f"Raw text print attempt failed: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Failed to print JSON: {str(e)}")
                finally:
                    win32print.ClosePrinter(handle)
            else:
                raise HTTPException(status_code=500, detail="Failed to start print job")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Error printing JSON: {str(e)}")
        return False
    
def print_ticket_action(input_printer_name: str, ticket_data: dict, session: SessionDep):
    try:
        printer_name = input_printer_name
        if not printer_name:
            result_printer = session.exec(
                select(Config)
                .where(Config.name == "default_printer")
                .order_by(Config.id.desc())
            ).first()
            
            if not result_printer:
                raise HTTPException(status_code=404, detail="Default printer not found")
            
            printer_name = result_printer.value
            
        # Verify printer exists and is ready
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        found = False
        for printer in printers:
            if printer[2].lower() == printer_name.lower():
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Printer '{printer_name}' not found")
        
        # Get printer status
        handle = win32print.OpenPrinter(printer_name)
        info = win32print.GetPrinter(handle, 2)
        
        if info['Status'] & win32print.PRINTER_STATUS_ERROR:
            raise HTTPException(status_code=500, detail=f"Printer '{printer_name}' is in error state")
        
        # Create ticket format
        ticket = f"""
        ======================
        TICKET
        ======================
        
        {ticket_data.get('header', 'NO HEADER')}
        
        ======================
        
        {ticket_data.get('items', '')}
        
        ======================
        
        {ticket_data.get('footer', 'NO FOOTER')}
        
        ======================
        """
        
        # Create a temporary RTF file with formatted text
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rtf') as temp_file:
            # Create RTF content with formatting
            rtf_content = (
                "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\n"
                "{\\colortbl ;\\red0\\green0\\blue0;\\red255\\green0\\blue0;\\red0\\green0\\blue255;}\n"
                "\\viewkind4\\uc1\\pard\\f0\\fs24\\b\\cf1\\par\n"
                f"{ticket}\\par\n"
                "\\par\n"
                "\\cf0\\f0\\fs24\\b0\\par\n"
            )
            temp_file.write(rtf_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Try to print using ShellExecute
            win32api.ShellExecute(
                0,
                "print",
                temp_file_path,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print("Ticket print attempt successful using formatted RTF")
            return True
        except Exception as e:
            print(f"RTF print attempt failed: {str(e)}")
            # Fallback to raw text printing
            doc_info = ("Ticket", None, "RAW")
            handle = win32print.OpenPrinter(printer_name)
            
            job_id = win32print.StartDocPrinter(handle, 1, doc_info)
            
            if job_id:
                try:
                    win32print.StartPagePrinter(handle)
                    formatted_text = f"{ticket}\n"
                    win32print.WritePrinter(handle, formatted_text.encode('utf-8'))
                    win32print.EndPagePrinter(handle)
                    win32print.EndDocPrinter(handle)
                    print("Ticket print attempt successful using raw text")
                    return True
                except Exception as e:
                    print(f"Raw text print attempt failed: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Failed to print ticket: {str(e)}")
                finally:
                    win32print.ClosePrinter(handle)
            else:
                raise HTTPException(status_code=500, detail="Failed to start print job")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Error printing ticket: {str(e)}")
        return False
    