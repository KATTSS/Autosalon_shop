from django.views.generic import ListView
from .models import Vacancy

class VacancyListView(ListView):
    model = Vacancy
    template_name = 'vacancies/list.html'
    context_object_name = 'vacancies'
    queryset = Vacancy.objects.filter(is_active=True)