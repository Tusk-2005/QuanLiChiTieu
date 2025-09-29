from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, transaction_list, transaction_create, dashboard,budget_create,transaction_delete
from .views import export_transactions_csv, export_transactions_excel, export_transactions_pdf
from . import views


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('transactions/', transaction_list, name="transaction_list"),
    path('transactions/new/', transaction_create, name="transaction_create"),
    path('dashboard/', dashboard, name="dashboard"),
    path('budget/new/', budget_create, name="budget_create"),
    path('transactions/<int:pk>/delete/', transaction_delete, name='transaction_delete'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),  
    path("budget/<int:pk>/delete/", views.budget_delete, name="budget_delete"),
    path("budget/<int:pk>/edit/", views.budget_edit, name="budget_edit"),
    path("register/", views.register, name="register"),
]
urlpatterns += [
    path('export/csv/', export_transactions_csv, name="export_csv"),
    path('export/excel/', export_transactions_excel, name="export_excel"),
    path('export/pdf/', export_transactions_pdf, name="export_pdf"),
]