""" Python Package Imports"""
import datetime

""" Django Package Imports"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us import models as us_models
from django.utils import timezone

"""
----------------------- 
 STUDENT Related Tables
-----------------------
 """

STUD_DESIGNATIONS = (
    ('U', 'Undergraduate'),
    ('M', 'Masters Student'),
    ('P', 'PhD Candidate'),
    ) 
 
class Student(models.Model):
    name = models.CharField(max_length=30)
    userName = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=30)
    designation = models.CharField(max_length=1, blank=True, choices=STUD_DESIGNATIONS)
    
    def __unicode__(self):
        return '%s\t%s\t%s' % (self.name, self.userName, self.email)
    
    class Meta:
        ordering = ['name']
    
class Resume(models.Model):
    student = models.OneToOneField(Student, primary_key = True)
    body = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.body
    
class Degree(models.Model):
    resume = models.ForeignKey(Resume)
    degree = models.CharField(max_length=20)
    major = models.CharField(max_length=30)
    university = models.CharField(max_length=50)
    date = models.DateField(blank=True, null=True)   
    
    def __unicode__(self):
        return '%s\t%s\t%s\t%s' % (self.degree, self.major, self.university, self.date)

""" 
------------------------
 EMPLOYER Related Tables
------------------------
 """ 

EMP_DESIGNATIONS = (
    ('F', 'On Campus: Faculty Member'),
    ('R', 'On Campus: Researcher'),
    ('S', 'On Campus: Staff'),
    ('O', 'Off Campus: Other'),
    )

class Employer(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    onCampus = models.BooleanField()
    address = models.CharField(max_length=64, blank=True)
    city = models.CharField(max_length=64, blank=True)
    state = us_models.USStateField(blank=True)
    zipCode = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    designation = models.CharField(max_length=1, blank=True, choices=EMP_DESIGNATIONS)
       
    def __unicode__(self):
        return '%s\t%s' % (self.name, self.email)

    class Meta:
        ordering= ['name']

class Job(models.Model):
    applicant = models.ManyToManyField(Student)
    employer = models.ForeignKey(Employer, blank=True, null=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    skillsRequired = models.TextField(blank=True)
    startDate = models.DateField(blank=True)
    endDate = models.DateField(blank=True)
    postedDate = models.DateTimeField(auto_now_add=True)
    isVisible = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
"""
--------------------
 USER Related Tables
--------------------
 """

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    student = models.OneToOneField(Student, blank=True, null=True)
    employer = models.OneToOneField(Employer, blank=True, null=True)
    lastLogin = models.DateField(blank=True, null=True)
    performanceHistory = models.DateTimeField(blank=True, null=True)
    activationKey = models.CharField(max_length=15)
    
    def __unicode__(self):
        return "%s" % (self.user)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"