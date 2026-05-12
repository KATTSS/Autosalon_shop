from django.views.generic import TemplateView
from core.models import Employee, PickupPoint


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'core/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all().order_by('full_name')
        context['pickup_points'] = PickupPoint.objects.all()
        return context