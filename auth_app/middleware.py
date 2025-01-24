from django.utils.deprecation import MiddlewareMixin
from .models import AccessLog
import json

class SecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        endpoint = request.path
        parameters = json.dumps(request.GET)

        # Проверка на несанкционированные параметры
        if 'unauthorized_param' in request.GET:
            AccessLog.objects.create(ip_address=ip_address, endpoint=endpoint, parameters=parameters, status='blocked')
            return HttpResponse('Unauthorized', status=401)
            
        # Log the request
        AccessLog.objects.create(ip_address=ip_address, endpoint=endpoint, parameters=parameters, status='allowed')

    def process_response(self, request, response):
        return response
