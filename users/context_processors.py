
def cookies_context(request):
    """Add cookies consent status to all templates"""
    cookies_accepted = request.COOKIES.get('cookies_accepted', 'false') == 'true'
    show_cookies_banner = not cookies_accepted
    
    return {
        'cookies_accepted': cookies_accepted,
        'show_cookies_banner': show_cookies_banner,
    }
