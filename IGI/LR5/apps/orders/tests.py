from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order
from apps.cars.models import (
    Car,
    CarCategory,
    Manufacturer
)


class OrderTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='Gena',password='12345678Gn')
        self.employee = User.objects.create_user(username='worker',password='12345678Gn')
        self.category = CarCategory.objects.create(name='Lux')
        self.manufacturer = Manufacturer.objects.create(name='BMW',country='Germany')
        self.car = Car.objects.create(
            name='BMW M5',
            price=4000,
            category=self.category,
            manufacturer=self.manufacturer,
            year=2020,
            mileage=10000,
            transmission='automatic',
            fuel_type='petrol',
            description='Test car',
            image='cars/test.jpg'
        )
        self.order = Order.objects.create(customer=self.customer, total_price=4000, delivery_date=timezone.now() + timedelta(days=7))

    def test_order_created(self):
        self.assertEqual(self.order.customer.username, 'Gena')

    def test_total_price(self):
        self.assertEqual(self.order.total_price, 4000)

    def test_edit_order(self):
        self.order.total_price = 8000
        self.order.save()
        self.assertEqual(self.order.total_price, 8000)

    def test_delete_order(self):
        order_id = self.order.id
        self.order.delete()
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_take_order(self):
        self.order.employee = self.employee
        self.order.save()
        self.assertEqual(self.order.employee.username, 'worker')
