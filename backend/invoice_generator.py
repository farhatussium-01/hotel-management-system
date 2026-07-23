from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class InvoicePDF:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6
        )

    def generate_invoice(self, invoice_data):
        """Generate PDF invoice from invoice data"""

        # Title
        title = Paragraph("HOTEL INVOICE", self.title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))

        # Invoice Info Header
        invoice_info_data = [
            ['Invoice Date:', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Reservation ID:', str(invoice_data['res_id'])],
        ]

        invoice_info_table = Table(invoice_info_data, colWidths=[2*inch, 3*inch])
        invoice_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        self.story.append(invoice_info_table)
        self.story.append(Spacer(1, 0.4*inch))

        # Guest Information Section
        guest_heading = Paragraph("Guest Information", self.heading_style)
        self.story.append(guest_heading)

        guest_data = [
            ['Guest Name:', invoice_data['guest_name']],
            ['Room Number:', f"{invoice_data['room_id']} ({invoice_data['room_type']})"],
            ['Check-in Date:', invoice_data['checkin']],
            ['Check-out Date:', invoice_data['checkout']],
            ['Nights Stayed:', str(invoice_data['nights'])],
        ]

        guest_table = Table(guest_data, colWidths=[2*inch, 4*inch])
        guest_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ]))

        self.story.append(guest_table)
        self.story.append(Spacer(1, 0.4*inch))

        # Charges Section
        charges_heading = Paragraph("Charges", self.heading_style)
        self.story.append(charges_heading)

        charges_data = [
            ['Description', 'Quantity', 'Rate', 'Amount'],
            ['Room Charges', str(invoice_data['nights']),
             f"${invoice_data['rate']:.2f}",
             f"${invoice_data['subtotal']:.2f}"],
            ['Tax ({:.0f}%)'.format(invoice_data['tax_rate']), '', '',
             f"${invoice_data['tax_amount']:.2f}"],
        ]

        if invoice_data['discount'] > 0:
            charges_data.append(['Discount', '', '', f"-${invoice_data['discount']:.2f}"])

        charges_table = Table(charges_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        charges_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))

        self.story.append(charges_table)
        self.story.append(Spacer(1, 0.3*inch))

        # Total Section
        total_data = [
            ['TOTAL AMOUNT', f"${invoice_data['total']:.2f}"],
        ]

        total_table = Table(total_data, colWidths=[5*inch, 2*inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#667eea')),
        ]))

        self.story.append(total_table)
        self.story.append(Spacer(1, 0.5*inch))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=6
        )

        footer_text = [
            "Thank you for choosing our hotel!",
            "For any queries, please contact our front desk.",
            "Generated by Hotel Management System"
        ]

        for text in footer_text:
            self.story.append(Paragraph(text, footer_style))

        # Build PDF
        self.doc.build(self.story)
        return self.filename

def generate_invoice_pdf(invoice_data, output_path):
    """Helper function to generate invoice PDF"""
    pdf = InvoicePDF(output_path)
    return pdf.generate_invoice(invoice_data)
