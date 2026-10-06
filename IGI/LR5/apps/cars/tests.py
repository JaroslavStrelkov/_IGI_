from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from apps.accounts.models import Profile
from apps.cars.models import Car, CarCategory, Manufacturer


class CarTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='employee', password='12345678Qq')
        self.user.profile.role = 'employee'
        self.user.profile.save()
        self.client.login(username='employee', password='12345678Qq')
        self.category = CarCategory.objects.create(name='Sport')
        self.manufacturer = Manufacturer.objects.create(name='BMW', country='Germany')
        self.car = Car.objects.create(
            name='BMW M4',
            description='Fast car',
            price=300000,
            year=2024,
            mileage=1000,
            transmission='automatic',
            fuel_type='petrol',
            category=self.category,
            manufacturer=self.manufacturer,
        )
    def test_car_created(self):
        self.assertEqual(self.car.name, 'BMW M4')

    def test_car_price(self):
        self.assertEqual(self.car.price, 300000)

    def test_edit_car(self):
        response = self.client.post(f'/cars/edit/{self.car.id}/',
            {
                'name': 'BMW M5',
                'description': 'Updated',
                'price': 350000,
                'year': 2025,
                'mileage': 500,
                'transmission': 'automatic',
                'fuel_type': 'petrol',
                'category': self.category.id,
                'manufacturer': self.manufacturer.id,
            }
        )

        self.car.refresh_from_db()
        self.assertEqual(self.car.name, 'BMW M5')

    def test_delete_car(self):
        response = self.client.get(f'/cars/delete/{self.car.id}/')
        self.assertEqual(Car.objects.count(),0)

    def test_create_car(self):
        response = self.client.post('/cars/create/',
            {
                'name': 'Audi RS6',
                'description': 'Audi car',
                'price': 200000,
                'year': 2023,
                'mileage': 3000,
                'transmission': 'automatic',
                'fuel_type': 'petrol',
                'category': self.category.id,
                'manufacturer': self.manufacturer.id,
            }
        )

        self.assertEqual(Car.objects.count(), 2)
