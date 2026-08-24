from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CertificateDownloadView,
    CertificateListView,
    QuizAttemptView,
    QuizCheckAnswerView,
    QuizResultsView,
    QuizViewSet,
)

router = DefaultRouter()
router.register('', QuizViewSet, basename='quiz')

urlpatterns = [
    path('results/', QuizResultsView.as_view(), name='quiz-results'),
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<uuid:id>/download/', CertificateDownloadView.as_view(), name='certificate-download'),
    path('<uuid:id>/attempt/', QuizAttemptView.as_view(), name='quiz-attempt'),
    path('<uuid:id>/check-answer/', QuizCheckAnswerView.as_view(), name='quiz-check-answer'),
] + router.urls
