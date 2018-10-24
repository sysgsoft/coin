import os.path
import sys
import yaml
import pprint
from config import *
import pymysql
import pandas as pd
from django.contrib.admin.templatetags.admin_list import results
import requests
import json
import random
import numpy as np
import requests
import itertools
from bs4 import BeautifulSoup
import re
import urllib
import time
import os
from views import *
from api.views import *
import pyodbc
import pandas



try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai


global location
location=[]

global bedroom
bedroom=0
global CONN
CONN=False
global customer_details_siteid
customer_details_siteid=pd.DataFrame()

global context

def connect_to_db():
    global conn
    global CONN

    conn = pyodbc.connect(driver = '{ODBC Driver 17 for SQL Server}', server = '185.168.192.104', 
                      database = 'LoyaltyCRM', uid = 'sysgloyalty', pwd = 'loyalty2017', autocommit=True)
    CONN=True
    return conn


#function to calculate age from dob
from datetime import date

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))  

def age_group(age):
    if 0<=age<20:
        return("<20")
    elif 20<=age<40:
        return("20-39")
    elif 40<=age<60:
        return("40-59")
    elif age>59:
        return(">59")

def select_segment(segment_name):
    #selecting card numbers in a particular customer segment
    segment_card=customer_segmentation[customer_segmentation["Segment"]==segment_name]["CardNo"].values
    return segment_card




