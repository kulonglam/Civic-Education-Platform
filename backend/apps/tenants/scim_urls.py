from django.urls import path

from .scim import ScimUserDetailView, ScimUsersView
from .scim_groups import ScimGroupDetailView, ScimGroupsView

urlpatterns = [
    path('Users', ScimUsersView.as_view(), name='scim-users'),
    path('Users/', ScimUsersView.as_view(), name='scim-users-slash'),
    path('Users/<str:user_id>', ScimUserDetailView.as_view(), name='scim-user-detail'),
    path('Users/<str:user_id>/', ScimUserDetailView.as_view(), name='scim-user-detail-slash'),
    path('Groups', ScimGroupsView.as_view(), name='scim-groups'),
    path('Groups/', ScimGroupsView.as_view(), name='scim-groups-slash'),
    path('Groups/<str:group_id>', ScimGroupDetailView.as_view(), name='scim-group-detail'),
    path('Groups/<str:group_id>/', ScimGroupDetailView.as_view(), name='scim-group-detail-slash'),
]
