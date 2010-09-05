from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
import os
BASE_DIR = os.path.dirname( os.path.abspath(__file__) )



            
def check( argStr ):

    import re
    
    validChars = r'[^\0-9:,-]'
    
    #-->check control to determine if the string that user provided:
    #1)starts and ends with numerical value
    #2)contains only values 0-9, ':', ',', '-' in order to determine the arithmetic values later
    #3)this sting must follow only one of the following cases:
    #  * Contain one or at most two ':' characters only ex. (12:100:1) or (12:100)
    #  * Contain one '-' characters only ex. (12-100)
    #  * Contain as many ',' characters wanted ex. (12,100,200,3000...)
    
    if ( re.search(validChars, argStr) or (not argStr[0].isdigit() ) or (not argStr[ len(argStr)-1 ].isdigit() ) ):
        return 1
    
    elif argStr.count(':') > 2 or argStr.count('-')>1:
        return 2
    
    elif not( argStr.isdigit() or ( not(argStr.count(':')) and not(argStr.count(',')) and argStr.count('-') ) or ( not(argStr.count(':')) and not(argStr.count('-')) and argStr.count(',') ) or ( not(argStr.count(',')) and not(argStr.count('-')) and argStr.count(':'))  ):

        return 3
    else:
        return 0

def partRange2param( string ):
    temp = string.partition(':')
    num1 = int(temp[0])
    num2 = int(temp[2])
    
    args = [num1,num2]
    return range(*args)
                                
                                    
def partRange3param( string ):
    temp = string.partition(':')
    num1= int( temp[0] )
    
    temp2 = temp[2].partition(':')
    num2 = int( temp2[0] )
    
    num3 = int( temp2[2] )
    
    args = [num1,num2,num3]
    
    return range(*args)


def determineForm( string ):
    
    tempStr = string
    
    #check for [1:100:10] or [1:10] form 
    
    if ( (tempStr.find(':')) != -1 ):
        tempStr = tempStr.replace(':','',1)
        if (tempStr.find(':')) != -1 :
            #it is a type of [1:100:10] range
            return partRange3param(string)

        else:
            return partRange2param(string)
    else:
        #else its only a number so we dont do anything    
        return [int(string)]


def sim( request ):
    
    
    from tasks import simulate
    from celery.task.sets import subtask
    from celery.task.sets import TaskSet


    arglist = request.POST.items()

    primitiveDict= dict()
    
    for arg in arglist:
        
        if arg[0] == 'csrfmiddlewaretoken':
            del arg
        elif arg[0] == 'actualfname':
            actualfname = arg[1]
            del arg
        elif arg[0] == 'className':
            className = arg[1]
            del arg
        elif arg[0] == 'funcName':
            funcName = arg[1]
            del arg                          
        else:
            keyword = '{0}'.format( str(arg[0]) )

            error_code = check( arg[1] )

            print error_code
            
            if ( error_code == 0 ):
                values = determineForm(arg[1])
                
                primitiveDict[keyword] =  values #values is already an int
            
            elif ( error_code == 1 ):
                return HttpResponse('This is an error that shouldnt occur.Contact the administrators'  )
                #return render_to_response('polls/errorSimFields.html', { 'error1': True, 'error2':False, 'error3':False } )

            elif ( error_code == 2 ):
                return HttpResponse('This is an error that shouldnt occur.Contact the administrators'  )
                #return render_to_response('polls/errorSimFields.html', { 'error1': False, 'error2':True, 'error3':False } )
            
            elif ( error_code == 3 ):
                return HttpResponse('This is an error that shouldnt occur.Contact the administrators'  )
                #return render_to_response('polls/errorSimFields.html', { 'error1': False, 'error2':False, 'error3':True } )

            else:
                return HttpResponse('This is an error that shouldnt occur.Contact the administrators'  )
    #at this point we find ourselves with a dictionary filled with keywords
    #which represent the actual arguments of the function we want to call
    #and a list of values which were calcualted from our special determine 
    #form method.
    ####################################################################
    #What we really want to do is to calculate all the possible matches of these
    #arguments and then map them,in each column of the list to be producted,
    #with the actual keyword we considered before--which would be also the 
    #arguments name.

    import itertools

    lstUnmappedArgs = list()
    for i in itertools.product( *(primitiveDict.values()) ):
        lstUnmappedArgs.append(i)

    #list to hold all the subtasks of the simulation to be
    taskList = list()
    
    #those keys are the actual parameters of the function to be called
    keys = primitiveDict.keys()
    
    #another list to hold the sequence of the arguments passed in
    #each simulation in order to store them later in the database
    argList = list()

    for i in lstUnmappedArgs:

        argList.append( (zip(keys,i) ) )

        taskList.append(  simulate.subtask( (dict(zip(keys,i)),
                            actualfname,className, funcName) )    )
    #    async_value = simulate.delay( dict(zip(keys,i)), actualfname,
    #                                  className, funcName)



    job = TaskSet( tasks =  taskList  )

    result = job.apply_async()
    
    result.ready()  # has all subtasks completed?
    
    result.successful() # was all subtasks successful?
    
    resultsList = result.join()

    #list to map the argument tuples for each task with the corresponding
    #return value

    argReturnValueList = list( zip( resultsList, argList ) )

    sqlStoring( argReturnValueList , className, funcName, actualfname )

    return HttpResponse('%s' %  resultsList)



def sqlStoring(  argReturnValueList , className, funcName, actualfname ):

    import sqlite3
    from time import strftime

    timeID = strftime("%Y-%m-%d %H:%M:%S")
    
    sqliteDBpath = BASE_DIR+'/simDBs/{0}_simResults_{1}'.format(actualfname,timeID)
    conn = sqlite3.connect( sqliteDBpath )
    
    c = conn.cursor()

    # Create table
    c.execute("create table simResults(results text, arguments text )")
    c.execute( "create table simDetails( class text, function text, filename text )" )



    # Insert a row of data
    for i in argReturnValueList:
    
        argumentsFinal = '{0}'.format( i[1] )

        c.execute("insert into simResults values (?,? )",[ i[0] , argumentsFinal ] )

    c.execute("insert into simDetails values( ?,?,?)",[className,funcName,actualfname] )

    # Save (commit) the changes
    conn.commit()

    # We can also close the cursor if we are done with it
    c.close()
    conn.close()
