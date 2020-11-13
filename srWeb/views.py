import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .pub import handleImage
import os

def index(request):
    return render(request, 'index.html')


def response_json_error(data, status_code=400):
    response = HttpResponse(json.dumps(data), content_type='application/json', status=status_code)
    response['Access-Control-Allow-Origin'] = '*'
    return response


def image_process(image):
    file = open('./static/data/' + image.name, 'wb')
    file.write(image.read())
    file_ext = os.path.splitext(image.name)
    if handleImage("./static/data/" + image.name,file_ext[0]):
        return True
    else:
        return False


@csrf_exempt
def upload_images(request):
    if request.method == 'POST':
        image = request.FILES.get('fileList')
        try:
            if image_process(image):
                file_ext = os.path.splitext(image.name)
                url = '/static/redata/' + file_ext[0]+'_sr.bmp'
                return HttpResponse(url)
            else:
                return HttpResponse("")
        except Exception as e:
            return response_json_error(e)
    else:
        return redirect('/')
