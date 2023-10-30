from django.db import models

# Create your models here.
# class Person(models.Model):
#     url=models.URLField(max_length= 200)
#     name= models.CharField(max_length=100)
#     works_at= models.TextField()
#     locat=models.CharField(max_length=100)
#     explist=models.TextField()
#     about=models.TextField()
#     eduction=models.TextField()

#     def __str__(self):
#         return self.url
    
    
class ScrapedData1(models.Model):
    profile_url=models.URLField(max_length=250)
    name = models.CharField(max_length=255)
    works_at = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    exp = models.TextField()
    about = models.TextField()
    uname = models.CharField(max_length=255)
    education = models.TextField()
    # certificates = models.TextField()
    # projects = models.TextField()

class CompanyData1(models.Model):
    comp_name=models.CharField(max_length=255,primary_key=True)
    # comp_name=models.CharField(max_length=255)
    website=models.URLField(max_length=250)
    industry=models.TextField()
    company_size=models.TextField()
    headquarter=models.TextField()
    founded=models.CharField(max_length=255)
    foll=models.CharField(max_length=255)
    specialties=models.TextField()


class EmployeeDetail1(models.Model):
    # compy_name=models.CharField(max_length=255)
    # website=models.URLField(max_length=250)
    # emp_info = models.TextField()
    e_name=models.CharField(max_length=255)
    e_head=models.TextField()
    e_link=models.TextField()
    
    company = models.ForeignKey(CompanyData1, on_delete=models.CASCADE, related_name='employees')
    

# 

# def __str__(self):
#         return self.comp_name





    

