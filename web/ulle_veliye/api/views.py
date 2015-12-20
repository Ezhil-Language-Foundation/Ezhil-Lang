# -*- coding: utf-8 -*-

import json
import tempfile

from django.http import JsonResponse, HttpResponse
from django.http.multipartparser import parse_header
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from six import string_types

import envoy
# from ezhil import EzhilFileExecuter       
# utils


def is_json_request(content_type):
    """Return the content type is json.
    """
    lhs, rhs = parse_header(content_type)
    return lhs == 'application/json'


def validate(data):
    code = data.get('code')
    if not code:
        return (False, {'code': 'Field is required'})
    if isinstance(code, string_types):
        return (True, '')
    return (False, {'code': 'value should be string or unicode or byte'})


def execute(code):
    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(code.encode('utf-8'))
        tmp_file.flush()
        print("Input file: {0}".format(tmp_file.name))
        TIMEOUT = getattr(settings, 'TIMEOUT', 10)
        # obj = EzhilFileExecuter(file_input=tmp_file.name, redirectop=True,
        #                         TIMEOUT=TIMEOUT, debug=True)
        # obj.run()
        # res = obj.get_output()
        cmd = "ezhili {0}".format(tmp_file.name)
        res = envoy.run(cmd, timeout=TIMEOUT)
        std_out = res.std_out
        print(std_out)
        return std_out


def handle_request(data):
    res = validate(data)
    if res[0]:
        result = execute(code=data['code'])
        output = {'result': result}
        return JsonResponse(data=output)
    return JsonResponse(data=res[1], status=400)


# Views


@csrf_exempt
def api_view(request):
    if request.method == "POST":
        if is_json_request(request.META.get('CONTENT_TYPE')):
            data = json.loads(request.body)
            return handle_request(data=data)
        return JsonResponse(data={'error': 'Non json data found'},
                            status=400)
    return HttpResponse(status=405)
