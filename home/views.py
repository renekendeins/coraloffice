
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

def legal_notice(request):
    return render(request, 'home/legal_notice.html')

def privacy_policy(request):
    return render(request, 'home/privacy_policy.html')

def cookies_policy(request):
    return render(request, 'home/cookies_policy.html')

def cookies_settings(request):
    if request.method == 'POST':
        # Handle cookies preferences
        essential_cookies = request.POST.get('essential_cookies', 'on')
        analytics_cookies = request.POST.get('analytics_cookies', 'off')
        marketing_cookies = request.POST.get('marketing_cookies', 'off')
        
        response = render(request, 'home/cookies_settings.html', {
            'message': 'Cookies preferences updated successfully!',
            'essential_cookies': essential_cookies,
            'analytics_cookies': analytics_cookies,
            'marketing_cookies': marketing_cookies,
        })
        
        # Set cookies preferences
        response.set_cookie('cookies_accepted', 'true', max_age=365*24*60*60)
        response.set_cookie('essential_cookies', essential_cookies, max_age=365*24*60*60)
        response.set_cookie('analytics_cookies', analytics_cookies, max_age=365*24*60*60)
        response.set_cookie('marketing_cookies', marketing_cookies, max_age=365*24*60*60)
        
        return response
    
    # Get current preferences
    essential_cookies = request.COOKIES.get('essential_cookies', 'on')
    analytics_cookies = request.COOKIES.get('analytics_cookies', 'off')
    marketing_cookies = request.COOKIES.get('marketing_cookies', 'off')
    
    return render(request, 'home/cookies_settings.html', {
        'essential_cookies': essential_cookies,
        'analytics_cookies': analytics_cookies,
        'marketing_cookies': marketing_cookies,
    })
