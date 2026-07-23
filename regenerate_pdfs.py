import sys
import os
import re
sys.path.insert(0, 'D:\\script\\hotel-management-system\\backend')

from invoice_generator import generate_invoice_pdf
from dotenv import load_dotenv

load_dotenv()

invoices_dir = 'D:\\script\\hotel-management-system\\static\\invoices'

# Find all text invoice files
txt_files = [f for f in os.listdir(invoices_dir) if f.startswith('invoice_') and f.endswith('.txt')]

print(f"Found {len(txt_files)} text invoice(s)")

for txt_file in txt_files:
    txt_path = os.path.join(invoices_dir, txt_file)

    # Extract reservation ID from filename
    match = re.search(r'invoice_(\d+)\.txt', txt_file)
    if not match:
        continue

    res_id = int(match.group(1))
    pdf_file = f'invoice_{res_id}.pdf'
    pdf_path = os.path.join(invoices_dir, pdf_file)

    # Check if PDF already exists
    if os.path.exists(pdf_path):
        print(f"[SKIP] PDF already exists for reservation {res_id}")
        continue

    # Parse text invoice to extract data
    try:
        with open(txt_path, 'r') as f:
            content = f.read()

        # Extract data using regex
        def extract_field(pattern, content):
            match = re.search(pattern, content)
            return match.group(1).strip() if match else None

        invoice_data = {
            'res_id': res_id,
            'guest_name': extract_field(r'Guest Name\s*:\s*(.+)', content),
            'room_id': int(extract_field(r'Room ID / Type\s*:\s*(\d+)', content)),
            'room_type': extract_field(r'Room ID / Type\s*:\s*\d+\s*\((.+?)\)', content),
            'checkin': extract_field(r'Check-in\s*:\s*(.+)', content),
            'checkout': extract_field(r'Check-out\s*:\s*(.+)', content),
            'nights': int(extract_field(r'Nights Stayed\s*:\s*(\d+)', content)),
            'rate': float(extract_field(r'Nightly Rate\s*:\s*(\d+\.?\d*)', content)),
            'subtotal': float(extract_field(r'Subtotal\s*:\s*(\d+\.?\d*)', content)),
            'tax_rate': float(extract_field(r'Tax \((\d+)%\)', content)),
            'tax_amount': float(extract_field(r'Tax \(\d+%\)\s*:\s*(\d+\.?\d*)', content)),
            'discount': float(extract_field(r'Discount\s*:\s*-?(\d+\.?\d*)', content)),
            'total': float(extract_field(r'TOTAL DUE\s*:\s*(\d+\.?\d*)', content)),
        }

        # Generate PDF
        generate_invoice_pdf(invoice_data, pdf_path)
        print(f"[SUCCESS] Generated PDF for reservation {res_id}")

    except Exception as e:
        print(f"[ERROR] Failed to generate PDF for reservation {res_id}: {e}")
        import traceback
        traceback.print_exc()

print("\nDone! All missing PDFs have been generated.")
