from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import VerificationCode
from .forms import LoginForm, VerificationForm
from django.contrib.auth.decorators import login_required
import random

def login_view(request):
  if request.method == 'POST':
      form = LoginForm(request.POST)
      if form.is_valid():
          user = authenticate(username=form.cleaned_data['username'],
                              password=form.cleaned_data['password'])
          if user:
              # Generate and send verification code
              code = random.randint(100000, 999999)
              VerificationCode.objects.create(user=user, code=code)
              # Here you should send the code to the user via email/SMS
              print(f"Verification code: {code}") # For demonstration purposes
              return redirect('verify')
  else:
      form = LoginForm()
  return render(request, 'auth_app/login.html', {'form': form})

def verify_view(request):
  if request.method == 'POST':
      form = VerificationForm(request.POST)
      if form.is_valid():
          code = form.cleaned_data['code']
          verification = VerificationCode.objects.filter(code=code, 
                                                        is_valid=True).first()
          if verification:
              verification.is_valid = False
              verification.save()
              login(request, verification.user)
              return redirect('home')
  else:
      form = VerificationForm()
  return render(request, 'auth_app/verify.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'auth_app/home.html')

#-----------------------for api---------------------------------------------
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Item, DynamicDataModel
from .serializers import DynamicDataSerializer
from django.http import JsonResponse
from django.views import View
from prometheus_client import Counter
from rest_framework import viewsets
from .serializers import ItemSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class DynamicDataAPIView(APIView):
    def get(self, request):
        data = {"some_field": "Dynamic data generated here"}
        return Response(data)


class TestDataAPIView(View):
    def get(self, request, *args, **kwargs):
        data = {
            "users": [
                {"id": 1, "name": "Александр", "email": "alex@mail.ru"},
                {"id": 2, "name": "Елена", "email": "elena@mail.ru"},
                {"id": 3, "name": "Ксения", "email": "ksenia@example.com"}
            ],
            "status": "success",
        }
        return JsonResponse(data)

# Создание метрики для подсчета запросов
dynamic_data_requests = Counter(
    'dynamic_data_requests_total',
    'Total number of requests to DynamicDataAPIView'
)

class DynamicDataAPIView(APIView):
    def get(self, request):
        # Увеличиваем счетчик метрики
        dynamic_data_requests.inc()

        # Возвращаем данные
        data = {"some_field": "Dynamic data generated here"}
        return Response(data)

class CreateDynamicDataAPIView(APIView):
    def post(self, request):
        some_field = request.data.get('some_field', '')
        if some_field:
            # Сохраняем данные в базе
            dynamic_data = DynamicDataModel.objects.create(some_field=some_field)
            dynamic_data.save()

            # Увеличиваем счетчик метрики
            dynamic_data_requests.inc()

            return JsonResponse({"status": "success", "message": "Data added"})
        return JsonResponse({"status": "error", "message": "No data provided"}, status=400)
