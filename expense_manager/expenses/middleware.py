from django.utils.deprecation import MiddlewareMixin

class AdminUserSessionMiddleware(MiddlewareMixin):
    """
    Middleware để tách session của admin và user thường.
    """
    def process_request(self, request):
        # Nếu truy cập trang admin -> dùng session riêng
        if request.path.startswith("/admin/"):
            admin_session = request.COOKIES.get("admin_sessionid")
            if admin_session:
                request.session._session_key = admin_session
