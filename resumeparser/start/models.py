from django.db import models


class UserResumes(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    mobile=models.CharField(max_length=10)
    email=models.CharField(max_length=50)




