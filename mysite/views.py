from django.http import HttpResponse

def helloworld(request):
    return HttpResponse('Im David Hello World!')