# boothapp/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from boothapp.models import Booth, Employee, MenuItem, InventoryItem, Sale, SaleItem
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        # Buat user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@boothhub.id', 'admin123')

        # Booth
        b1, _ = Booth.objects.get_or_create(name='Fresh Drink Booth 1', defaults={'location':'Mall Central Atrium','booth_type':'minuman','icon':'fa-mug-hot'})
        b2, _ = Booth.objects.get_or_create(name='Fresh Chicken Booth', defaults={'location':'Mall Central Lantai 2','booth_type':'makanan','icon':'fa-drumstick-bite'})
        b3, _ = Booth.objects.get_or_create(name='Smoothie & Coffee Corner', defaults={'location':'Food Court Lt. 3','booth_type':'campuran','icon':'fa-blender'})
        b4, _ = Booth.objects.get_or_create(name='Es Teh & Kopi Stand', defaults={'location':'Area Parkir Timur','booth_type':'minuman','icon':'fa-glass-water'})

        # ... lanjutkan seeder untuk Employee, MenuItem, InventoryItem, Sale
        # (pola sama dengan data awal di versi localStorage)

        self.stdout.write(self.style.SUCCESS('Data demo berhasil dimuat!'))