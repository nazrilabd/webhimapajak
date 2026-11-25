from django.shortcuts import render

def home_view(request):
    return render(request, 'index.html')

def admin_dashboard_view(request):
    return render(request, 'admin.html')

def login_view(request):
    return render(request, 'login.html')
