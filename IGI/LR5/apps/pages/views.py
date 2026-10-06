from django.shortcuts import render
from .models import (AboutCompany, News, FAQ, EmployeeContact, Vacancy)
from django.utils import timezone
from datetime import timezone as dt_timezone
import calendar
import requests

def about_page(request):
    company = AboutCompany.objects.first()

    return render(request, 'pages/about.html', {'company': company})

def news_list(request):
    news = News.objects.all().order_by('-created_at')

    return render(request, 'pages/news.html', {'news': news})

def faq_page(request):
    faqs = FAQ.objects.all()

    return render(request, 'pages/faq.html', {'faqs': faqs})

def contacts_page(request):
    contacts = EmployeeContact.objects.all()

    return render(request, 'pages/contacts.html', {'contacts': contacts})

def vacancies_page(request):
    vacancies = Vacancy.objects.all()

    return render(request, 'pages/vacancies.html', {'vacancies': vacancies})


def privacy_page(request):
    return render(request, 'pages/privacy.html')

def external_api_page(request):
    cat_fact = 'Факт недоступен'
    dog_image = None
    try:
        cat_data = requests.get('https://catfact.ninja/fact', timeout=5).json()
        cat_fact = cat_data.get('fact', 'Факт недоступен')

    except Exception:
        pass

    if request.user.is_authenticated:
        try:
            dog_data = requests.get('https://dog.ceo/api/breeds/image/random', timeout=5).json()
            dog_image = dog_data.get('message')
            
        except Exception:
            pass

    context = {'cat_fact': cat_fact,'dog_image': dog_image,}
    return render(request, 'pages/external_api.html', context)

def timezone_page(request):
    utc_time = timezone.now().astimezone(dt_timezone.utc)
    local_time = timezone.localtime()
    timezone_name = timezone.get_current_timezone_name()
    current_year = local_time.year
    current_month = local_time.month
    text_calendar = calendar.month(current_year,current_month)
    context = {'utc_time': utc_time, 'local_time': local_time, 'timezone_name' : timezone_name, 'calendar': text_calendar,}

    return render(request, 'pages/timezone.html', context) 
