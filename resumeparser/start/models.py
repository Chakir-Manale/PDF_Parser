from django.db import models


class UserResumes(models.Model):
    pinfo = models.CharField(max_length=1000,default="")
    cgpa = models.CharField(max_length=50,default="")
    mobile=models.CharField(max_length=10,default="")
    email=models.CharField(max_length=50,default="")
    objective = models.CharField(max_length=1000,default="")
    education = models.TextField(max_length=5000,default="")
    skill = models.TextField(max_length=5000,default="")
    achievements = models.CharField(max_length=3000,default="")
    projects = models.TextField(max_length=5000,default="")
    hobbies = models.CharField(max_length=1000,default="")




