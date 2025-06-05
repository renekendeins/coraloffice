
from django.shortcuts import render
from django.http import HttpResponse

class CookiesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cookies consent banner context to all responses
        if not hasattr(request, 'cookies_accepted'):
            request.cookies_accepted = request.COOKIES.get('cookies_accepted', 'false') == 'true'
        
        return response
