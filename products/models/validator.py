import re
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class UserValidatorMixin:
    """Миксин для валидации данных пользователей"""
    
    @staticmethod
    def validate_phone(value):
        """Валидация номера телефона в формате +375 (XX) XXX-XX-XX"""
        pattern = r'^\+375 ?\(\d{2}\) ?\d{3}-\d{2}-\d{2}$'
        if not re.match(pattern, value):
            raise ValidationError(
                'Номер телефона должен быть в формате: +375 (XX) XXX-XX-XX'
            )
    
    @staticmethod
    def validate_birth_date(value):
        if value:
            today = timezone.now().date()
            adult_date = value.replace(year=value.year + 18)
            if adult_date > today:
                raise ValidationError('Пользователь должен быть старше 18 лет')
    
    def clean(self):
        """Общая валидация для моделей, наследующих этот миксин"""
        super().clean()
        
        if hasattr(self, 'phone') and self.phone:
            self.validate_phone(self.phone)
        
        if hasattr(self, 'birth_date') and self.birth_date:
            self.validate_birth_date(self.birth_date)