# tasks.py
from celery import shared_task
from datetime import datetime, timedelta
from .models import Shedule,Order
from django.utils import timezone

@shared_task
def deactivate_old_schedules():
    yesterday = datetime.now() - timedelta(days=1)
    old_schedules = Shedule.objects.filter(date__lt=yesterday)
    old_schedules.update(is_active=False)

@shared_task
def deactivate_completed_orders():
    current_date = timezone.now()
    active_orders = Order.objects.filter(is_active=True)
    for order in active_orders:
        deactivation_date = order.order_date + timedelta(days=order.months * 30) 
        if current_date > deactivation_date:
            order.is_active = False
            order.save()