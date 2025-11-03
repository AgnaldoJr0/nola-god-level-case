from django.urls import path
from . import views

urlpatterns = [
    path('metrics/revenue-by-day/', views.revenue_by_day),
    path('metrics/top-products/', views.top_products),
    path('metrics/peak-hours/', views.peak_hours),
    path('metrics/revenue-by-month/', views.revenue_by_month),
]
