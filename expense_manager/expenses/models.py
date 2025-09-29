from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Thu nhập'),
        ('expense', 'Chi tiêu'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)   # mỗi user có nhiều giao dịch
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # số tiền
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)   # income / expense
    date = models.DateField()   # ngày giao dịch
    note = models.TextField(blank=True)   # ghi chú

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.DateField()  

    def __str__(self):
        return f"{self.user.username} - {self.category or 'Tổng'} - {self.month.strftime('%m/%Y')}"
# class CustomUser(AbstractUser):
#     role = models.CharField(
#         max_length=20,
#         choices=[("admin", "Admin"), ("user", "User")],
#         default="user"
#     )