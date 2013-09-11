from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.localflavor.us.forms import USStateField 
from django.contrib.auth.models import User

STUD_DESIGNATIONS = (
    ('U', 'Undergraduate'),
    ('M', 'Masters Student'),
    ('P', 'PhD Candidate'),
    ) 

EMP_DESIGNATIONS = (
    ('F', 'On Campus: Faculty Member'),
    ('R', 'On Campus: Researcher'),
    ('S', 'On Campus: Staff'),
    ('O', 'Off Campus: Other'),
    )

class ApplyForm(forms.Form):
    apply = forms.BooleanField()

class ResumeForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea) 
    
class DegreeForm(forms.Form):
    degree = forms.CharField(max_length=20, required=False)
    major = forms.CharField(max_length=30, required=False)
    university = forms.CharField(max_length=50, required=False) 
    
class JobForm(forms.Form):
    name = forms.CharField(max_length=30)
    description = forms.CharField(max_length=100)
    isVisible = forms.BooleanField(required=False)
    skillsRequired = forms.CharField(widget=forms.Textarea)
    startDate = forms.DateField(required=False)
    endDate = forms.DateField(required=False)

class EmpRegistrationForm(forms.Form):
    name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=10)
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    passwordChecker = forms.CharField(label='Password (match above)', widget=forms.PasswordInput())
    email = forms.EmailField(max_length=30)
    address = forms.CharField(max_length=64)
    city = forms.CharField(max_length=64)
    state = USStateField()
    zipCode = forms.CharField(max_length=10)
    phone = forms.CharField(max_length=12)
    designation = forms.ChoiceField(choices=EMP_DESIGNATIONS, widget=forms.RadioSelect)
    
class StudRegistrationForm(forms.Form):
    name = forms.CharField(max_length=30)
    designation = forms.ChoiceField(choices=STUD_DESIGNATIONS, widget=forms.RadioSelect)
    username = forms.CharField(label='Username', max_length=10)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    passwordChecker = forms.CharField(label='Password (match above)', widget=forms.PasswordInput())


    """ Not Currently Implemented"""        
    def cleanPassword(self):
        if 'password' in self.cleaned_data:
            password = self.cleaned_data['password']
            passwordChecker = self.cleaned_data['passwordChecker']
            if (password == passwordChecker):
                return passwordChecker
            else:
                raise forms.ValidationError('Passwords do not match.')
            
    def cleanUsername(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            raise forms.ValidationError('Chosen username has been taken.')
        except User.DoesNotExist:
            return username
        
    def cleanEmail(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
            raise forms.ValidationError('Email is currently in use. NaN does not tolerate attempts to burgal email.')
        except User.DoesNotExist:
            return email