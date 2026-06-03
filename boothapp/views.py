from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Q          # ← Q ditambahkan di sini
from django.utils import timezone
from django.db.models.functions import TruncDate
from datetime import timedelta, date
import json



from .models import Booth, Employee, InventoryItem, MenuItem, Sale, SaleItem, OperationalExpense
from .forms import BoothForm, EmployeeForm, InventoryForm, RestockForm, MenuItemForm, SaleForm, OperationalExpenseForm

def format_rp(value):
    """Format angka menjadi Rupiah Indonesia: 1500000 -> Rp 1.500.000"""
    try:
        val = int(float(value)) if value else 0
    except (ValueError, TypeError):
        val = 0
    return f"Rp {val:,}".replace(",", ".")


# ==================== DASHBOARD ====================
@login_required
def dashboard(request):
    today = date.today()
    yesterday = today - timedelta(days=1)

    # KPI
    today_sales = Sale.objects.filter(date=today)
    today_revenue = today_sales.aggregate(total=Sum('total'))['total'] or 0
    yesterday_revenue = Sale.objects.filter(date=yesterday).aggregate(total=Sum('total'))['total'] or 0

    if yesterday_revenue > 0:
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue * 100)
    else:
        revenue_change = 0

    today_tx = today_sales.count()
    avg_per_tx = today_revenue / today_tx if today_tx > 0 else 0
    active_booths = Booth.objects.filter(status='active').count()
    total_booths = Booth.objects.count()
    low_stock_items = InventoryItem.objects.filter(stock__lte=F('min_stock'))
    low_stock_count = low_stock_items.count()
    active_employees = Employee.objects.filter(status='active').count()

    # Chart: Revenue 7 hari
    last7 = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        rev = Sale.objects.filter(date=d).aggregate(total=Sum('total'))['total'] or 0
        last7.append({'date': d.strftime('%Y-%m-%d'), 'revenue': int(rev)})

    # Chart: Penjualan per booth hari ini
    booth_revenues = Booth.objects.filter(status='active').annotate(
        today_rev=Sum('sales__total', filter=Q(sales__date=today)),
        today_tx=Count('sales', filter=Q(sales__date=today))
    )
    
    # Format Rupiah untuk setiap booth
    for b in booth_revenues:
        b.today_rev_fmt = format_rp(b.today_rev)

    context = {
        'today_revenue': today_revenue,
        'today_revenue_fmt': format_rp(today_revenue),     # Diformat di Python
        'revenue_change': revenue_change,
        'today_tx': today_tx,
        'avg_per_tx': avg_per_tx,
        'avg_per_tx_fmt': format_rp(avg_per_tx),           # Diformat di Python
        'active_booths': active_booths,
        'total_booths': total_booths,
        'low_stock_count': low_stock_count,
        'active_employees': active_employees,
        'low_stock_items': low_stock_items[:6],
        'last7': last7,
        'booth_revenues': booth_revenues,
        'booths': Booth.objects.filter(status='active'),
        'today': today,
    }
    return render(request, 'boothapp/dashboard.html', context)

# ==================== BOOTH ====================
@login_required
def booth_list(request):
    booths = Booth.objects.all()
    today = date.today()
    context = {'booths': booths, 'today': today}
    return render(request, 'boothapp/booth_list.html', context)


@login_required
def booth_create(request):
    if request.method == 'POST':
        form = BoothForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boothapp:booth_list')
    else:
        form = BoothForm()
    return render(request, 'boothapp/booth_form.html', {'form': form, 'title': 'Tambah Booth'})


@login_required
def booth_update(request, pk):
    booth = get_object_or_404(Booth, pk=pk)
    if request.method == 'POST':
        form = BoothForm(request.POST, instance=booth)
        if form.is_valid():
            form.save()
            return redirect('boothapp:booth_list')
    else:
        form = BoothForm(instance=booth)
    return render(request, 'boothapp/booth_form.html', {'form': form, 'title': 'Edit Booth'})


@login_required
def booth_delete(request, pk):
    booth = get_object_or_404(Booth, pk=pk)
    if request.method == 'POST':
        booth.delete()
    return redirect('boothapp:booth_list')


