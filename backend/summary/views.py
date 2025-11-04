from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDay, TruncHour, TruncMonth
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from .models import Order, OrderItem
from datetime import datetime
import csv

from .models import Store, Channel


def parse_date_range(request):
    """Parses start/end query params (ISO dates or datetimes). Returns (start, end) timezone-aware or None."""
    start = request.GET.get('start')
    end = request.GET.get('end')
    def _parse(s):
        if not s:
            return None
        try:
            # try full datetime first
            dt = datetime.fromisoformat(s)
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            return dt
        except Exception:
            try:
                d = datetime.fromisoformat(s + 'T00:00:00')
                if timezone.is_naive(d):
                    d = timezone.make_aware(d)
                return d
            except Exception:
                return None
    return _parse(start), _parse(end)


@api_view(['GET'])
def revenue_by_day(request):
    start, end = parse_date_range(request)
    qs = Order.objects.filter(status='COMPLETED')
    if start:
        qs = qs.filter(order_time__gte=start)
    if end:
        qs = qs.filter(order_time__lte=end)
    data = (
        qs
        .annotate(day=TruncDay('order_time'))
        .values('day')
        .annotate(faturamento=ExpressionWrapper(Sum(F('total_cents')) / 100.0, output_field=FloatField()), pedidos=Count('id'))
        .order_by('day')
    )
    return Response(list(data))


@api_view(['GET'])
def top_products(request):
    """Top products with optional filters: store, channel, start, end, limit"""
    start, end = parse_date_range(request)
    store = request.GET.get('store')
    channel = request.GET.get('channel')
    limit = int(request.GET.get('limit') or 10)

    items = OrderItem.objects.select_related('order', 'product')
    if start:
        items = items.filter(order__order_time__gte=start)
    if end:
        items = items.filter(order__order_time__lte=end)
    if store:
        items = items.filter(order__store_id=store)
    if channel:
        items = items.filter(order__channel__code=channel)

    data = (
        items
        .values('product__id', 'product__name', 'product__category')
        .annotate(unidades_vendidas=Sum('quantity'), receita=ExpressionWrapper(Sum(F('total_price_cents')) / 100.0, output_field=FloatField()))
        .order_by('-unidades_vendidas')[:limit]
    )
    return Response(list(data))


@api_view(['GET'])
def peak_hours(request):
    start, end = parse_date_range(request)
    qs = Order.objects.filter(status='COMPLETED')
    if start:
        qs = qs.filter(order_time__gte=start)
    if end:
        qs = qs.filter(order_time__lte=end)
    data = (
        qs
        .annotate(hour=TruncHour('order_time'))
        .values('hour')
        .annotate(pedidos=Count('id'), receita=ExpressionWrapper(Sum(F('total_cents')) / 100.0, output_field=FloatField()))
        .order_by('hour')
    )
    return Response(list(data))


@api_view(['GET'])
@cache_page(60)  # cache simples: 60s
def revenue_by_month(request):
    """Retorna receita por mês e métricas adicionais (pedidos). Aceita filtros de data (start/end) e store/channel."""
    start, end = parse_date_range(request)
    store = request.GET.get('store')
    channel = request.GET.get('channel')
    qs = Order.objects.filter(status='COMPLETED')
    if start:
        qs = qs.filter(order_time__gte=start)
    if end:
        qs = qs.filter(order_time__lte=end)
    if store:
        qs = qs.filter(store_id=store)
    if channel:
        qs = qs.filter(channel__code=channel)

    data = (
        qs
        .annotate(month=TruncMonth('order_time'))
        .values('month')
        .annotate(pedidos=Count('id'), receita=ExpressionWrapper(Sum(F('total_cents')) / 100.0, output_field=FloatField()))
        .order_by('month')
    )
    return Response(list(data))


@api_view(['GET'])
def compare_stores(request):
    """Compara duas lojas por receita/pedidos/avg_ticket em um período.

    Params: store_a, store_b, metric(revenue|orders|avg_ticket), start, end
    """
    store_a = request.GET.get('store_a')
    store_b = request.GET.get('store_b')
    metric = request.GET.get('metric', 'revenue')
    start, end = parse_date_range(request)

    def agg_for_store(store_id):
        qs = Order.objects.filter(status='COMPLETED', store_id=store_id)
        if start:
            qs = qs.filter(order_time__gte=start)
        if end:
            qs = qs.filter(order_time__lte=end)
        total_revenue = qs.aggregate(revenue=ExpressionWrapper(Sum(F('total_cents')) / 100.0, output_field=FloatField()))['revenue'] or 0
        orders = qs.count()
        avg_ticket = (total_revenue / orders) if orders else 0
        return {'revenue': total_revenue, 'orders': orders, 'avg_ticket': avg_ticket}

    if not store_a or not store_b:
        return Response({'detail': 'store_a and store_b are required'}, status=400)

    a = agg_for_store(store_a)
    b = agg_for_store(store_b)
    return Response({'store_a': a, 'store_b': b, 'metric': metric})


@api_view(['GET'])
def export_csv(request):
    """Exporta CSV para um dos relatórios suportados (type=top-products|revenue-by-day|peak-hours|revenue-by-month)
    Recebe mesmos filtros que os endpoints correspondentes.
    """
    report_type = request.GET.get('type')
    if report_type == 'top-products':
        data = top_products(request).data
        filename = 'top_products.csv'
        headers = ['product_id', 'product_name', 'category', 'qty', 'revenue']
    elif report_type == 'revenue-by-day':
        data = revenue_by_day(request).data
        filename = 'revenue_by_day.csv'
        headers = ['day', 'faturamento', 'pedidos']
    elif report_type == 'peak-hours':
        data = peak_hours(request).data
        filename = 'peak_hours.csv'
        headers = ['hour', 'pedidos', 'receita']
    elif report_type == 'revenue-by-month':
        data = revenue_by_month(request).data
        filename = 'revenue_by_month.csv'
        headers = ['month', 'pedidos', 'receita']
    else:
        return Response({'detail': 'type param inválido'}, status=400)

    # construir response CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in data:
        # normalize row keys
        writer.writerow([row.get(k) for k in [h if h in row else h.replace('-', '_') for h in headers]])
    return response


@api_view(['GET'])
def list_stores(request):
    data = list(Store.objects.values('id', 'name').order_by('name'))
    return Response(data)


@api_view(['GET'])
def list_channels(request):
    data = list(Channel.objects.values('code', 'name').order_by('name'))
    return Response(data)
