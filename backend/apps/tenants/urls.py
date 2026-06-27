from django.urls import path

from .views import (
    AcceptInviteView,
    CurrentOrganizationView,
    InvitePreviewView,
    LeaveOrganizationView,
    MemberDetailView,
    MemberInviteView,
    MembershipListView,
    MyOrganizationsView,
    OrganizationBySlugView,
    OrganizationInviteListView,
    OrganizationInviteRevokeView,
)

urlpatterns = [
    path('current/', CurrentOrganizationView.as_view(), name='organization-current'),
    path('mine/', MyOrganizationsView.as_view(), name='organization-mine'),
    path('by-slug/<slug:slug>/', OrganizationBySlugView.as_view(), name='organization-by-slug'),
    path('members/', MembershipListView.as_view(), name='organization-members'),
    path('members/invite/', MemberInviteView.as_view(), name='organization-member-invite'),
    path('members/<uuid:membership_id>/', MemberDetailView.as_view(), name='organization-member-detail'),
    path('invites/', OrganizationInviteListView.as_view(), name='organization-invites'),
    path('invites/<uuid:invite_id>/', OrganizationInviteRevokeView.as_view(), name='organization-invite-revoke'),
    path('invites/accept/<str:token>/', AcceptInviteView.as_view(), name='organization-invite-accept'),
    path('invites/preview/<str:token>/', InvitePreviewView.as_view(), name='organization-invite-preview'),
    path('leave/', LeaveOrganizationView.as_view(), name='organization-leave'),
]
