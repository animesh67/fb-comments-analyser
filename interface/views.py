from django.shortcuts import render
from django.http import HttpResponse
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from scrapyd_api import ScrapydAPI
from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import redirect
import time
import pandas as pd
from googletrans import Translator
from .models import User
from .models import Source_detail
# Create your views here.

scrapyd = ScrapydAPI('http://localhost:6800')


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url) # check if url format is valid
    except ValidationError:
        return False

    return True


def home(request):
	return render(request, 'home.html', {})

def details(request):
	if request.method == 'POST':
		url1= request.POST.get('link')
		url2=request.POST.get('link1')
		id1= request.POST.get('mail')
		pass1 = request.POST.get('pass')
		if not is_valid_url(url1):
			return render(request,'error.html',{})
		
		if url2:
			task = scrapyd.schedule('fbcrawl', 'comments',email=id1, password=pass1, page=url2)
			return redirect('/status?task_id='+task)
		else:
			task = scrapyd.schedule('fbcrawl', 'comments',email=id1, password=pass1, post=url1)
			return redirect('/status?task_id='+task)

	return render(request,'details.html',{})

def status(request):
	task_id=request.GET.get("task_id",'')
	print(task_id)
	if request.method=='POST':
		prevstat=scrapyd.cancel('fbcrawl',task_id)
		return render(request,'cancel.html',{})

	status = scrapyd.job_status('fbcrawl',task_id)
	print(status)
	if(status=='finished'):
		try:
			df=pd.read_csv('comment.csv');
		except pandas.io.common.EmptyDataError:
			return redirect('/email_error/')
		dowloadcleaned()
		return redirect('/finish/')
	return render(request,'task.html',{})


def email_error(request):
	return render(request,'emailerror.html',{})

def finish(request):
	if request.method=='POST':
		return download()
	return render(request,'finish.html',{})
	
def download():
	test_file = open('comment.csv', 'rb')
	response = HttpResponse(content=test_file)
	response['Content-Type'] = 'text/csv'
	response['Content-Disposition'] = 'attachment; filename="data.csv"'
	return response



final_list=[]
def deEmojify(inputString):
    text = inputString.encode('ascii', 'ignore').decode('ascii')
    final_list.append(text)

def dowloadcleaned():
	translator = Translator()
	df = pd.read_csv('comment.csv')
	#df['text'] = df['text'].astype(str)
	df = df.applymap(str)
	comm = df['text']
	#print(df.text.dtype)
	final=[]
	source = df['source'].tolist()
	source_url = df['source_url'].tolist()

	for i in range(len(comm)):
		final.append(comm.iloc[i])

	print(final)
	for i in range(len(final)):
		deEmojify(final[i])

	print(final_list)

	all_comments =[]

	translatedList = translator.translate(final_list, dest='en')
	for translated in translatedList:
		all_comments.append(translated.text)

	print(all_comments)
	final_df = pd.DataFrame(list(zip(source, source_url, all_comments)), columns=['source', 'source_url', 'text'])
	final_df.to_csv('translate.csv',index=False)
 

def cleaned_data(request):
	if request.method =='POST':
		test_file = open('translate.csv', 'rb')
		response = HttpResponse(content=test_file)
		response['Content-Type'] = 'text/csv'
		response['Content-Disposition'] = 'attachment; filename="translated_comments.csv"'
		return response
	return render(request,'cleaneddata.html',{})


def result(request):
	if request.method=='POST':
		name =request.POST.get("Username")
		pas=request.POST.get("pass")
		print(name,pas)
		b=User(username=name, password=pas)
		if b:
			return HttpResponse("USER DOES NOT EXIST")
		else:
			return 

	return render(request,'result.html',{})


def analyse(request):
	if request.method =='POST':
		test_file = open('translate_result.csv', 'rb')
		response = HttpResponse(content=test_file)
		response['Content-Type'] = 'text/csv'
		response['Content-Disposition'] = 'attachment; filename="analysed_comments.csv"'
		return response
	return render(request,'analyse.html',{})