from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime
import json
from zoneinfo import ZoneInfo

def generate_daily_report_pdf(context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    daily_report = context.get('daily_report')
    total_sales = context.get('total_sales')
    report_date_str = context.get('report_date_str')
    orders_data = context.get('orders_data')
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph(f"Reporte Diario - {report_date_str}", title_style))
    story.append(Spacer(1, 12))
    
    # Summary table
    summary_data = [
        ['Concepto', 'Monto (Q)'],
        ['Total de Ventas', f'{total_sales:.2f}'],
    ]
    if daily_report and daily_report.closed_at:
        summary_data.extend([
            ['Efectivo en Caja', f'{daily_report.cash_in_register:.2f}'],
            ['Diferencia', f'{daily_report.difference:.2f}']
        ])
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Orders detail
    if orders_data:
        story.append(Paragraph("Detalle de Órdenes", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        orders_data_table = [['ID', 'Hora', 'Items', 'Total', 'Estado']]
        for order in orders_data:
            orders_data_table.append([
                order['id'],
                order['time'],
                Paragraph(order['items'], styles['Normal']),
                order['total'],
                order['status']
            ])
        
        orders_table = Table(orders_data_table, colWidths=[0.5*inch, 1*inch, 3*inch, 1*inch, 1*inch])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(orders_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_sales_report_pdf(report_data, period_type):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        alignment=1
    )
    title = f"Reporte de Ventas {period_type.title()}"
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(report_data['period_label'], ParagraphStyle('centered', alignment=1)))
    story.append(Spacer(1, 20))

    # Summary
    summary_style = styles['Normal']
    story.append(Paragraph(f"<b>Total de Ventas:</b> Q{report_data['total_sales']:.2f}", summary_style))
    story.append(Paragraph(f"<b>Total de Órdenes:</b> {report_data['total_orders']}", summary_style))
    story.append(Paragraph(f"<b>Día con más ventas:</b> {report_data['dia_mas_ventas']}", summary_style))
    story.append(Spacer(1, 20))

    # Top Selling Products
    story.append(Paragraph("Top 5 Productos Más Vendidos", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    top_products = report_data.get('top_selling_products')
    if top_products:
        table_data = [['Producto', 'Cantidad Vendida']]
        for item in top_products:
            table_data.append([item.name, str(item.total_quantity)])
        
        table = Table(table_data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No hay datos de productos vendidos.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_receipt_pdf(order, cash_received, change):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(3 * inch, 5 * inch), topMargin=0.2*inch, bottomMargin=0.2*inch, leftMargin=0.2*inch, rightMargin=0.2*inch)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    center_style = ParagraphStyle('center', parent=styles['Normal'], alignment=1)
    center_bold_style = ParagraphStyle('center_bold', parent=center_style, fontName='Helvetica-Bold')
    normal_style = styles['Normal']
    
    # Header
    story.append(Paragraph("Restaurante M&S", center_bold_style))
    story.append(Paragraph("Comprobante de Pago", center_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # Order Info
    guatemala_tz = ZoneInfo("America/Guatemala")
    local_created_at = order.created_at.replace(tzinfo=ZoneInfo("UTC")).astimezone(guatemala_tz)
    formatted_date = local_created_at.strftime('%d/%m/%Y %H:%M')

    story.append(Paragraph(f"Orden #{order.id}", normal_style))
    story.append(Paragraph(f"Fecha: {formatted_date}", normal_style))
    story.append(Paragraph(f"Cliente: {order.customer_name or 'N/A'}", normal_style))
    story.append(Paragraph(f"Mesero: {order.waiter.full_name}", normal_style))
    story.append(Spacer(1, 0.2 * inch))

    # Items Table
    items_data = [['Cant.', 'Descripción', 'Total']]
    for item in order.items:
        # Create descriptive name for variants
        if not item.product.is_base_product and item.product.parent:
            description = f"{item.product.parent.name} ({item.product.name})"
        else:
            description = item.product.name

        if item.extras:
            try:
                extras_list = json.loads(item.extras)
                if extras_list:
                    extra_names = [f"{extra['name']} (x{extra['quantity']})" for extra in extras_list]
                    description += f"<br/><font size='-1'><i>Extras: {', '.join(extra_names)}</i></font>"
            except (json.JSONDecodeError, TypeError):
                # Fallback for old data that is just a string
                description += f"<br/><font size='-1'><i>Extras: {item.extras}</i></font>"
        
        items_data.append([
            item.quantity,
            Paragraph(description, normal_style),
            f"Q{item.unit_price * item.quantity:.2f}"
        ])

    items_table = Table(items_data, colWidths=[0.4*inch, 1.6*inch, 0.6*inch])
    items_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'), # Quantity
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'), # Total
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.2 * inch))

    # Totals
    totals_data = [
        ['Total:', f'Q{order.total:.2f}'],
        ['Efectivo Recibido:', f'Q{cash_received:.2f}'],
        ['Cambio:', f'Q{change:.2f}'],
    ]
    totals_table = Table(totals_data, colWidths=[1.8*inch, 0.8*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 0.2 * inch))

    # Footer
    story.append(Paragraph("¡Gracias por su preferencia!", center_style))

    doc.build(story)
    buffer.seek(0)
    return buffer