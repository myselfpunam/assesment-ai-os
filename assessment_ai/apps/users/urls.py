from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    MeView,
    ChangePasswordView,
    LecturerProfileView,
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('me/', MeView.as_view(), name='user-me'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('<uuid:lecturer_id>/teaching-profile/', LecturerProfileView.as_view(), name='lecturer-profile'),
]
