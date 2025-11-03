from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncHour, TruncMonth
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Order, OrderItem

@api_view(['GET'])
def revenue_by_day(request):
    data = (
        Order.objects.filter(status='COMPLETED')
        .annotate(day=TruncDay('order_time'))
        .values('day')
        .annotate(faturamento=ExpressionWrapper(Sum(F('total_cents')) / 100.0, output_field=FloatField()))
        .order_by('day')
    )
    return Response(data)

@api_view(['GET'])
def top_products(request):
    data = (
        OrderItem.objects
        .values('product__name', 'product__category')
        .annotate(unidades_vendidas=Sum('quantity'),
                  receita=Sum('total_price_cents') / 100.0)
        .order_by('-unidades_vendidas')[:20]
    )
    return Response(data)

@api_view(['GET'])
def peak_hours(request):
    data = (
        Order.objects.filter(status='COMPLETED')
        .annotate(hour=TruncHour('order_time'))
        .values('hour')
        .annotate(pedidos=Count('id'), receita=Sum('total_cents') / 100.0)
        .order_by('hour')
    )
    return Response(data)

@api_view(['GET'])
def revenue_by_month(request):
    data = (
        Order.objects.filter(status='COMPLETED')
        .annotate(month=TruncMonth('order_time'))
        .values('month')
        .annotate(pedidos=Count('id'), receita=Sum('total_cents') / 100.0)
        .order_by('month')
    )
    return Response(data)
