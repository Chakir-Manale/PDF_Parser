from django.db import models


class UserPDF(models.Model):
    pdf = models.FileField('Upload Resumes', upload_to='UploadedPDFs/')
    title = models.CharField(max_length=1000, default="")
    tables = models.IntegerField(blank=True, default=0)
    pages = models.IntegerField(blank=True, default=0)

