from django.views.generic import ListView
from .models import PromoCode
from django.utils import timezone

class PromoListView(ListView):
    model = PromoCode
    template_name = 'promo/list.html'
    context_object_name = 'promo_codes'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['active_promo'] = self.get_queryset().filter(
            is_active=True, valid_from__lte=now, valid_to__gte=now
        )
        context['archived_promo'] = self.get_queryset().filter(
            is_active=False
        ) | self.get_queryset().filter(valid_to__lt=now)
        return context