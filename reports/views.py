from django.http import HttpResponse

def home(request):
    return HttpResponse("Traxio is ready.")