from .admin_site import admin_site   # custom admin site
from .models import Transaction, Category, Budget
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Đăng ký các model vào custom admin site
admin_site.register(Transaction)
admin_site.register(Category)
admin_site.register(Budget)

# Đăng ký lại User vào custom admin site với UserAdmin

admin_site.register(User, UserAdmin)