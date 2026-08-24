from django.urls import path

from ..views import CommentModerateView, CommentReportView

urlpatterns = [
    path('<uuid:id>/moderate/', CommentModerateView.as_view(), name='comment-moderate'),
    path('<uuid:id>/report/', CommentReportView.as_view(), name='comment-report'),
]
