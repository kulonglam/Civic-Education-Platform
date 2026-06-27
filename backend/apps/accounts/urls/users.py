from django.urls import path

from ..views import (
    AvatarUploadView,
    ProfileView,
    SuspendUserView,
    UnsuspendUserView,
    UpdateUserRoleView,
    UserListView,
)

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='user-avatar'),
    path('<uuid:user_id>/suspend/', SuspendUserView.as_view(), name='user-suspend'),
    path('<uuid:user_id>/unsuspend/', UnsuspendUserView.as_view(), name='user-unsuspend'),
    path('<uuid:user_id>/role/', UpdateUserRoleView.as_view(), name='user-role'),
]
