"""Views for dashboard_apps."""
import hmac
from hashlib import sha1
from ipaddress import ip_address, ip_network

from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt

import requests


def print_request(request: HttpRequest):
    """Just print everything out."""
    print(f'request = {request}')
    print(f'request.scheme = {request.scheme}')
    print(f'request.body = {request.body!s}')
    print(f'request.path = {request.path}')
    print(f'request.path_info = {request.path_info}')
    print(f'request.method = {request.method}')
    print(f'request.encoding = {request.encoding}')
    print(f'request.content_type = {request.content_type}')
    print(f'request.content_params = {request.content_params}')
    print(f'request.GET = {request.GET}')
    print(f'request.POST = {request.POST}')
    print(f'request.COOKIES = {request.COOKIES}')
    print(f'request.META = {request.META}')
    print(f'request.headers = {request.headers}')


def log(request: HttpRequest, rep: str = 'ok') -> HttpResponse:
    """Log and return."""
    print_request(request)
    return HttpResponse(rep)


@csrf_exempt
def webhook(request: HttpRequest) -> HttpResponse:
    """
    Process request incoming from a github webhook.

    thx https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html
    """
    # validate ip source
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    networks = requests.get('https://api.github.com/meta').json()['hooks']
    if not any(ip_address(forwarded_for) in ip_network(net) for net in networks):
        print('!!! NOT from github IP:')
        print_request(request)
        return HttpResponseForbidden('Request not incoming from github hooks IP')

    # validate signature
    signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if signature is None:
        print('!!! request NOT signed:')
        print_request(request)
        return HttpResponseForbidden('Request without signature')
    else:
        algo, signature = signature.split('=')
        if algo != 'sha1':
            print('!!! signature, but not sha1:')
            print_request(request)
            return HttpResponseServerError('I only speak sha1.', status=501)

        mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
        if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
            print(f'!!! wrong signature: {mac.hexdigest()} != {signature}')
            print_request(request)
            return HttpResponseForbidden('wrong signature.')

    # process event
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    if event == 'ping':
        return log(request, 'pong')
    if event == 'push':
        return log(request, 'push event detected')

    return log(request, event)
