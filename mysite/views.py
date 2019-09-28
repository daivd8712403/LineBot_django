from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
import json
import sqlite3
import os
import time
import pytz
import datetime
import json

line_bot_api = LineBotApi('ENfyQaO0OUZRgC7AOqSkbGm4JVoqH+wuEjVHsnj21iKeszVSh09W58RuRuJu/VMe7qhCDSlWNCyUiA0ZoOpY/YkNSRFg7mHaWKLUXzk4WMVA8dQzFZa0+MOMVSb3s4iA5WH8B3X0/ZzXLmxskzZUSgdB04t89/1O/w1cDnyilFU=')
parser = WebhookParser('a89f77cc9789dff49db7e7858f7ca83f')

def getDateTime_str():
    tpe = pytz.timezone('Asia/Taipei')
    utcnow = datetime.datetime.utcnow()
    tpeTime = tpe.fromutc(utcnow)
    strTime = tpeTime.strftime('%Y-%m-%d %H:%M:%S')
    return strTime

def getDateTime():
    tpe = pytz.timezone('Asia/Taipei')
    utcnow = datetime.datetime.utcnow()
    tpeTime = tpe.fromutc(utcnow)
    return tpeTime

def helloworld(request):
	return HttpResponse('Hello World')

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        #---------我是分隔線------------
        try:
            signature = request.META['HTTP_X_LINE_SIGNATURE']
            body = request.body.decode('utf-8')
            try:
                events = parser.parse(body, signature)
            except InvalidSignatureError:
                return HttpResponse()
            except LineBotApiError:
                return HttpResponse()

            for event in events:
                if isinstance(event, MessageEvent):
                    print(event.source)
                    if event.message.text == 'Hi':
                        replyMessage = "Hey there, my name is David."
                    elif event.message.text == 'David':
                        replyMessage = "What's up?"
                    else:
                        replyMessage = 'I don\'t know what "' + event.message.text + '" means.'
                    
                    try:
                        line_bot_api.reply_message(
                            reply_token = event.reply_token,
                            messages = TextSendMessage(text=replyMessage),
                            notification_disabled = True,
                            timeout = None
                        )
                    except:
                        pass
        except:
            return HttpResponse()
        #---------我是分隔線------------                
        return HttpResponse('POST')
    else:
        return HttpResponse('GET')

@csrf_exempt
def pushMessage(request):
    if request.method == 'POST':
        #---------我是分隔線------------ 
        postreqdata = json.loads(request.body.decode('utf-8'))
        line_bot_api.push_message('LINE_UUID', TextSendMessage(text=postreqdata['message']))
        conn = sqlite3.connect('AIoT.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO lightLogs VALUES ('{0}')'''.format(getDateTime_str()))
        conn.commit()
        conn.close()
        #---------我是分隔線------------ 
        return HttpResponse('OK')

def light_init(request):
    try:
        conn = sqlite3.connect('AIoT.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE lights (time text, r text, g text, b text, triggered text)''')
        cursor.execute('''INSERT INTO lights VALUES ('{0}', '0', '0', '0', '0')'''.format(getDateTime_str()))
        cursor.execute('''CREATE TABLE lightLogs (time text)''')
        conn.commit()
        conn.close()
        return HttpResponse('DB Initialize Success')
    except:
        return HttpResponse('Already Initialized')

def lightSetting(request):
    if request.method == 'POST':
        conn = sqlite3.connect('AIoT.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO lights VALUES ('{0}', '{1}', '{2}', '{3}', '0')'''.format(getDateTime_str(), 1 if request.POST['R'] == 'True' else 0, 1 if request.POST['G'] == 'True' else 0, 1 if request.POST['B'] == 'True' else 0))
        print('''INSERT INTO lights VALUES ('{0}', '{1}', '{2}', '{3}', '0')'''.format(getDateTime_str(), 1 if request.POST['R'] == 'True' else 0, 1 if request.POST['G'] == 'True' else 0, 1 if request.POST['B'] == 'True' else 0))
        conn.commit()
        conn.close()
        setting = True
        return render(request, 'app/lightSetting.html', locals())
    else:
        return render(request, 'app/lightSetting.html', locals())

@csrf_exempt
def lightQuery(request):
    if request.method == "POST":
        conn = sqlite3.connect('AIoT.db')
        cursor = conn.cursor()
        response = {}
        for row in cursor.execute('SELECT * FROM lights ORDER BY time DESC limit 1'):
            response['time'] = row[0]
            response['R'] = row[1]
            response['G'] = row[2]
            response['B'] = row[3]
            response['triggered'] = row[4]
        
        cursor.execute('''UPDATE lights SET triggered = '1' WHERE time = '{0}' '''.format(response['time']))
        conn.commit()
        conn.close()
        return HttpResponse(json.dumps(response))
    return HttpResponse()


def dashboard(request):
	today_date = getDateTime()
	date_label = []
	for i in range(7):
		temp = {}
		temp['date'] = (today_date + datetime.timedelta(days = (i-6))).strftime('%Y-%m-%d')
		temp['count'] = 0
		date_label.append(temp)

	conn = sqlite3.connect('AIoT.db')
	cursor = conn.cursor()
	list_to_show = []
	counter = 1
	try:
		for row in cursor.execute('SELECT * FROM lightLogs ORDER BY time DESC'):
			temp = {}
			temp['counter'] = counter
			temp['time'] = row[0]
			for item in date_label:
				if item['date'] == temp['time'][:10]:
					item['count'] += 1
			counter += 1
			list_to_show.append(temp)
		conn.close()
	except:
		conn.close()
		return redirect('/light_init/')
	return render(request, 'app/dashboard.html', locals())

def index(request):
	return redirect('/dashboard/')