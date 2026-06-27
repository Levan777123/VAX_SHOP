from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import LoginView, LogoutView, MeView, RefreshView, RegisterView, UserAdminViewSet

router = DefaultRouter()
router.register(r'users', UserAdminViewSet, basename='admin-users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', RefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
