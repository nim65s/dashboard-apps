"""Views for dashboard_apps."""
import hmac
import json
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
    print('print_request')
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


def log(request: HttpRequest) -> HttpResponse:
    """Log and return."""
    print_request(request)
    return HttpResponse('ok')


@csrf_exempt
def github_webhook(request: HttpRequest) -> HttpResponse:
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

    body = json.loads(request.body)

    # process event
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    if event == 'ping':
        print('pong')
    elif event == 'push':
        print('push event detected')
        if body['ref'] == 'refs/heads/master':
            print(' + on the master branch')
        elif body['ref'] == 'refs/heads/devel':
            print(' + on the devel branch')
        else:
            print(' + ref:', body['ref'])
    elif event == 'pull_request':
        print('pull request detected')
        if body['action'] in ['opened', 'synchronize']:
            print(' + opened / synchronized')
            print(' - with number', body['number'])
            print(' - on commit', body['pull_request']['head']['sha'])
            print(' - from repo', body['pull_request']['head']['repo']['full_name'])
            print(' - on ref', body['pull_request']['head']['ref'])
            print(' - git url', body['pull_request']['head']['repo']['git_url'])
            print(' - ssh url', body['pull_request']['head']['repo']['ssh_url'])
            print(' - clone url', body['pull_request']['head']['repo']['clone_url'])
    elif event == 'check_suite':
        print('check suite detected')
    else:
        print(f'*** event: {event}')

    return log(request)


@csrf_exempt
def gitlab_webhook(request: HttpRequest) -> HttpResponse:
    """Process request incoming from a gitlab webhook."""

    # validate ip source
    forwarded_for = ip_address(request.META.get('HTTP_X_FORWARDED_FOR'))
    if forwarded_for not in settings.GITLAB_IPS:
        print('!!! NOT from gitlab IP:')
        print_request(request)
        return HttpResponseForbidden('Request not incoming from gitlab IP')

    # validate token
    token = request.META.get('HTTP_X_GITLAB_TOKEN')
    if token is None:
        print('!!! NO token')
        print_request(request)
        return HttpResponseForbidden('Request without token')
    if token != settings.GITLAB_WEBHOOK_KEY:
        print('!!! WRONG token')
        print_request(request)
        return HttpResponseForbidden('Request with wrong token')


    return log(request)
