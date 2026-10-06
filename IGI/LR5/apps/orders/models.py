from django.db import models
from django.contrib.auth.models import User
from apps.cars.models import Car
from apps.promo.models import PromoCode
from django.core.exceptions import ValidationError

class Order(models.Model):
    STATUS_CHOICES = [('new', 'Новый'), ('confirmed', 'Подтвержден'), ('in_delivery', 'Доставляется'), ('completed', 'Завершен'), ('cancelled', 'Отменен')]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    sale_date = models.DateTimeField(null = True, blank=True)
    delivery_date = models.DateField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        if self.delivery_date and self.sale_date:
            delivery = self.delivery_date if hasattr(self.delivery_date, 'date') else self.delivery_date
            if hasattr(delivery, 'date'):
                delivery = delivery.date()
            
            sale = self.sale_date if hasattr(self.sale_date, 'date') else self.sale_date
            if hasattr(sale, 'date'):
                sale = sale.date()
            if isinstance(delivery, str):
                from datetime import datetime
                delivery = datetime.strptime(delivery, '%Y-%m-%d').date()
            if isinstance(sale, str):
                from datetime import datetime
                sale = datetime.strptime(sale, '%Y-%m-%d').date()
            if delivery < sale:
                raise ValidationError({'delivery_date': 'Дата доставки не может быть раньше даты продажи'})
            
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def get_total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f'{self.car.name} ({self.quantity})'