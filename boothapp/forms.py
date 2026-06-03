from django import forms
from .models import Booth, Employee, InventoryItem, MenuItem, Sale
from .models import Booth, Employee, InventoryItem, MenuItem, Sale, OperationalExpense

class BoothForm(forms.ModelForm):
    class Meta:
        model = Booth
        fields = ['name', 'location', 'booth_type', 'status', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nama Booth'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lokasi'}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'booth', 'position', 'shift', 'phone', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }


class InventoryForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'booth', 'category', 'stock', 'unit', 'min_stock', 'price_per_unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'kg, liter, pack'}),
        }


class RestockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label='Jumlah Restock',
        widget=forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}))


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['booth', 'name', 'price', 'category', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
        }

class OperationalExpenseForm(forms.ModelForm):
    class Meta:
        model = OperationalExpense
        fields = ['booth', 'category', 'description', 'amount', 'date', 'is_recurring']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contoh: Gaji Januari, Sewa Bulan Feb'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }

class SaleForm(forms.Form):
    booth = forms.ModelChoiceField(queryset=Booth.objects.filter(status='active'))
    payment = forms.ChoiceField(choices=Sale.PAYMENT_CHOICES)