# from django.urls import path
# from .views import FuelRouteAPIView, HealthCheckView

# urlpatterns = [
#     path('calculate-route/', FuelRouteAPIView.as_view(), name='calculate_route'),
#     path('health/', HealthCheckView.as_view(), name='health_check'),
# ]


# routing/urls.py
from django.urls import path
from .views import calculate_route
from django.http import JsonResponse

def health(request):
    return JsonResponse({"status":"OK"})

urlpatterns = [
    path("calculate-route/", calculate_route, name="calculate_route"),
    path("health/", health, name="health"),
]
