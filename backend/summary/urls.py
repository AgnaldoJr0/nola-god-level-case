from django.urls import path
from . import views

urlpatterns = [
    path('metrics/revenue-by-day/', views.revenue_by_day),
    path('metrics/top-products/', views.top_products),
    path('metrics/peak-hours/', views.peak_hours),
    path('metrics/revenue-by-month/', views.revenue_by_month),
    path('metrics/compare-stores/', views.compare_stores),
    path('metrics/export-csv/', views.export_csv),
    path('stores/', views.list_stores),
    path('channels/', views.list_channels),
]
