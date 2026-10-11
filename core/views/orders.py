from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from products.models import Sale


@login_required(login_url='core:login')
@require_POST
def complete_order(request, pk):
    """Выдачу заказа подтверждает сотрудник."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    sale = get_object_or_404(Sale, pk=pk)
    return _transition(sale, Sale.Status.COMPLETED)


@login_required(login_url='core:login')
@require_POST
def cancel_order(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if not request.user.is_staff and sale.customer.user_id != request.user.pk:
        return HttpResponseForbidden()
    return _transition(sale, Sale.Status.CANCELLED)


def _transition(sale, status):
    try:
        sale.transition_to(status)
    except ValueError as error:
        return HttpResponseBadRequest(str(error))
    return redirect('core:order_history')
