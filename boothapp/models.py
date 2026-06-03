from django.db import models
from django.contrib.auth.models import User


class Booth(models.Model):
    TIPE_CHOICES = [
        ('minuman', 'Minuman'),
        ('makanan', 'Makanan'),
        ('campuran', 'Campuran'),
    ]
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('inactive', 'Nonaktif'),
    ]
    ICON_CHOICES = [
        ('fa-mug-hot', 'Kopi/Minuman'),
        ('fa-drumstick-bite', 'Ayam/Makanan'),
        ('fa-blender', 'Smoothie'),
        ('fa-glass-water', 'Es Teh'),
        ('fa-ice-cream', 'Dessert'),
        ('fa-utensils', 'Restoran'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nama Booth')
    location = models.CharField(max_length=300, verbose_name='Lokasi')
    booth_type = models.CharField(max_length=20, choices=TIPE_CHOICES, verbose_name='Tipe')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-mug-hot')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Booth'
        verbose_name_plural = 'Booth'
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    SHIFT_CHOICES = [
        ('pagi', 'Pagi (06:00 - 14:00)'),
        ('siang', 'Siang (14:00 - 22:00)'),
        ('malam', 'Malam (22:00 - 06:00)'),
    ]
    STATUS_CHOICES = [
        ('active', 'Aktif'),
        ('inactive', 'Nonaktif'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nama Lengkap')
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='employees')
    position = models.CharField(max_length=100, verbose_name='Posisi')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    phone = models.CharField(max_length=20, verbose_name='No. Telepon')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Karyawan'
        verbose_name_plural = 'Karyawan'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.position}"


class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('bahan_minuman', 'Bahan Minuman'),
        ('bahan_makanan', 'Bahan Makanan'),
        ('kemasan', 'Kemasan'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nama Bahan')
    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='inventory')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name='Kategori')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok')
    unit = models.CharField(max_length=30, verbose_name='Satuan')
    min_stock = models.PositiveIntegerField(default=5, verbose_name='Stok Minimum')
    price_per_unit = models.PositiveIntegerField(default=0, verbose_name='Harga per Satuan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bahan Baku'
        verbose_name_plural = 'Bahan Baku'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.booth.name})"

    @property
    def is_low(self):
        return self.stock <= self.min_stock

    @property
    def is_critical(self):
        return self.stock <= self.min_stock * 0.5


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('minuman', 'Minuman'),
        ('makanan', 'Makanan'),
    ]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200, verbose_name='Nama Menu')
    price = models.PositiveIntegerField(verbose_name='Harga')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_available = models.BooleanField(default=True, verbose_name='Tersedia')

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menu'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} — {self.booth.name}"


class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('tunai', 'Tunai'),
        ('digital', 'Digital (QRIS/Transfer)'),
    ]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField(db_index=True)
    total = models.PositiveIntegerField(verbose_name='Total')
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name='Metode Pembayaran')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Penjualan'
        verbose_name_plural = 'Penjualan'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Penjualan #{self.id} — {self.booth.name} ({self.date})"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    menu_name = models.CharField(max_length=200)  # snapshot nama saat transaksi
    quantity = models.PositiveIntegerField(verbose_name='Jumlah')
    price = models.PositiveIntegerField(verbose_name='Harga Satuan')
    subtotal = models.PositiveIntegerField(verbose_name='Subtotal')

    def __str__(self):
        return f"{self.menu_name} x{self.quantity}"
    
class OperationalExpense(models.Model):
    CATEGORY_CHOICES = [
        ('karyawan', 'Biaya Karyawan'),
        ('sewa', 'Sewa Tempat'),
        ('investasi', 'Investasi Awal'),
        ('operasional', 'Operasional Harian'),
    ]

    booth = models.ForeignKey(Booth, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Kategori')
    description = models.CharField(max_length=200, verbose_name='Deskripsi')
    amount = models.PositiveIntegerField(verbose_name='Jumlah Biaya')
    date = models.DateField(verbose_name='Tanggal Pengeluaran')
    is_recurring = models.BooleanField(default=False, verbose_name='Biaya Berulang (Bulanan)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Biaya Operasional'
        verbose_name_plural = 'Biaya Operasional'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_category_display()} - {self.description} ({self.booth.name})"    