from django.conf.urls import *
from NaN.views import * 

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'NeedANerd.views.home', name='home'),
    # url(r'^NeedANerd/', include('NeedANerd.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    # Administrative Block
    url(r'^$', homepage),
    url(r'^login/$', loginPage),
    url(r'^logout/$', logoutPage),
    url(r'^register/student/$', registerStudentPage),
    url(r'^register/employer/$', registerEmployerPage),
    url(r'^activate/(\w+)', activatePage),
    
    # Student Block
    url(r'^student/$', student),
    url(r'^student/portal/$', studentPortal),
    url(r'^student/resumeCreate/$', studentResumeCreate),
    url(r'^student/degreeHome/$', studentDegree),
    url(r'^student/degree/create/$', studentDegreeCreate),
    url(r'^student/degree/update/(\d+)/$', studentDegreeUpdate),
    url(r'^student/(\d+)/$', specificStudent),
    url(r'^student/(\d+)/jobs/$', specificStudentJobs),
    url(r'^student/search/$', ajaxStudentHome),
    url(r'^student/search/(\w+)/$', ajaxStudentSearch),  
    
    # Employer Block
    url(r'^employer/$', employer),
    url(r'^employer/portal/$', employerPortal),
    url(r'^employer/(\d+)/$', specificEmployer),
    url(r'^employer/jobs/$', jobHome),
    url(r'^employer/(\d+)/job/$', specificJobCreation),
    url(r'^employer/(\d+)/job/(\d+)/$', specificJob),
    url(r'^employer/search/$', ajaxEmployerHome),
    url(r'^employer/search/(\w+)/$', ajaxEmployerSearch),
    url(r'^employer/search2/(\w+)/$', ajaxEmployerSearchTwo),
    url(r'^employer/search3/$', ajaxEmployerSearchThree),
    url(r'^jobs/search/$', ajaxJobHome),
    url(r'^jobs/search/(\w+)/$', ajaxJobSearch),
        
    
)
