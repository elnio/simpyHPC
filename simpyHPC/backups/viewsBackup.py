# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect

from django.core.urlresolvers import reverse
from mysite.polls.models import Poll, Choice
from django.template import RequestContext,Context, loader#dont think i need that if i use shortcuts
from django.shortcuts import render_to_response, get_object_or_404

from django.http import Http404

#def index(request):
#    return HttpResponse( "Hello world, You are at the poll index")

#def index( request ):
#    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
#    output = ', '.join( [p.question for p in latest_poll_list] )
#    return HttpResponse(output)

##def index( request ):
##    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
##    t = loader.get_template( 'polls/index.html')
##    c = Context( { 'latest_poll_list' : latest_poll_list, } )
##    return HttpResponse( t.render( c ) )

##def index( request ):
##    latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
##    return render_to_response( 'polls/index.html',
##                               {'latest_poll_list':latest_poll_list})


#def detail( request, poll_id ):
#    return HttpResponse("You're looking at poll %s" % poll_id)

#def detail(request, poll_id ):
#    try:
#        p = Poll.objects.get( pk = poll_id )
#    except Poll.DoesNotExist:
#        raise Http404
#    return render_to_response( 'polls/details.html',
#                              { 'poll': p } )

##modified in order to work with csrd_token and stuff
#def detail(request, poll_id ):
#    p = get_object_or_404( Poll, pk = poll_id)
#    return render_to_response( 'polls/detail.html',
#                            { 'poll':p} )


##def detail(request, poll_id):

##    p = get_object_or_404( Poll, pk=poll_id)
##    return render_to_response('polls/detail.html',
##                        { 'poll':p},
##                        context_instance = RequestContext(request)
##                        )

#def results( request, poll_id ):
#    return HttpResponse( "You're looking at the result of poll %s." % poll_id)


##def results(request, poll_id):
###    p = get_object_or_404( Poll, pk = poll_id)

##    return render_to_response('polls/results.html', {'poll':p} )


def sim(request):
    from tasks import simulate
    import a
    import inspect

    arg_dict = inspect.getargspec(a.MMCCmodel.run).args

    return render_to_response('polls/simFields.html', {'arg_dict':arg_dict} )


   #this would be the 'self' argument which is not needed for   the call


   ## async_value = simulate.delay( 
   ## reserved =  3, density = 3,stime = 1.0, rate = 4.0,
   ## maxCustomers = 24000, scale_rate = 18.0,rand_seed = 78 )
   #  return HttpResponse( async_value)
   


#def vote( request, poll_id ):
#    return HttpResponse( "You're voting on poll %s" % poll_id)


def showPollFields( request ):
    from mysite.polls.forms import PollForm

    data = Poll.objects.get( pk=1 )
    forma = PollForm( instance = data)

    return render_to_response('polls/lef.html',
            {'forma':forma,},
         context_instance = RequestContext(request) )



def vote(request, object_id):

    p=get_object_or_404( Poll, pk=object_id)
    try:
        selected_choice = p.choice_set.get( pk=request.POST['choice'] )
    except (KeyError, Choice.DoesNotExist ):

             #return render_to_response('polls/detail.html',
             #changed poll to object to use general views
            return render_to_response('polls/poll_detail.html',
                    
                #changed poll to object to use general views
                {'object':p, 'error_message':"You didn't select a choice",},
                context_instance = RequestContext(request) )
    else:
        
        selected_choice.votes += 1
        selected_choice.save()

     #   return HttpResponseRedirect( reverse('mysite.polls.views.results',
     #                                           args=(p.id,) ) )
    #in order to use generic views we changed the line above to:
        return HttpResponseRedirect( reverse('poll_results', args=(p.id,)))






