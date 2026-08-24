from django.urls import path

from .views import (
    CampaignDetailView,
    CampaignJoinView,
    CampaignListCreateView,
    PetitionDetailView,
    PetitionListCreateView,
    PetitionSignView,
    PollDetailView,
    PollListCreateView,
    PollVoteView,
)

urlpatterns = [
    path('polls/', PollListCreateView.as_view(), name='engagement-polls'),
    path('polls/<uuid:poll_id>/', PollDetailView.as_view(), name='engagement-poll-detail'),
    path('polls/<uuid:poll_id>/vote/', PollVoteView.as_view(), name='engagement-poll-vote'),
    path('petitions/', PetitionListCreateView.as_view(), name='engagement-petitions'),
    path('petitions/<uuid:petition_id>/', PetitionDetailView.as_view(), name='engagement-petition-detail'),
    path('petitions/<uuid:petition_id>/sign/', PetitionSignView.as_view(), name='engagement-petition-sign'),
    path('campaigns/', CampaignListCreateView.as_view(), name='engagement-campaigns'),
    path('campaigns/<uuid:campaign_id>/', CampaignDetailView.as_view(), name='engagement-campaign-detail'),
    path('campaigns/<uuid:campaign_id>/join/', CampaignJoinView.as_view(), name='engagement-campaign-join'),
]
