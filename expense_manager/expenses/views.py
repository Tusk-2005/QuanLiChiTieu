from django.shortcuts import render, redirect,get_object_or_404
from rest_framework import viewsets
from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from .forms import TransactionForm
from django.db.models import Sum
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import Budget
from .forms import BudgetForm
from django.contrib import messages
import csv
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import TransactionForm, BudgetForm
from .forms import UserRegisterForm

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Phân quyền
            if user.is_superuser or user.is_staff:
                return redirect("/admin/")   # admin → trang quản trị
            else:
                return redirect("dashboard")  # user thường → dashboard
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu!")

    return render(request, "expenses/login.html")
@login_required
def budget_create(request):
    budgets = Budget.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)

    # Tính tổng chi tiêu theo category
    spent_dict = {}
    for t in transactions:
     if t.category:  # chỉ cộng khi có category
        spent_dict[t.category.id] = spent_dict.get(t.category.id, 0) + t.amount

    # Gắn thêm thuộc tính cho mỗi budget
    for b in budgets:
        spent = spent_dict.get(b.category.id, 0)
        b.spent = spent
        b.remaining = b.amount - spent

    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect("budget_create")
    else:
        form = BudgetForm()

    return render(request, "expenses/budget_form.html", {
        "form": form,
        "budgets": budgets
    })
def export_transactions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ngày', 'Loại', 'Số tiền', 'Danh mục', 'Ghi chú'])

    transactions = Transaction.objects.all()
    for t in transactions:
        writer.writerow([t.date, t.get_type_display(), t.amount, t.category, t.note])

    return response
def export_transactions_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=transactions.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.append(['Ngày', 'Loại', 'Số tiền', 'Danh mục', 'Ghi chú'])

    transactions = Transaction.objects.all()
    for t in transactions:
        ws.append([t.date, t.get_type_display(), t.amount, str(t.category), t.note])

    wb.save(response)
    return response
def export_transactions_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Báo cáo Giao dịch")

    y = 760
    transactions = Transaction.objects.all()
    for t in transactions:
        line = f"{t.date} | {t.get_type_display()} | {t.amount} | {t.category} | {t.note}"
        p.drawString(100, y, line)
        y -= 20

    p.showPage()
    p.save()
    return response
@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Gom nhóm dữ liệu theo category
    data = {}
    for t in transactions:
        category_name = t.category.name if t.category else "Không có danh mục"
        # Ép Decimal -> float
        data[category_name] = data.get(category_name, 0) + float(t.amount)

    labels = list(data.keys())
    values = list(data.values())

    context = {
        "labels": json.dumps(labels, ensure_ascii=False),  # hiển thị Unicode tiếng Việt
        "data": json.dumps(values),
    }
    return render(request, "expenses/dashboard.html", context)
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, "expenses/transaction_list.html", {"transactions": transactions})
@login_required
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user   # gán user hiện tại
            transaction.save()
            return redirect("transaction_list")
    else:
        form = TransactionForm()
    return render(request, "expenses/transaction_form.html", {"form": form})
@login_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)  # chỉ lấy của chính user
    if request.method == "POST":
        tx.delete()
        messages.success(request, "Đã xoá giao dịch.")
        return redirect("transaction_list")
    # GET -> hiện trang xác nhận
    return render(request, "expenses/transaction_confirm_delete.html", {"object": tx})
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)  # chỉ cho chủ sở hữu sửa
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.user = request.user
            updated.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'expenses/transaction_form.html', {'form': form, 'edit_mode': True})
@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == "POST":
        budget.delete()
        return redirect("budget_create")
    return redirect("budget_create")
@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect("budget_create")
    else:
        form = BudgetForm(instance=budget)

    return render(request, "expenses/budget_form.html", {
        "form": form,
        "budgets": Budget.objects.filter(user=request.user)
    })
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False   # user thường, không có quyền admin
            user.save()
            messages.success(request, 'Tài khoản đã được tạo thành công! Bạn có thể đăng nhập.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'expenses/register.html', {'form': form})
