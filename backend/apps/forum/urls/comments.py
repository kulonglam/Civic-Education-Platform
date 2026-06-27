from django.urls import path

from ..views import CommentModerateView

urlpatterns = [
    path('<uuid:id>/moderate/', CommentModerateView.as_view(), name='comment-moderate'),
]
