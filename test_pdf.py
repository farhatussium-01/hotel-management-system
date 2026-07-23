import sys
sys.path.insert(0, 'D:\\script\\hotel-management-system\\backend')

from invoice_generator import generate_invoice_pdf
import os

# Test invoice data
test_invoice = {
    'res_id': 999,
    'guest_name': 'Test Guest',
    'room_id': 101,
    'room_type': 'Single',
    'checkin': '2026-07-20',
    'checkout': '2026-07-23',
    'nights': 3,
    'rate': 1500.00,
    'subtotal': 4500.00,
    'tax_rate': 12.0,
    'tax_amount': 540.00,
    'discount': 0.00,
    'total': 5040.00
}

output_path = 'D:\\script\\hotel-management-system\\static\\invoices\\test_invoice.pdf'

try:
    generate_invoice_pdf(test_invoice, output_path)
    print(f"[SUCCESS] PDF generated at: {output_path}")
    print(f"[INFO] File exists: {os.path.exists(output_path)}")
    print(f"[INFO] File size: {os.path.getsize(output_path)} bytes")
except Exception as e:
    print(f"[ERROR] Failed to generate PDF: {e}")
    import traceback
    traceback.print_exc()
