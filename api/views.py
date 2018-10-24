from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from typing import Dict, List, Any

from . models import employees
from rest_framework import status
from . serializers import employeesSerializer
from rest_framework import viewsets
from config import *
from api.externel_api import call_api
import requests
from rest_framework.decorators import permission_classes
from rest_framework import permissions
import apiai
import yaml
import datetime
import json
from config import *
currentTime = datetime.datetime.now()




def page_reload_operation(question):
    question['messageSource'] = 'messageFromBot'
    question['messageText']= [{'msg_text':welcome_note,'msg_plugin': [{"type":"button",
      "label":top_level_buttons}]}]
    return question

def clear_context(user_id):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'de'
    request.resetContexts = True
    request.session_id = user_id
    request.query = 'hi'
    response = yaml.load(request.getresponse())
    


# Create your views here.
@permission_classes((permissions.AllowAny,))


class TestAPI(viewsets.ViewSet):
 

    def create(self, request):
        question_user = request.data

        sessionid = question_user['user_id']
	CACHE_ID=sessionid


        user_input = question_user['messageText']

        if question_user['messageSource'] == 'userInitiatedReset':
            clear_context(CACHE_ID)
            question = page_reload_operation(question_user)
	    print question
            return Response(question)

        
        question=call_api(question_user)
 
	print question
    	return Response(question)





  





