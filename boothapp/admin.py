from django.contrib import admin
from .models import Booth, Employee, InventoryItem, MenuItem, Sale, SaleItem, OperationalExpense

@admin.register(OperationalExpense)
class OperationalExpenseAdmin(admin.ModelAdmin):
    list_display = ['booth', 'category', 'description', 'amount', 'date', 'is_recurring']
    list_filter = ['category', 'booth', 'is_recurring']
    search_fields = ['description']

@admin.register(Booth)
class BoothAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'booth_type', 'status']
    list_filter = ['status', 'booth_type']
    search_fields = ['name', 'location']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'booth', 'position', 'shift', 'status']
    list_filter = ['status', 'shift', 'booth']
    search_fields = ['name']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'booth', 'category', 'stock', 'unit', 'min_stock']
    list_filter = ['category', 'booth']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'booth', 'price', 'category', 'is_available']
    list_filter = ['category', 'is_available', 'booth']

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['menu_name', 'quantity', 'price', 'subtotal']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'booth', 'date', 'total', 'payment']
    list_filter = ['payment', 'date', 'booth']
    inlines = [SaleItemInline]