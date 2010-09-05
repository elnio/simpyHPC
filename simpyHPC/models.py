from django.db import models
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect


from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext,Context
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404

class simFileModel( models.Model):

    title = models.CharField( max_length = 20 )
    file = models.FileField( upload_to = 'none' )
    className = models.CharField( max_length = 50)
    funcName = models.CharField( max_length = 50)

    def __unicode__( self ):
        return '{0}.{1}'.format(self.className, self.funcName)


    def getClass(self):
        return className
    def getFunc( self ):
        return funcName

    def getClassFunc( self ):
        return '{0}.{1}'.format( self.className, self.funcName )
    
    def findFuncArgs( self,request, actualfname ):

        import sys
        import os
        BASE_DIR = os.path.dirname( os.path.abspath(__file__) )

        sys.path.append(BASE_DIR+'/simpyFiles/')
        

        #if the module has been imported before then we need to 
        #reload it in order to see the changes if there are any

        
        if actualfname in sys.modules:
            module = reload( sys.modules[actualfname])
        else:
            module = __import__(actualfname)




        import inspect 

        klass = getattr(module, self.className)
        function = getattr(klass, self.funcName)

        arg_dict = inspect.getargspec( function ).args
        
        del arg_dict[0]
        
        return render_to_response('polls/simFields.html',
                {'arg_dict':arg_dict, 'actualfname':actualfname,
                 'className':self.className, 'funcName':self.funcName},
                context_instance=RequestContext(request))
    


