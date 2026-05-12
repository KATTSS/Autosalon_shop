from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from products.models import Product, Sale, SaleItem
from core.models import Customer, PickupPoint
from promo.models import PromoCode
from decimal import Decimal
from django.utils import timezone
from django.db import transaction


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Оформление заказа"""
    template_name = 'core/checkout.html'
    login_url = 'core:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        
        if not cart:
            return context
        
        cart_items = []
        total = Decimal('0')
        
        for product_id, item_data in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                quantity = item_data.get('quantity', 1)
                item_total = product.price * quantity
                total += item_total
                
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'item_total': item_total,
                })
            except Product.DoesNotExist:
                continue
        
        context.update({
            'cart_items': cart_items,
            'total': total,
            'pickup_points': PickupPoint.objects.all(),
            'active_promo_codes': PromoCode.objects.filter(
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            ),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        """Создание заказа"""
        cart = request.session.get('cart', {})
        
        if not cart:
            messages.error(request, 'Корзина пуста!')
            return redirect('core:cart')
        
        try:
            with transaction.atomic():
                # Получаем или создаём покупателя
                customer, _ = Customer.objects.get_or_create(
                    user=request.user,
                    defaults={'phone': ''}
                )
                
                # Проверяем промокод
                promo_code = None
                promo_code_id = request.POST.get('promo_code')
                if promo_code_id:
                    promo_code = PromoCode.objects.get(id=promo_code_id)
                    if not promo_code.is_valid():
                        messages.warning(request, 'Промокод недействителен!')
                        promo_code = None
                
                # Создаём продажу
                sale = Sale.objects.create(
                    customer=customer,
                    pickup_point_id=request.POST.get('pickup_point'),
                    promo_code=promo_code,
                    sale_date=timezone.now(),
                )
                
                # Добавляем товары
                for product_id, item_data in cart.items():
                    product = Product.objects.get(id=int(product_id))
                    quantity = item_data.get('quantity', 1)
                    
                    # Проверяем наличие (повторно, на всякий случай)
                    if quantity > product.calculate_stock():
                        raise ValueError(
                            f'Недостаточно товара "{product.name}" на складе!'
                        )
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                    )
                
                # Очищаем корзину
                request.session['cart'] = {}
                messages.success(
                    request, 
                    f'✅ Заказ №{sale.id} успешно оформлен! '
                    f'Сумма: {sale.total_amount} руб.'
                )
                
                return redirect('core:order_detail', pk=sale.id)
                
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
        
        return redirect('core:checkout')