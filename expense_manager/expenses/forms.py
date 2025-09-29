from django import forms
from .models import Transaction, Budget
from datetime import date
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["category", "amount", "type", "date", "note"]

class BudgetForm(forms.ModelForm):
    month = forms.DateField(
        input_formats=['%Y-%m'],
        widget=forms.DateInput(format='%Y-%m', attrs={'type': 'month'})
    )

    class Meta:
        model = Budget
        fields = ["category", "amount", "month"]

    def clean_month(self):
        m = self.cleaned_data['month']
        return m.replace(day=1)
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    