# ==================== KARYAWAN ====================
@login_required
def employee_list(request):
    booth_id = request.GET.get('booth', 'all')
    employees = Employee.objects.select_related('booth').all()
    if booth_id != 'all':
        employees = employees.filter(booth_id=int(booth_id))
    
    # Hitung untuk summary cards
    shift_pagi_count = employees.filter(shift='pagi', status='active').count()
    shift_siang_count = employees.filter(shift='siang', status='active').count()
    inactive_count = employees.filter(status='inactive').count()
    
    context = {
        'employees': employees,
        'booths': Booth.objects.all(),
        'selected_booth': booth_id,
        'shift_pagi_count': shift_pagi_count,
        'shift_siang_count': shift_siang_count,
        'inactive_count': inactive_count,
    }
    return render(request, 'boothapp/employee_list.html', context)


@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boothapp:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'boothapp/employee_form.html', {'form': form, 'title': 'Tambah Karyawan'})


@login_required
def employee_update(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return redirect('boothapp:employee_list')
    else:
        form = EmployeeForm(instance=emp)
    return render(request, 'boothapp/employee_form.html', {'form': form, 'title': 'Edit Karyawan'})


@login_required
def employee_toggle_status(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    emp.status = 'inactive' if emp.status == 'active' else 'active'
    emp.save()
    return redirect('boothapp:employee_list')


# ==================== STOK ====================
@login_required
def inventory_list(request):
    booth_id = request.GET.get('booth', 'all')
    category = request.GET.get('category', 'all')
    items = InventoryItem.objects.select_related('booth').all()
    if booth_id != 'all':
        items = items.filter(booth_id=int(booth_id))
    if category != 'all':
        items = items.filter(category=category)
    low_count = items.filter(stock__lte=F('min_stock')).count()
    context = {
        'items': items,
        'booths': Booth.objects.all(),
        'selected_booth': booth_id,
        'selected_category': category,
        'low_count': low_count,
    }
    return render(request, 'boothapp/inventory_list.html', context)


@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boothapp:inventory_list')
    else:
        form = InventoryForm()
    return render(request, 'boothapp/inventory_form.html', {'form': form, 'title': 'Tambah Bahan Baku'})


@login_required
def inventory_update(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('boothapp:inventory_list')
    else:
        form = InventoryForm(instance=item)
    return render(request, 'boothapp/inventory_form.html', {'form': form, 'title': 'Edit Bahan Baku'})


@login_required
def inventory_restock(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = RestockForm(request.POST)
        if form.is_valid():
            item.stock += form.cleaned_data['quantity']
            item.save()
            return redirect('boothapp:inventory_list')
    else:
        form = RestockForm()
    return render(request, 'boothapp/restock_form.html', {'form': form, 'item': item})


@login_required
def inventory_delete(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        item.delete()
    return redirect('boothapp:inventory_list')


# ==================== MENU ====================
@login_required
def menu_list(request):
    booth_id = request.GET.get('booth', 'all')
    category = request.GET.get('category', 'all')
    items = MenuItem.objects.select_related('booth').all()
    
    if booth_id != 'all':
        items = items.filter(booth_id=int(booth_id))
    if category != 'all':
        items = items.filter(category=category)
    
    # Hitung untuk summary cards
    drink_count = items.filter(category='minuman').count()
    food_count = items.filter(category='makanan').count()
    available_count = items.filter(is_available=True).count()
    
    # Format Rupiah untuk harga menu
    for item in items:
        item.price_fmt = format_rp(item.price)
    
    context = {
        'items': items,
        'booths': Booth.objects.all(),
        'selected_booth': booth_id,
        'selected_category': category,
        'drink_count': drink_count,
        'food_count': food_count,
        'available_count': available_count,
    }
    return render(request, 'boothapp/menu_list.html', context)


@login_required
def menu_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boothapp:menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'boothapp/menu_form.html', {'form': form, 'title': 'Tambah Menu'})

@login_required
def menu_update(request, pk):
    menu = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('boothapp:menu_list')
    else:
        form = MenuItemForm(instance=menu)
    return render(request, 'boothapp/menu_form.html', {'form': form, 'title': 'Edit Menu'})


@login_required
def menu_toggle(request, pk):
    menu = get_object_or_404(MenuItem, pk=pk)
    menu.is_available = not menu.is_available
    menu.save()
    return redirect('boothapp:menu_list')


@login_required
def menu_delete(request, pk):
    menu = get_object_or_404(MenuItem, pk=pk)
    if request.method == 'POST':
        menu.delete()
    return redirect('boothapp:menu_list')


# ==================== PENJUALAN ====================
@login_required
def sale_list(request):
    sale_date = request.GET.get('date', date.today().isoformat())
    booth_id = request.GET.get('booth', 'all')
    sales = Sale.objects.filter(date=sale_date).select_related('booth').prefetch_related('items')
    
    if booth_id != 'all':
        sales = sales.filter(booth_id=int(booth_id))
        
    total_revenue = sales.aggregate(total=Sum('total'))['total'] or 0
    total_tx = sales.count()
    avg_per_tx = int(total_revenue / total_tx) if total_tx > 0 else 0
    
    # Format Rupiah untuk setiap transaksi dan itemnya
    for sale in sales:
        sale.total_fmt = format_rp(sale.total)
        for item in sale.items.all():
            item.subtotal_fmt = format_rp(item.subtotal)
    
    context = {
        'sales': sales,
        'sale_date': sale_date,
        'booths': Booth.objects.all(),
        'selected_booth': booth_id,
        'total_revenue': total_revenue,
        'total_revenue_fmt': format_rp(total_revenue),     # Ditambahkan
        'avg_per_tx': avg_per_tx,
        'avg_per_tx_fmt': format_rp(avg_per_tx),           # Ditambahkan
    }
    return render(request, 'boothapp/sale_list.html', context)


@login_required
def sale_create(request):
    if request.method == 'POST':
        booth_id = request.POST.get('booth')
        payment = request.POST.get('payment')
        booth = get_object_or_404(Booth, pk=booth_id)

        sale = Sale.objects.create(
            booth=booth,
            date=date.today(),
            total=0,
            payment=payment,
            created_by=request.user,
        )

        total = 0
        menu_items = MenuItem.objects.filter(booth=booth, is_available=True)
        for mi in menu_items:
            qty_key = f'qty_{mi.id}'
            qty = int(request.POST.get(qty_key, 0))
            if qty > 0:
                subtotal = qty * mi.price
                SaleItem.objects.create(
                    sale=sale,
                    menu_item=mi,
                    menu_name=mi.name,
                    quantity=qty,
                    price=mi.price,
                    subtotal=subtotal,
                )
                total += subtotal

        sale.total = total
        sale.save()

        if total == 0:
            sale.delete()

        return redirect('boothapp:sale_list')

    context = {
        'booths': Booth.objects.filter(status='active'),
        'form': SaleForm(),
    }
    return render(request, 'boothapp/sale_form.html', context)


@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
    return redirect('boothapp:sale_list')


# ==================== MENU BY BOOTH (AJAX) ====================
@login_required
def menu_by_booth(request, booth_id):
    items = MenuItem.objects.filter(booth_id=booth_id, is_available=True)
    data = [{'id': m.id, 'name': m.name, 'price': m.price} for m in items]
    return JsonResponse(data, safe=False)


# ==================== LAPORAN ====================

@login_required 
def report(request):
    today = date.today()
    start_30_date = today - timedelta(days=29)

    # ==================== PENDAPATAN ====================
    last30 = []
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        rev = Sale.objects.filter(date=d).aggregate(total=Sum('total'))['total'] or 0
        tx = Sale.objects.filter(date=d).count()
        last30.append({
            'date': d.strftime('%Y-%m-%d'),
            'day_name': d.strftime('%a'),
            'revenue': int(rev),
            'transactions': tx,
        })

    total_30_revenue = sum(d['revenue'] for d in last30)
    total_30_tx = sum(d['transactions'] for d in last30)
    avg_daily = total_30_revenue // 30 if total_30_revenue else 0
    avg_per_tx = int(total_30_revenue / total_30_tx) if total_30_tx > 0 else 0

    # ==================== BIAYA OPERASIONAL ====================
    expenses_30 = OperationalExpense.objects.filter(date__gte=start_30_date, date__lte=today)
    total_30_expense = expenses_30.aggregate(total=Sum('amount'))['total'] or 0
    
    # Komposisi biaya
    karyawan_exp = expenses_30.filter(category='karyawan').aggregate(total=Sum('amount'))['total'] or 0
    sewa_exp = expenses_30.filter(category='sewa').aggregate(total=Sum('amount'))['total'] or 0
    investasi_exp = expenses_30.filter(category='investasi').aggregate(total=Sum('amount'))['total'] or 0
    operasional_exp = expenses_30.filter(category='operasional').aggregate(total=Sum('amount'))['total'] or 0

    # ==================== LABA BERSIH ====================
    net_profit = total_30_revenue - total_30_expense

    # ==================== PER BOOTH ====================
    booth_revenues = Booth.objects.annotate(
        revenue=Sum('sales__total'),
        tx=Count('sales'),
    ).order_by('-revenue')
    
    # Hitung avg, expense, profit dan format Rupiah untuk setiap booth
    for b in booth_revenues:
        b.avg_tx = int((b.revenue or 0) / b.tx) if b.tx and b.tx > 0 else 0
        b.revenue_fmt = format_rp(b.revenue)
        b.avg_tx_fmt = format_rp(b.avg_tx)
        
        # Biaya per booth
        b_expense = expenses_30.filter(booth=b).aggregate(total=Sum('amount'))['total'] or 0
        b.expense = b_expense
        b.expense_fmt = format_rp(b.expense)
        
        # Laba per booth
        b.profit = (b.revenue or 0) - b.expense
        b.profit_fmt = format_rp(b.profit)

    # ==================== TOP MENU ====================
    top_menu = list(SaleItem.objects.values('menu_name').annotate(
        total_qty=Sum('quantity'),
        total_rev=Sum('subtotal'),
    ).order_by('-total_rev')[:8])

    for item in top_menu:
        item['total_rev_fmt'] = format_rp(item.get('total_rev', 0))

    # ==================== PAYMENT ====================
    tunai = Sale.objects.filter(payment='tunai').aggregate(count=Count('id'), total=Sum('total'))
    digital = Sale.objects.filter(payment='digital').aggregate(count=Count('id'), total=Sum('total'))

    context = {
        'last30': last30,
        'total_30_revenue': total_30_revenue,
        'total_30_revenue_fmt': format_rp(total_30_revenue),
        'total_30_tx': total_30_tx,
        'avg_daily': avg_daily,
        'avg_daily_fmt': format_rp(avg_daily),
        'avg_per_tx': avg_per_tx,
        'avg_per_tx_fmt': format_rp(avg_per_tx),
        'booth_revenues': booth_revenues,
        'top_menu': top_menu,
        'tunai': tunai,
        'digital': digital,
        'tunai_total_fmt': format_rp(tunai.get('total')),
        'digital_total_fmt': format_rp(digital.get('total')),
        # Data Biaya Baru
        'total_30_expense_fmt': format_rp(total_30_expense),
        'net_profit_fmt': format_rp(net_profit),
        'karyawan_exp': int(karyawan_exp),
        'sewa_exp': int(sewa_exp),
        'investasi_exp': int(investasi_exp),
        'operasional_exp': int(operasional_exp),
    }
    return render(request, 'boothapp/report.html', context)


# ==================== BIAYA OPERASIONAL ====================
@login_required
def expense_list(request):
    booth_id = request.GET.get('booth', 'all')
    category = request.GET.get('category', 'all')
    expenses = OperationalExpense.objects.select_related('booth').all()
    
    if booth_id != 'all':
        expenses = expenses.filter(booth_id=int(booth_id))
    if category != 'all':
        expenses = expenses.filter(category=category)
    
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    karyawan_expense = expenses.filter(category='karyawan').aggregate(total=Sum('amount'))['total'] or 0
    sewa_expense = expenses.filter(category='sewa').aggregate(total=Sum('amount'))['total'] or 0
    investasi_expense = expenses.filter(category='investasi').aggregate(total=Sum('amount'))['total'] or 0
    operasional_expense = expenses.filter(category='operasional').aggregate(total=Sum('amount'))['total'] or 0
    
    # Format Rupiah
    for e in expenses:
        e.amount_fmt = format_rp(e.amount)
    
    context = {
        'expenses': expenses,
        'booths': Booth.objects.all(),
        'selected_booth': booth_id,
        'selected_category': category,
        'total_expense_fmt': format_rp(total_expense),
        'karyawan_expense_fmt': format_rp(karyawan_expense),
        'sewa_expense_fmt': format_rp(sewa_expense),
        'investasi_expense_fmt': format_rp(investasi_expense),
        'operasional_expense_fmt': format_rp(operasional_expense),
    }
    return render(request, 'boothapp/expense_list.html', context)


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = OperationalExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('boothapp:expense_list')
    else:
        form = OperationalExpenseForm()
    return render(request, 'boothapp/expense_form.html', {'form': form, 'title': 'Tambah Biaya Operasional'})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(OperationalExpense, pk=pk)
    if request.method == 'POST':
        form = OperationalExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('boothapp:expense_list')
    else:
        form = OperationalExpenseForm(instance=expense)
    return render(request, 'boothapp/expense_form.html', {'form': form, 'title': 'Edit Biaya Operasional'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(OperationalExpense, pk=pk)
    if request.method == 'POST':
        expense.delete()
    return redirect('boothapp:expense_list')


@login_required
@login_required
def cashflow_report(request):
    today = date.today()
    
    # Default: bulan ini (tanggal 1 sampai hari ini)
    start_date = today.replace(day=1)
    end_date = today
    
    # Ambil dari GET request jika ada
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    if start_date_str:
        try:
            parts = start_date_str.split('-')
            start_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            pass
            
    if end_date_str:
        try:
            parts = end_date_str.split('-')
            end_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            pass

    # Pemasukan per hari (Grup langsung oleh field 'date' karena tipenya sudah DateField)
    inflows = Sale.objects.filter(date__range=(start_date, end_date))\
        .values('date').annotate(total=Sum('total')).order_by('date')
    
    # Pengeluaran per hari
    outflows = OperationalExpense.objects.filter(date__range=(start_date, end_date))\
        .values('date').annotate(total=Sum('amount')).order_by('date')

    # Gabungkan ke dalam dictionary berdasarkan tanggal
    cashflow_dict = {}
    current_date = start_date
    while current_date <= end_date:
        cashflow_dict[current_date] = {'inflow': 0, 'outflow': 0}
        current_date += timedelta(days=1)

    for inf in inflows:
        if inf['date'] in cashflow_dict:
            cashflow_dict[inf['date']]['inflow'] = inf['total'] or 0

    for out in outflows:
        if out['date'] in cashflow_dict:
            cashflow_dict[out['date']]['outflow'] = out['total'] or 0

    # Hitung Arus Kas Bersih & Kumulatif
    daily_data = []
    cumulative_balance = 0
    total_inflow = 0
    total_outflow = 0

    for d, vals in cashflow_dict.items():
        net = vals['inflow'] - vals['outflow']
        cumulative_balance += net
        total_inflow += vals['inflow']
        total_outflow += vals['outflow']
        
        daily_data.append({
            'date': d,
            'inflow': vals['inflow'],
            'outflow': vals['outflow'],
            'net': net,
            'cumulative': cumulative_balance,
            'inflow_fmt': format_rp(vals['inflow']),
            'outflow_fmt': format_rp(vals['outflow']),
            'net_fmt': format_rp(net),
            'cumulative_fmt': format_rp(cumulative_balance),
        })

    total_net = total_inflow - total_outflow

    context = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'daily_data': daily_data,
        'total_inflow_fmt': format_rp(total_inflow),
        'total_outflow_fmt': format_rp(total_outflow),
        'total_net_fmt': format_rp(total_net),
        'cumulative_balance_fmt': format_rp(cumulative_balance),
    }
    return render(request, 'boothapp/cashflow.html', context)