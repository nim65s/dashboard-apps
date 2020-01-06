"""
main views for dashboard_apps
"""
from ipaddress import ip_address, ip_network

import requests
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def log(request):
    """
    just print everything out
    """
    print(f'{request = }')
    print(f'{request.scheme = }')
    print(f'{request.body = }')
    print(f'{request.path = }')
    print(f'{request.path_info = }')
    print(f'{request.method = }')
    print(f'{request.encoding = }')
    print(f'{request.content_type = }')
    print(f'{request.content_params = }')
    print(f'{request.GET = }')
    print(f'{request.POST = }')
    print(f'{request.COOKIES = }')
    print(f'{request.META = }')
    print(f'{request.headers = }')
    return HttpResponse('ok')


@csrf_exempt
def webhook(request):
    """
    got something from a github webhook
    """
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    networks = requests.get('https://api.github.com/meta').json()['hooks']
    if any(ip_address(forwarded_for) in ip_network(net) for net in networks):
        print('from github IP')
    else:
        print('not from github IP')

    return log(request)
