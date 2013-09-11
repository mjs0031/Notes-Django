""" Python Package Imports """
import random, string, unicodedata
from datetime import *

""" Django Package Imports"""
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response

from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.mail import send_mail

""" Internal Package Imports"""
from NaN.models import *
from NaN.forms import *


"""
---------------
 HOMEPAGE
---------------
 """
def homepage(request):
    user = request.user
    return render_to_response('homepageTemplate.html', RequestContext(request))


"""
---------------------
 AUTHENTICATION BLOCK
---------------------
 """

def loginPage(request):
    state = ''
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                userProfile = UserProfile.objects.get(user=user)
                if userProfile.student == None:
                    return HttpResponseRedirect('/employer/portal/')
                else:
                    return HttpResponseRedirect('/student/portal/')
            else:
                state = "failed"
                return render_to_response('login.html', locals())
        else:
            state = "Your username and password don't match." 
    return render_to_response('login.html', locals(), context_instance=RequestContext(request))

def logoutPage(request):
    logout(request)
    return render_to_response('logout.html')


"""
-------------------
 STUDENT VIEW BLOCK
-------------------
 """
@login_required
def student(request):
    studentsAll = Student.objects.all()
    return render_to_response('allStudentsTemplate.html', locals())

@login_required    
def specificStudent(request, offset):
    offset = int(offset)
    student = Student.objects.get(pk=offset)
    resume = Resume.objects.get(student=student)
    degreeSet = Degree.objects.filter(resume=resume)
    return render_to_response('specificStudentTemplate.html', locals())

@login_required
def specificStudentJobs(request, offset):
    offset = int(offset)
    student = Student.objects.get(pk=offset)
    jobSet = Job.objects.filter(applicant=student)
    return render_to_response('specificStudentJobsTemplate.html', locals())

@login_required
def ajaxStudentHome(request):
    return render_to_response('ajaxStudentHome.html')

@login_required
def ajaxStudentSearch(request, searchString):
    found = True 
    results = Student.objects.filter(name__startswith=searchString)
    if not results:
        results = Student.objects.all()
        found = False
    return render_to_response('ajaxStudentRender.html', {
                                "results": results,
                                "found": found,
                                })

@login_required
def studentResumeCreate(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    resumeExists = True
    try:
        resume = Resume.objects.get(student=student)
    except Resume.DoesNotExist:
        resume = None
        resumeExists = False     
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            if resumeExists == False:
                Resume.objects.create(
                            body = form.cleaned_data['body'],
                            student = student
                        )
            else:
                resume.body = form.cleaned_data['body']
                resume.save()
            return HttpResponseRedirect('/student/portal/')
    else:
        form = ResumeForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })
    return render_to_response('resumeCreate.html', locals())

@login_required
def studentDegree(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    resume = Resume.objects.get(student=student)
    degreeSet = Degree.objects.filter(resume=resume)
    hasDegrees = True
    if not degreeSet:
        hasDegrees = False        
    return render_to_response('studentDegreeHome.html', locals())

@login_required
def studentDegreeCreate(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    resume = Resume.objects.get(student=student)
    
    designation = ''
    if(student.designation == "M"):
        designation = "Master's Student"
    if(student.designation == "U"):
        designation = "Undergraduate Student"
    if(student.designation == "P"):
        designation = "PhD Candidate"
        
    
    if request.method == 'POST':
        form = DegreeForm(request.POST)
        if form.is_valid():
            degree = Degree.objects.create(
                            university = form.cleaned_data['university'],
                            degree = form.cleaned_data['degree'],
                            major = form.cleaned_data['major'],
                            resume = resume
                        )
            employerSet = Employer.objects.all()
            emailBody = "A new student/degree combination has been registered on Need-@-Nerd.\n\
                            \n\
                            Name: %s\n\
                            Education Level (currently): %s\n\
                            Email: %s\n\
                            \n\
                            Degree: %s\n\
                            Major: %s\n\
                            University: %s\n\
                            \n\
                            Resume: %s" % (student.name, designation, student.email, degree.degree, degree.major, degree.university, resume.body)
                            
            for employer in employerSet:
                send_mail('New Job Posting on N-@-N', 
                          emailBody, 
                          'matthewswann00@gmail.com',
                          [employer.email])            
            return HttpResponseRedirect('/student/degreeHome/')
    else:
        form = DegreeForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })
    return render_to_response('studentDegreeCreate.html', locals()) 

