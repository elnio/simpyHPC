from django.db import models

# Create your models here.
import datetime

class Poll(models.Model):
    question = models.CharField( max_length = 200)
    pub_date = models.DateTimeField('date published')
    
    #!must enter this every time and i should search why more in depth
    def __unicode__( self ):
        return self.question
    
    #Just a check to determine if the polls was published today
    def was_published_today( self ):
        return self.pub_date.date == datetime.date.today()
    
    was_published_today.short_description = 'Published today?'

class Choice( models.Model ):
    poll = models.ForeignKey( Poll)
    choice = models.CharField( max_length = 200 )
    votes = models.IntegerField()
   
    def __unicode__( self ):
        return self.choice 

