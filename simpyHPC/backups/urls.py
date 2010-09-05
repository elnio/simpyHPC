from django.conf.urls.defaults import *

### !!! Following line/s has been added to use generic views ###
from mysite.polls.models import Poll
###

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

### !!! Following line/s has been added to use generic views ###
info_dict = {
                'queryset':Poll.objects.all(),
                        }

urlpatterns = patterns( '',
    (r'^$','django.views.generic.list_detail.object_list',info_dict),
    
    (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail',info_dict),
    
    url(r'^(?P<object_id>\d+)/results/$','django.views.generic.list_detail.object_detail',dict(info_dict,template_name='polls/results.html'),'poll_results'),

    (r'^(?P<object_id>\d+)/vote/$','mysite.polls.views.vote'),
    
    )

##


### !!! Following line/s has been commented to use generic views ###

#first argument is the common prefixes for simplicity
#urlpatterns = patterns('mysite.polls.views',
#   (r'^$', 'index'),
#   (r'^(?P<poll_id>\d+)/$','detail'),
#   (r'^(?P<poll_id>\d+)/results/$', 'results'),
#   (r'^(?P<poll_id>\d+)/vote/$','vote'),
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#     )

##

