from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Report
from .tasks import generate_html_report
from .tasks import generate_pdf_report
from celery.result import AsyncResult


#POST API for html report
class GenerateHTMLReportView(APIView):
    def post(self, request):
        data = request.data

        if not isinstance(data, list) or not data:
            return Response({"error" : "Invalid or empty data. Expected a non-empty list."}, status = status.HTTP_400_BAD_REQUEST)
        
        student_id = data[0].get('student_id')
        if not student_id:
            return Response({"error": "student_id missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            task = generate_html_report.delay(data = data)
            return Response({"task_id": task.id, "message": "Task successfully submitted."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": f"Failed to enqueue HTML generation task. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#GET API for html report
class GetHTMLReportView(APIView):
    def get(self, request, task_id):
        if not task_id:
            return Response({"error": "Missing 'task_id' in the request."}, status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id)
        status_ = result.status

        if status_ == 'PENDING':
            return Response({"status": "PENDING", "message": "Task has not started yet."}, status=status.HTTP_202_ACCEPTED)
        elif status_ == 'STARTED':
            return Response({"status": "STARTED", "message": "Task is currently in progress."}, status=status.HTTP_202_ACCEPTED)
        elif status_ == 'FAILURE':
            return Response({"status": "FAILURE", "message": "Task failed. Please check task logs or Flower dashboard for more details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif status_ == 'SUCCESS':
            try:
                report = Report.objects.get(task_id=task_id)
                if not report.content:
                    return Response({"error": "HTML report content not found."}, status=status.HTTP_404_NOT_FOUND)

                return HttpResponse(report.content, content_type='text/html')

            except Report.DoesNotExist:
                return Response({"error": "No report found for the provided task ID."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": f"An unexpected error occurred while fetching the report. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": status_, "message": "Unknown task status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#POST API for pdf report
class GeneratePDFReportView(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list) or not data:
            return Response({"error": "Invalid or empty data. Expected a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        student_id = data[0].get('student_id')
        if not student_id:
            return Response({"error": "Missing 'student_id' in the payload."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = generate_pdf_report.delay(data=data)
            return Response({"task_id": task.id, "message": "Task successfully submitted."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": f"Failed to enqueue PDF generation task. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#GET API for pdf report 
class GetPDFReportView(APIView):
    def get(self, request, task_id):
        if not task_id:
            return Response({"error": "Missing 'task_id' in the request."}, status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id)
        status_ = result.status

        if status_ == 'PENDING':
            return Response({"status": "PENDING", "message": "Task not yet started."}, status=status.HTTP_202_ACCEPTED)
        elif status_ == 'STARTED':
            return Response({"status": "STARTED", "message": "Task is in progress."}, status=status.HTTP_202_ACCEPTED)
        elif status_ == 'FAILURE':
            return Response({"status": "FAILURE", "message": "Task failed. Please check the task logs or Flower dashboard."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif status_ == 'SUCCESS':
            try:
                report = Report.objects.get(task_id=task_id)
                if not report.pdf_file:
                    return Response({"error": "PDF report not available."}, status=status.HTTP_404_NOT_FOUND)

                download_url = f"{request.build_absolute_uri('/media/')}{report.pdf_file.name}"

                return Response({
                    "status": "SUCCESS",
                    "message": "PDF ready for download.",
                    "download_url": download_url
                }, status=status.HTTP_200_OK)
            

            except Report.DoesNotExist:
                return Response({"error": "No report found for the provided task ID."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": f"An error occurred while retrieving the PDF. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status": status_, "message": "Unknown task status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

