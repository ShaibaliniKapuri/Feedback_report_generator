from celery import shared_task
from .models import Report
from .utils import get_event_alias_order
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.conf import settings
import os


#celery task for generating the html report

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=5)
def generate_html_report(self, data):
    task_id = self.request.id
    student_id = data[0].get('student_id')
    events = data[0].get('events', [])

    event_order = get_event_alias_order(events)

    event_order_str = ' -> '.join(event_order)

    html_content = render_to_string('report_template.html', {
        'student_id': student_id,
        'event_order': event_order_str,
    })

    Report.objects.create(
        task_id=task_id,
        student_id=student_id,
        report_type='html',
        content=html_content
    )
    return "HTML Report generated"


#celery task for pdf report generation

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=5)
def generate_pdf_report(self, data):
    task_id = self.request.id
    student_id = data[0].get('student_id')
    events = data[0].get('events', [])

    event_order = get_event_alias_order(events)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize= A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Student Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, f"Student ID: {student_id}")
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 140, "Event Order:")

    table_data = [["Q.No", "Event"]]
    for idx, event in enumerate(event_order, 1):
        table_data.append([f"Q{idx}", event])

    table = Table(table_data, colWidths=[100, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 100, height - 180 - (len(event_order) * 20))
    p.save()

    pdf_content = buffer.getvalue()
    buffer.close()

    Report.objects.create(
        task_id=task_id,
        student_id=student_id,
        report_type='pdf',
        pdf_file=ContentFile(pdf_content, name=f"{task_id}.pdf")
    )

    return "PDF report generated"
