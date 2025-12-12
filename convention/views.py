from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Convention Home Page")

def register(request):
    return HttpResponse("Convention Registration Page")
# Create your views here.
