from datetime import datetime, timezone
from django.shortcuts import render
from django.http import (HttpResponseRedirect, HttpResponseNotFound)
from django.contrib.auth.decorators import login_required
from .models import (Order, OrderItem)
from apps.accounts.utils import (employee_required)
from apps.cars.models import Car
from django.core.exceptions import ValidationError
from apps.promo.models import PromoCode
import logging


logger = logging.getLogger(__name__)

@login_required
def orders_list(request):
    if request.user.is_superuser:
        orders = Order.objects.all()

    elif (request.user.profile.role == 'employee'):
        orders = Order.objects.all()

    else:
        orders = Order.objects.filter(customer=request.user)

    return render(request, 'orders/index.html', {'orders': orders})

@login_required
@login_required
def create_order(request):
    cars = Car.objects.all()
    errors = {}
    form_data = {}

    if request.method == 'POST':
        car_ids = request.POST.getlist('cars')
        delivery_date = request.POST.get('delivery_date')
        promo_input = request.POST.get('promo_code')
        form_data = {'delivery_date': delivery_date, 'promo_code': promo_input, 'selected_cars': car_ids,}
        order = Order()
        order.customer = request.user
        order.delivery_date = delivery_date
        order.status = 'new'
        order.total_price = 0
        
        try:
            order.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
        if errors:
            return render(request, 'orders/create.html', {'cars': cars, 'errors': errors, 'form_data': form_data})
        order.save()
        total = 0

        for car_id in car_ids:
            car = Car.objects.get(id=car_id)
            item = OrderItem()
            item.order = order
            item.car = car
            quantity = int(request.POST.get(f'quantity_{car.id}', 1))
            item.quantity = quantity
            item.price = car.price * quantity
            total += item.price
            item.save()

        if promo_input:
            try:
                promo = PromoCode.objects.get(code=promo_input, is_active=True)
                discount = (total * promo.discount_percent / 100)
                total -= discount
                order.promo_code = promo
            except PromoCode.DoesNotExist:
                pass

        order.total_price = total
        order.save()
        logger.info(f'Order is created #{order.id} user {request.user.username}')
        return HttpResponseRedirect('/orders/')

    return render(request, 'orders/create.html', {'cars': cars, 'errors': {}, 'form_data': {}})

@login_required
def edit_order(request, id):
    try:
        order = Order.objects.get(id=id)
        is_employee = (request.user.profile.role == 'employee')
        is_admin = request.user.is_superuser
        is_customer = (order.customer == request.user)
        errors = {}

        if not (is_employee or is_admin or is_customer):
            return HttpResponseNotFound('<h2>Нет доступа</h2>')

        if (is_customer and order.status != 'new'):
            return HttpResponseNotFound('<h2>Заказ уже подтвержден</h2>')

        cars = Car.objects.all()
        
        if request.method == 'POST':
            old_delivery_date = order.delivery_date
            old_status = order.status
            order.delivery_date = request.POST.get('delivery_date')
            if is_employee or is_admin:
                order.status = request.POST.get('status')
            
            try:
                order.full_clean()
            except ValidationError as e:
                errors = e.message_dict
                order.delivery_date = old_delivery_date
                if is_employee or is_admin:
                    order.status = old_status
                
                return render(request, 'orders/edit.html', {
                    'order': order,
                    'cars': cars,
                    'is_employee': is_employee,
                    'is_admin': is_admin,
                    'errors': errors
                })
            order.items.all().delete()
            total = 0
            selected_cars = request.POST.getlist('cars')

            for car_id in selected_cars:
                car = Car.objects.get(id=car_id)
                quantity_value = request.POST.get(f'quantity_{car.id}', '1')

                if not quantity_value:
                    quantity_value = '1'

                quantity = int(quantity_value)
                item = OrderItem()
                item.order = order
                item.car = car
                item.quantity = quantity
                item.price = (car.price * quantity)
                item.save()
                total += item.price

            order.total_price = total
            order.save()

            logger.info(f'Order #{order.id} edit user {request.user.username}')
            return HttpResponseRedirect('/orders/')

        return render(request, 'orders/edit.html', {
            'order': order,
            'cars': cars,
            'is_employee': is_employee,
            'is_admin': is_admin,
            'errors': {}
        })

    except Order.DoesNotExist:
        return HttpResponseNotFound('<h2>Заказ не найден</h2>')

@login_required
@employee_required
def delete_order(request, id):

    try:
        order = Order.objects.get(id=id)
        logger.warning(f'Order #{order.id} deleted user {request.user.username}')
        order.delete()
        return HttpResponseRedirect('/orders/')

    except Order.DoesNotExist:
        return HttpResponseNotFound('<h2>Заказ не найден</h2>')
    
@login_required
@employee_required
def take_order(request, id):

    try:
        order = Order.objects.get(id=id)

        if order.employee is None:
            order.employee = request.user
            order.sale_date = datetime.now()
            order.status = 'confirmed'

            order.save()

            logger.info(f'Arbeiter {request.user.username} took order #{order.id}')

        return HttpResponseRedirect('/orders/')

    except Order.DoesNotExist:
        return HttpResponseNotFound('<h2>Заказ не найден</h2>')
    
@login_required
@employee_required
def change_status(request, id, status):

    try:
        order = Order.objects.get(id=id)

        if (order.employee == request.user or request.user.is_superuser):
            old_status = order.status
            order.status = status

            order.save()

            logger.info(f'Order status #{order.id} edit from "{old_status}" on "{status}" user {request.user.username}')

        return HttpResponseRedirect('/orders/')

    except Order.DoesNotExist:
        return HttpResponseNotFound('<h2>Заказ не найден</h2>')