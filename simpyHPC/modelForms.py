from django.forms import ModelForm
from models import simFileModel
from django.shortcuts import render_to_response
from django.template import RequestContext

import os
from time import strftime

BASE_DIR = os.path.dirname( os.path.abspath(__file__) )

class simFileForm( ModelForm ):
    class Meta:
        model = simFileModel
        
        ##Enter the "name of the class"."the name   of the function" that is going to deploy your simulation:

## Handle for the file uploading and methods for handling the forms
def handle_uploaded_file( model ):

    timeID = strftime("%Y-%m-%d %H:%M:%S")

    
    destination = open( BASE_DIR+'/simpyFiles/{0}'.format( model.title )   ,'wb+')
    
   # destination = open( BASE_DIR+'/simpyFiles/{0}_{1}'.format( model.title,timeID )   ,'wb+')
    for chunk in model.file.chunks():
        destination.write( chunk )
        destination.close()


def upload_file( request ):

    if request.method == 'POST':

        form = simFileForm( request.POST, request.FILES)

        if form.is_valid():
           
            model = form.save(commit = False )
            
            handle_uploaded_file(model)

            moduleName = model.title.split('.py')[0]

            return model.findFuncArgs(request, moduleName )

        else:
            form = simFileForm()
            return render_to_response( 'polls/upload.html',{'form':form},context_instance=RequestContext(request) )
    
    
    else:
        form2 = simFileForm()
        return render_to_response('polls/upload.html',{'form':form2},context_instance=RequestContext(request) )

