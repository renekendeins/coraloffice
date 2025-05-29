
from django.shortcuts import render

def home(request):
    context = {
        'page_title': 'Welcome to CoralOffice',
        'featured_services': [
            {
                'title': 'Dive Course Management',
                'description': 'Manage PADI, SSI, and other certification courses with ease.',
                'icon': '🤿'
            },
            {
                'title': 'Equipment Rental',
                'description': 'Track and manage diving equipment rentals and maintenance.',
                'icon': '⚙️'
            },
            {
                'title': 'Trip Planning',
                'description': 'Organize diving trips and boat schedules efficiently.',
                'icon': '🚤'
            },
            {
                'title': 'Customer Management',
                'description': 'Keep track of customer certifications and diving history.',
                'icon': '👥'
            }
        ],
        'dive_sites': [
            {'name': 'Coral Garden Reef', 'depth': '12-18m', 'difficulty': 'Beginner'},
            {'name': 'Blue Hole Adventure', 'depth': '25-40m', 'difficulty': 'Advanced'},
            {'name': 'Shipwreck Explorer', 'depth': '20-30m', 'difficulty': 'Intermediate'},
            {'name': 'Night Dive Special', 'depth': '8-15m', 'difficulty': 'Open Water'},
        ]
    }
    return render(request, 'home/index.html', context)

def about(request):
    return render(request, 'home/about.html')

def services(request):
    return render(request, 'home/services.html')

def contact(request):
    return render(request, 'home/contact.html')