@login_required
def studentDegreeUpdate(request, offset):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    resume = Resume.objects.get(student=student)
    degree = Degree.objects.get(pk=offset)
    if request.method == 'POST':
        form = DegreeForm(request.POST)
        if form.is_valid():
            degree.university = form.cleaned_data['university']
            degree.degree = form.cleaned_data['degree']
            degree.major = form.cleaned_data['major']
            degree.save()
            return HttpResponseRedirect('/student/degreeHome/')
    else:
        form = DegreeForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })    
    return render_to_response('studentDegreeUpdate.html', locals())   

@login_required
def studentPortal(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    hasNewJobs = True
    jobSet = Job.objects.filter(postedDate__gte=user.last_login)
    if not jobSet:
        hasNewJobs = False
    return render_to_response('studentPortal.html', locals())

"""
--------------------
 EMPLOYER VIEW BLOCK
--------------------
 """
@login_required
def employer(request):
    employerAll = Employer.objects.all()
    return render_to_response('allEmployersTemplate.html', locals())

@login_required
def specificEmployer(request, offset):
    offset = int(offset)
    employer = Employer.objects.get(pk=offset)
    jobSet = Job.objects.filter(employer=employer)
    return render_to_response('specificEmployerTemplate.html', locals())

@login_required
def specificJob(request, firstOffset, secondOffset):
    firstOffest = int(firstOffset)
    secondOffset = int(secondOffset)
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    employer = userProfile.employer
    job = Job.objects.get(pk=secondOffset)
    applicantSet = job.applicant.all() 
    
    
    isEmployer = False
    hasForm = False
    if(employer != None):
        isEmployer = True
        hasForm = True
        if request.POST:
            form = JobForm(request.POST)
            if form.is_valid():
                job.name = form.cleaned_data['name']
                job.description = form.cleaned_data['description']
                job.save()
                return HttpResponseRedirect('/employer/jobs/')
        else:
            form = JobForm()
            variable = RequestContext(request, {
                                  "form": form,
                                    })               
    else:
        student = userProfile.student
        isValidStudent = True
        try:
            resume = Resume.objects.get(student=student)
            degreeSet = Degree.objects.filter(resume=resume)
        except Resume.DoesNotExist:
            isValidStudent = False
        if not degreeSet:
            isValidStudent = False
        if request.POST:
            form = ApplyForm(request.POST)
            if form.is_valid():
                applying = form.cleaned_data['apply']
                if applying:
                    job.applicant.add(student)
                return HttpResponseRedirect('/student/%s/jobs' % (student.id))
        else:
            form = ApplyForm()
            variable = RequestContext(request, {
                                  "form": form,
                                    })     
               
   
    return render_to_response('specificJobTemplate.html', locals())

@login_required
def jobHome(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    employer = userProfile.employer
    jobSet = Job.objects.filter(employer=employer)
    hasJobs = True
    if not jobSet:
        hasJobs = False    
    return render_to_response('employerJobHome.html', locals())

@login_required
def specificJobCreation(request, offset):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    employer = userProfile.employer
    if request.POST:
        form = JobForm(request.POST)
        if form.is_valid(): 
            job = Job.objects.create(
                        name = form.cleaned_data['name'],
                        description = form.cleaned_data['description'],
                        isVisible = True,
                        employer = employer,
                        startDate = form.cleaned_data['startDate'],
                        endDate = form.cleaned_data['endDate'],
                        skillsRequired = form.cleaned_data['skillsRequired']    
                        )
            studentSet = Student.objects.all()
            emailBody = "A new job has been posted on Need-@-Nerd.\n\
                            \n\
                            Employer: %s\n\
                            On Campus: %s\n\
                            Email: %s\n\
                            Address: %s\n\
                            City: %s\n\
                            State: %s\n\
                            \n\
                            Job Title: %s\n\
                            Job Description: %s" % (employer.name, employer.onCampus, employer.email, employer.address, employer.city, employer.state, job.name, job.description)
                            
            for student in studentSet:
                send_mail('New Job Posting on N-@-N', 
                          emailBody, 
                          'matthewswann00@gmail.com',
                          [student.email])
            return HttpResponseRedirect('/employer/portal/')
    else:
        form = JobForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })      
    return render_to_response('specificJobCreation.html', locals())

