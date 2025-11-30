from django.urls import path
from .views import FuelRouteAPIView, HealthCheckView

urlpatterns = [
    path('calculate-route/', FuelRouteAPIView.as_view(), name='calculate_route'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
