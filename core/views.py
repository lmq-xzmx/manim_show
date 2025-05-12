from django.shortcuts import render

# Create your views here.

def home(request):
    """首页视图"""
    return render(request, 'core/home.html')

def about(request):
    """关于页面"""
    return render(request, 'core/about.html')
