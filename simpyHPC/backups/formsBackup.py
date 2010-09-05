from django.forms import ModelForm
from models import Poll
from django import forms
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse


## Here are the forms and their callbacks
class UploadFileForm( forms.Form ):

    title = forms.CharField( max_length = 50)
    file = forms.FileField()



## Handle for the file uploading and methods for handling the forms
def handle_uploaded_file( file, fileName ):
    destination = open(   './%s' % fileName   ,'wb+')
    for chunk in file.chunks():
        destination.write( chunk )
    destination.close()


def upload_file( request ):


    if request.method == 'POST':
        form = UploadFileForm( request.POST, request.FILES)

        actual_name = request.POST['title']

        if form.is_valid():
            handle_uploaded_file( request.FILES['file'], actual_name)
            return HttpResponseRedirect ('/upload_success')

        else:
            form = UploadFileForm()
        return render_to_response( 'polls/upload.html', {'form':form},
                 context_instance = RequestContext(request) )
    else:
        form2 = UploadFileForm()
        return render_to_response('polls/upload.html',{'form':form2},
                        context_instance=RequestContext(request) )

def uploadSuccess(request):
    return render_to_response( 'polls/upload_success.html' )
