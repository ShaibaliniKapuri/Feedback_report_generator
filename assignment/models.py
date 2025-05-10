from django.db import models

# Create your models here.
class Report(models.Model):
    task_id = models.CharField(max_length = 100, unique = True)
    student_id = models.CharField(max_length = 100)
    report_type = models.CharField(max_length = 10)
    content = models.TextField(null = True, blank = True)
    pdf_file = models.FileField(upload_to='pdf_reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)


    def __str__ (self):
        return f"{self.report_type} Report for {self.student_id}"
