from django.urls import path
from . import views

app_name = 'boothapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Booth
    path('booth/', views.booth_list, name='booth_list'),
    path('booth/create/', views.booth_create, name='booth_create'),
    path('booth/<int:pk>/update/', views.booth_update, name='booth_update'),
    path('booth/<int:pk>/delete/', views.booth_delete, name='booth_delete'),

    # Karyawan
    path('karyawan/', views.employee_list, name='employee_list'),
    path('karyawan/create/', views.employee_create, name='employee_create'),
    path('karyawan/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('karyawan/<int:pk>/toggle/', views.employee_toggle_status, name='employee_toggle'),

    # Stok
    path('stok/', views.inventory_list, name='inventory_list'),
    path('stok/create/', views.inventory_create, name='inventory_create'),
    path('stok/<int:pk>/update/', views.inventory_update, name='inventory_update'),
    path('stok/<int:pk>/restock/', views.inventory_restock, name='inventory_restock'),
    path('stok/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),

    # Menu
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/create/', views.menu_create, name='menu_create'),
    path('menu/<int:pk>/update/', views.menu_update, name='menu_update'),
    path('menu/<int:pk>/toggle/', views.menu_toggle, name='menu_toggle'),
    path('menu/<int:pk>/delete/', views.menu_delete, name='menu_delete'),
    path('menu/booth/<int:booth_id>/', views.menu_by_booth, name='menu_by_booth'),

    # Biaya Operasional
    path('biaya/', views.expense_list, name='expense_list'),
    path('biaya/create/', views.expense_create, name='expense_create'),
    path('biaya/<int:pk>/update/', views.expense_update, name='expense_update'),
    path('biaya/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # Penjualan
    path('penjualan/', views.sale_list, name='sale_list'),
    path('penjualan/create/', views.sale_create, name='sale_create'),
    path('penjualan/<int:pk>/delete/', views.sale_delete, name='sale_delete'),

    # Laporan
    path('laporan/', views.report, name='report'),
    # Laporan Arus Kas
    path('laporan/arus-kas/', views.cashflow_report, name='cashflow_report'),
]