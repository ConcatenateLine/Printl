from pydantic import BaseModel

# Define example data
class TicketExample(BaseModel):
    header: str = "ACME CORPORATION\n123 Business Ave\nAnytown, CA 90210\nPhone: (555) 123-4567"
    items: list = [
        {
            "name": "Widget",
            "quantity": 2,
            "price": 19.99,
            "total": 39.98
        },
        {
            "name": "Gadget",
            "quantity": 1,
            "price": 29.99,
            "total": 29.99
        }
    ]
    footer: dict = {
        "subtotal": 69.97,
        "tax": 6.99,
        "total": 76.96,
        "payment_method": "Cash",
        "change": 23.04,
        "transaction_id": "TX123456789",
        "cashier": "John Doe",
        "date": "2025-03-30",
        "time": "03:08"
    }

class JsonExample(BaseModel):
    report: dict = {
        "title": "Monthly Sales Report",
        "period": "March 2025",
        "metrics": {
            "total_sales": 150000.00,
            "average_order": 125.00,
            "total_customers": 1200,
            "new_customers": 300,
            "returning_customers": 900
        },
        "top_products": [
            {
                "name": "Product A",
                "sales": 50000.00,
                "quantity": 400
            },
            {
                "name": "Product B",
                "sales": 35000.00,
                "quantity": 280
            }
        ]
    }

class TextExample(BaseModel):
    text: str = "Important Memo:\n\nPlease ensure all reports are submitted by 5 PM today.\nMake sure to include all necessary documentation.\nThank you,\nManagement"

class UrlExample(BaseModel):
    url: str = "https://www.example.com/exmaplefile.pdf"