@login_required
def employerPortal(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    employer = userProfile.employer
    return render_to_response('employerPortal.html', locals())

@login_required
def ajaxEmployerHome(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    isStudent = True
    if (student == None):
        isStudent = False
    return render_to_response('ajaxEmployerHome.html', locals())

@login_required
def ajaxEmployerSearch(request, searchString):
    found = True 
    results = Employer.objects.filter(name__startswith=searchString)
    if not results:
        results = Employer.objects.all()
        found = False
    return render_to_response('ajaxEmployerRender.html', locals())

@login_required
def ajaxEmployerSearchTwo(request, searchString):
    found = True 
    results = Employer.objects.filter(state=searchString)
    if not results:
        results = Employer.objects.all()
        found = False
    return render_to_response('ajaxEmployerRender.html', locals())

@login_required
def ajaxEmployerSearchThree(request):
    found = True 
    results = Employer.objects.filter(onCampus=True)
    if not results:
        results = Employer.objects.all()
        found = False
    return render_to_response('ajaxEmployerRender.html', locals())

@login_required
def ajaxJobHome(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    student = userProfile.student
    isStudent = True
    if (student == None):
        isStudent = False
    return render_to_response('ajaxJobHome.html', locals())

@login_required
def ajaxJobSearch(request, searchString):
    found = True 
    results = Job.objects.filter(skillsRequired__startswith=searchString)
    if not results:
        results = Job.objects.all()
        found = False
    return render_to_response('ajaxJobRender.html', locals())  
    

"""
------------------- 
 REGISTRATION BLOCK
-------------------
 """
 
def registerStudentPage(request):
    if request.method == 'POST':
        form = StudRegistrationForm(request.POST)
        if form.is_valid():
            newUser = User.objects.create_user(
                            username = form.cleaned_data['username'],
                            password = form.cleaned_data['password'],
                            email = form.cleaned_data['email'],
                                )
            newUser.is_active = False
            newUser.save()
            student = Student.objects.create(
                            name = form.cleaned_data['name'],  
                            designation = form.cleaned_data['designation'],
                            userName = form.cleaned_data['username'],
                            email = form.cleaned_data['email']                                             
                                    )
            userProfile = UserProfile.objects.create(
                            user = newUser,
                            student = student,                   
                            activationKey = ''.join(random.choice(string.digits) for n in range(15))
                                )
            emailBody = 'Please visit http://127.0.0.1:8000/activate/%s/ to activate your account' % (userProfile.activationKey)
            send_mail('Activation Code for Need-@-Nerd', 
                      emailBody, 
                      'matthewswann00@gmail.com',
                      [newUser.email])
            
            return HttpResponseRedirect('/')
    else:
        form = StudRegistrationForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })
        return render_to_response('registerStudent.html', locals())

def registerEmployerPage(request):
    if request.method == 'POST':
        form = EmpRegistrationForm(request.POST)
        if form.is_valid():
            newUser = User.objects.create_user(
                            username = form.cleaned_data['username'],
                            password = form.cleaned_data['password'],
                            email = form.cleaned_data['email'],
                                )
            newUser.is_active = False
            newUser.save()
            designation = form.cleaned_data['designation'],
            onCampus = True
            if(designation == 'O'):
                onCampus = False
            employer = Employer.objects.create(
                            name = form.cleaned_data['name'],  
                            designation = designation,
                            onCampus = onCampus,
                            email = form.cleaned_data['email'],
                            address = form.cleaned_data['address'],
                            state = form.cleaned_data['state'],
                            zipCode = form.cleaned_data['zipCode'],
                            phone = form.cleaned_data['phone'],                                             
                                )
            userProfile = UserProfile.objects.create(
                            user = newUser,
                            employer = employer,                   
                            activationKey = ''.join(random.choice(string.digits) for n in range(15))
                                )
            if (onCampus == True):
                newUser.is_active = True
                newUser.save()            
            return HttpResponseRedirect('/')
    else:
        form = EmpRegistrationForm()
        variable = RequestContext(request, {
                                  "form": form,
                                  })
        return render_to_response('registerEmployer.html', locals())    

def activatePage(request, activateCode):
    try:
        profile = UserProfile.objects.get(activationKey=activateCode)
        user = profile.user
        if user.is_active == False:
            user.is_active = True
            user.save()
            return HttpResponseRedirect('/login/')
        else:
            raise Http404('Account has already been activated.')
    except UserProfile.DoesNotExist:
        raise Http404('No user authentication key found.')
    except User.DoesNotExist:
        raise Http404('User information not found.')
    return render_to_response('activation.html')






