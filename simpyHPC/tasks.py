from celery.decorators import task
from django.http import HttpResponse
from celery.task.sets import subtask
import sys
import os
BASE_DIR = os.path.dirname( os.path.abspath(__file__) )

@task()
def simulate( kwargs, actualfname, className, funcName ):
   
    sys.path.append(BASE_DIR+'/simpyFiles/')
    

    if actualfname in sys.modules:

        module = sys.modules[actualfname]
        reload( module)
    else:
        
        module = __import__(actualfname)


    klass = getattr(module,className)
    function = getattr(klass(),funcName)
    
    return_value = function( **kwargs )
    
    print return_value

    return return_value

@task()
def add(x,y):
	return x+y