def call_api(dict_input):
    global location
    print location
    global out_dict
    global conn
    global CONN
    global customer_details_siteid
    out_dict = {}
    out_dict['messageText'] = []
    out_dict['messageSource'] = 'messageFromBot'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'de'
    request.resetContexts = False
    request.session_id = dict_input['user_id']
    request.query = dict_input['messageText']
    #print(request.query)
    
      
    response = yaml.load(request.getresponse())
    
	
    speech=response['result']['fulfillment']['messages'][0]['speech']
	
    if (CONN):
	pass
    else:
	conn=connect_to_db()
 
    if response['result']['metadata']['intentName'] == 'Default Welcome Intent':
	out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin': [{"type":"button",
      "label":top_level_buttons}]}]
        
    	return out_dict

 
    elif "Please select one location..!" in speech:
	out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin': [{"type":"button",
      "label":cities}]}]
    	return out_dict



    elif "Profit data has to be displayed" in speech:
	
	city=response["result"]["parameters"]["any"]
	location=[]
	location.append(city)
	To_user="The brief profit statistics for "+city+" is as follows: Today 100 euro This week 250 euro This month 1850 Euro This quarter 3000 Euro This year 1000 Euro"               
	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[{"type":"button","label":profit_analysis}]}]
        
    	return out_dict



    elif "month wise profit plot has to be displayed" in speech:
	import calendar
        MonthProfit=pandas.read_sql("select * from AI_MonthWiseProfit",conn)
	MonthProfit_=MonthProfit[MonthProfit['Location'].str.contains(location[-1])&MonthProfit['Month'].astype(str).str.contains('2018')]
	maxmonth=calendar.month_name[MonthProfit_.loc[MonthProfit_['Profit'].idxmax()]['Month'].month]
	minmonth=calendar.month_name[MonthProfit_.loc[MonthProfit_['Profit'].idxmin()]['Month'].month]
	To_user1=''
	for index,row in MonthProfit_.iterrows():
    		To_user1+= str(row.Month.date())+' : '+str(row.Profit)+' '
	To_user='In this year, '+location[-1]+' got the most profit in '+maxmonth+' and the least in '+minmonth+'. Here is the detailed report up to this month:   '+ To_user1
	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    	return out_dict

    elif "quarter wise profit plot has to be displayed" in speech:
        quarter_profit=pandas.read_sql("select * from AI_QuarterWiseProfit",conn)
	quarter_profit_=quarter_profit[(quarter_profit['Location'].str.contains(location[-1]))&(quarter_profit['year']==2018)]
	To_user1=''
	for index,row in quarter_profit_.iterrows():
    		To_user1+= str(row.Quarter)+' : '+str(row.Profit)+' '
	To_user='The quarter wise profit details for this year in '+location[-1]+' is given. Please have a look:  '+To_user1
    	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    	return out_dict

    elif "year wise profit plot has to be displayed" in speech:
        out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin':[]}]
	############ DB Querry for profit vs years #############
    	return out_dict

    elif "Kindly select one option" in speech:
        out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin': [{"type":"button",
      "label":demographic_profit}]}]
	############ DB Querry for profit vs years #############
    	return out_dict

    elif "location wise profit plot has to be displayed" in speech:
	
	LocationProfit=pandas.read_sql("select * from AI_LocationProfitAnalysis",conn)
	To_user1=''
	for index,row in LocationProfit.iterrows():
    		To_user1+= str(row.Location)+' : '+str(row.Profit)+'  '
	
	maxplace=LocationProfit.loc[LocationProfit['Profit'].idxmax()]['Location']
	To_user2=maxplace+' has made the highest profit among all. Here is the top '+str(len(LocationProfit))+'  locations along with their profit deatils.'+To_user1
	out_dict['messageText']= [{'msg_text':To_user2,'msg_plugin':[]}]
    	return out_dict
	

    elif "demographics profit data has to be displayed" in speech:
	
	plot=response["result"]["parameters"]["Profit-demographic"]
	
	if plot=="gender wise profit analysis":
		transaction_data=pandas.read_sql("select * from AI_GenderProfitAnalysis",conn)
		df=transaction_data[transaction_data['Location'].str.contains(location[-1])]
		
		To_user='In '+str(location[-1])+', a total profit of '+str(df[df['Gender']=='Male'].Profit.values[0])+' is contributed by men and a total of '+str(df[df['Gender']=='Female'].Profit.values[0])+' is contributed by women'
		out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    		return out_dict
	
	if plot=="age wise profit analysis":
		AgeProfit=pandas.read_sql("select * from AI_AgeProfitAnalysis",conn)
		AgeProfit_=AgeProfit[AgeProfit['Location'].str.contains(location[-1])]
		maxgroup=AgeProfit_.loc[AgeProfit_['Profit'].idxmax()]['Age_group']
		To_user1=''
		for index,row in AgeProfit_.iterrows():
    			To_user1+= str(row.Age_group)+' : '+str(row.Profit)+' '
		To_user= 'In '+location[-1]+', Among the four groups, People who belong to age group '+maxgroup+' has contributed more to total profit. Here is the detailed report: '+To_user1
		out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    		return out_dict




    elif "customer analysis" in speech:
	
	city=response["result"]["parameters"]["any"]
	location=[]
	location.append(city)
	
	
        #fetching customer segmentation table
	customer_segmentation=pandas.read_sql("select * from AI_CustomerSegmentation",conn)
	#fetching customer details
	customer_details=pandas.read_sql("select lc.CardNo,ps.[DateOfBirth], ps.[GenderId],sy.SiteId from [dbo].[LoyaltyCards] lc inner join [dbo].[PersonalInfo] ps on lc.MemberId=ps.MemberId inner join [dbo].[Sysuser] sy on ps.MemberId=sy.Id where sy.ClientId=1127 and UserType=3",conn)
	customer_details=customer_details.dropna()
	site_details=pandas.read_sql("select Id as SiteId, Name as location from Site",conn)
	customer_details_=customer_details.merge(site_details,on="SiteId")
	customer_details_siteid=customer_details_[customer_details_['location'].str.contains(location[-1])]
	out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin':[{"type":"button","label":customer_analysis}]}]
	return out_dict


    elif "customer gender analysis has to be displayed" in speech:
        gender=[1,2]
	gender_details=customer_details_siteid.GenderId.value_counts().rename_axis('GenderId').reset_index(name='counts')
	if len(gender_details)<2:
    		if gender_details.GenderId[0]==1:
        		gender_details=gender_details.append(pandas.DataFrame([[2,0.0]],columns=['GenderId','counts']),ignore_index=True)
    		else:
        		gender_details=gender_details.append(pandas.DataFrame([[1,0.0]],columns=['GenderId','counts']),ignore_index=True)
	gender_details["Gender"]=["Male" if x==1 else "Female" for x in gender_details.GenderId.values]
	To_user='In '+location[-1]+', '+str(int(gender_details[gender_details['Gender']=='Male'].counts.values[0]))+' of the total customers are men and '+str(int(gender_details[gender_details['Gender']=='Female'].counts.values[0]))+' are women'
	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    	return out_dict



    elif "customer age based analysis has to be displayed" in speech:
	#age calculation
	customer_details_siteid["age"]=[calculate_age(customer_details_siteid.DateOfBirth.values[i]) for i in range(len(customer_details_siteid.DateOfBirth.values))]
	customer_details_siteid["age_group"]=[age_group(x) for x in customer_details_siteid.age.values]
	customer_age_group_count=customer_details_siteid.age_group.value_counts().rename_axis('age_group').reset_index(name='counts')
        age_list=["<20","20-39","40-59",">59"]
	#handling missed age groups with count zero
	identified_age_groups=list(customer_age_group_count["age_group"].values)
	missed_group=list(set(age_list) - set(identified_age_groups))
	new_rows=[[x,0.0] for x in missed_group]
	customer_age_group_count=customer_age_group_count.append(pandas.DataFrame(new_rows,columns=['age_group','counts']))
	To_user1=''
	for index,row in customer_age_group_count.iterrows():
    		To_user1+= str(row.age_group)+' : '+str(row.counts)+' '
	To_user= 'Here is the number of customers who comes under different age groups:  '+To_user1
	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin':[]}]
    	return out_dict
    	


    elif "Please select a segment to continue with" in speech:
        out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin': [{"type":"button",
      "label":customer_segments}]}]
    	return out_dict


    elif "segmentation analysis options" in speech:
	tmp=response["result"]["parameters"]["Customer-segments"]
	To_user="Number of "+str(tmp)+" customers are: 1235"        
	out_dict['messageText']= [{'msg_text':To_user,'msg_plugin': [{"type":"button","label":customer_segments_options}]}]
    	return out_dict


    elif "ai prediction" in speech:
	out_dict['messageText']= [{'msg_text':'Please select one option to continue with','msg_plugin': [{"type":"button","label":prediction_options}]}]
    	return out_dict


    elif "Please choose your own amenities..!" in speech:
        out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin': [{"type":"popup",
      "label":amenities}]}]
    	return out_dict

    elif "Perfect..! Here are the list of homes with your preference..!" in speech:
        out_dict['messageText'].append(response['result']['fulfillment']['messages'][0]['speech'])
	global location
	global bedroom
	print bedroom
	bedroom=int(bedroom)
	loc=str(location[0])
	print loc
	list__=result_(loc,bedroom)
	out_dict["plugin"] = {'name': 'link', 'type': 'products', 'data': list__}
	print out_dict
    	return out_dict

    else:
	out_dict['messageText']= [{'msg_text':response['result']['fulfillment']['messages'][0]['speech'],'msg_plugin':[]}]
	
	return out_dict



