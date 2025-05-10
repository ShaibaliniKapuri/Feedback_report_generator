from django.urls import path
from .views import GenerateHTMLReportView, GetHTMLReportView, GeneratePDFReportView, GetPDFReportView

urlpatterns = [
    path('html', GenerateHTMLReportView.as_view(), name='generate_html_report'),
    path('html/<str:task_id>', GetHTMLReportView.as_view(), name='get_html_report'),
    path('pdf', GeneratePDFReportView.as_view(), name='generate_pdf_report'),
    path('pdf/<str:task_id>', GetPDFReportView.as_view(), name='get_pdf_report'),
]
