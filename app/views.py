from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def home(request):
    return HttpResponse("Welcome to CareQueue API")

@csrf_exempt
@require_http_methods(["POST"])
def parse_text(request):
    data = request.POST.get('text', '')
    print('data', data)
    return JsonResponse({'message': 'Audio Received', 'data': data})
