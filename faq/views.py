from django.views.generic import ListView
from .models import FAQItem

class FAQListView(ListView):
    model = FAQItem
    template_name = 'faq/list.html'
    context_object_name = 'faq_items'
    queryset = FAQItem.objects.filter(is_published=True)