from django.views.generic import TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class CartView(TemplateView):
    """Просмотр корзины"""
    template_name = 'core/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})
        
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
                    'product_id': product_id,
                })
            except Product.DoesNotExist:
                continue
        
        context['cart_items'] = cart_items
        context['total'] = total
        context['cart_count'] = len(cart_items)
        
        return context


def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    if request.method != 'POST':
        return redirect('core:catalog')
    
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > product.stock:
        messages.error(
            request, 
            f'Недостаточно товара "{product.name}" на складе! Доступно: {product.stock} шт.'
        )
        logger.warning(f'Attempt to add {quantity} of {product.name} (only {product.stock} available)')
        return redirect('core:product_detail', pk=product_id)
    
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        new_quantity = cart[product_id_str]['quantity'] + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Нельзя добавить больше товара "{product.name}"')
            return redirect('core:product_detail', pk=product_id)
        cart[product_id_str]['quantity'] = new_quantity
    else:
        cart[product_id_str] = {'quantity': quantity}
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} добавлен в корзину ({quantity} шт.)')
    logger.debug(f'{product.name} added to cart by {request.user}')

    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'core:catalog'))
    return redirect(next_url)


def remove_from_cart(request, product_id):
    """Удаление товара из корзины"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        messages.success(request, 'Товар удалён из корзины')
    
    return redirect('core:cart')


def update_cart(request, product_id):
    """Обновление количества товара"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > product.stock:
            messages.error(request, f'Максимальное количество: {product.stock}')
            return redirect('core:cart')
        
        if quantity > 0:
            cart[str(product_id)]['quantity'] = quantity
        else:
            cart.pop(str(product_id), None)
        
        request.session['cart'] = cart
    
    return redirect('core:cart')