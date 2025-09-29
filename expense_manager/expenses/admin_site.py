from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "Expense Manager - Admin"
    site_title = "Expense Manager Admin"
    index_title = "Quản trị hệ thống"

    def login(self, request, extra_context=None):
        # Gọi login mặc định
        response = super().login(request, extra_context)
        # Nếu đăng nhập thành công -> tạo cookie session riêng cho admin
        if request.user.is_authenticated:
            request.session.save()
            response.set_cookie("admin_sessionid", request.session.session_key)
        return response

# Tạo instance để dùng trong urls.py
admin_site = CustomAdminSite(name="custom_admin")
