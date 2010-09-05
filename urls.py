from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

#first argument is the common prefixes for simplicity
urlpatterns = patterns('',
       # (r'^polls/', include('mysite.polls.urls')),
         (r'^upload/', 'projectSimulation.simpyHPC.modelForms.upload_file'),
         (r'^simulation/', 'projectSimulation.simpyHPC.views.sim'),
         (r'^validation/', 'projectSimulation.simTemplates.polls.validation'),
         )
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    # )

