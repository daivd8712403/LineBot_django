from django.http import HttpResponse
from django.shortcuts import render
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

line_bot_api = LineBotApi('Channel_access_token')
parser = WebhookParser('Channel_secret')

def helloworld(request):
    return HttpResponse('Im David Hello World!')

def callback(request):
    if request.method == 'POST':
        return HttpResponse('OK')
    else:
        return HttpResponse('OK')