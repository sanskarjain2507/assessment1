from django.shortcuts import render

def index_page(request):
    return render(request,'College/login.html')