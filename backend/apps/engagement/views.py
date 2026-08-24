from django.db.models import Count, F
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import UserProfile
from apps.gamification.services import XP_CAMPAIGN_JOIN, XP_PETITION_SIGN, XP_POLL_VOTE, award_xp
from apps.tenants.permissions import CanDeleteOrgContent, IsOrgContentEditor, IsOrgMember

from .models import Campaign, CampaignSignup, Petition, PetitionSignature, Poll, PollOption, PollVote
from .serializers import (
    CampaignCreateSerializer,
    CampaignSerializer,
    PetitionCreateSerializer,
    PetitionSerializer,
    PollCreateSerializer,
    PollSerializer,
    PollVoteSerializer,
)


def _wants_manage(request) -> bool:
    return request.query_params.get('manage') in ('1', 'true', 'yes')


def _is_content_editor(request) -> bool:
    return IsOrgContentEditor().has_permission(request, None)


class PollListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOrgContentEditor()]
        return [IsOrgMember()]

    @extend_schema(responses=PollSerializer(many=True))
    def get(self, request):
        polls = Poll.objects.prefetch_related('options').order_by('-created_at')
        if not (_wants_manage(request) and _is_content_editor(request)):
            polls = polls.filter(status__in=[Poll.STATUS_OPEN, Poll.STATUS_CLOSED])
        kind = request.query_params.get('kind')
        if kind:
            polls = polls.filter(kind=kind)
        serializer = PollSerializer(polls, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=PollCreateSerializer, responses=PollSerializer)
    def post(self, request):
        serializer = PollCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        poll = serializer.save()
        return Response(
            PollSerializer(poll, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PollDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsOrgMember()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgContentEditor()]

    def _get_poll(self, poll_id, *, editor: bool):
        qs = Poll.objects.prefetch_related('options')
        poll = qs.filter(id=poll_id).first()
        if poll is None:
            return None
        if not editor and poll.status == Poll.STATUS_DRAFT:
            return None
        return poll

    @extend_schema(responses=PollSerializer)
    def get(self, request, poll_id):
        poll = self._get_poll(poll_id, editor=_is_content_editor(request))
        if poll is None:
            return Response({'detail': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PollSerializer(poll, context={'request': request}).data)

    @extend_schema(request=PollCreateSerializer, responses=PollSerializer)
    def patch(self, request, poll_id):
        poll = Poll.objects.filter(id=poll_id).prefetch_related('options').first()
        if poll is None:
            return Response({'detail': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PollCreateSerializer(
            poll, data=request.data, partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        poll = serializer.save()
        return Response(PollSerializer(poll, context={'request': request}).data)

    def delete(self, request, poll_id):
        poll = Poll.objects.filter(id=poll_id).first()
        if poll is None:
            return Response({'detail': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)
        poll.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PollVoteView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(request=PollVoteSerializer, responses=PollSerializer)
    def post(self, request, poll_id):
        poll = Poll.objects.filter(id=poll_id).prefetch_related('options').first()
        if poll is None:
            return Response({'detail': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not poll.is_open:
            return Response({'detail': 'Poll is closed.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PollVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        option = PollOption.objects.filter(id=serializer.validated_data['option_id'], poll=poll).first()
        if option is None:
            return Response({'detail': 'Invalid option.'}, status=status.HTTP_400_BAD_REQUEST)

        if PollVote.objects.filter(poll=poll, user=request.user).exists():
            return Response({'detail': 'You already voted on this poll.'}, status=status.HTTP_400_BAD_REQUEST)

        profile = UserProfile.objects.filter(user_id=request.user.id).first()
        PollVote.objects.create(
            organization=poll.organization,
            poll=poll,
            option=option,
            user=request.user,
            region=(getattr(profile, 'region', '') or ''),
            age_band=(getattr(profile, 'age_band', '') or ''),
        )
        PollOption.objects.filter(id=option.id).update(vote_count=F('vote_count') + 1)
        award_xp(request.user, XP_POLL_VOTE, reason='poll_vote')

        poll.refresh_from_db()
        return Response(PollSerializer(poll, context={'request': request}).data)


class PetitionListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOrgContentEditor()]
        return [IsOrgMember()]

    @extend_schema(responses=PetitionSerializer(many=True))
    def get(self, request):
        petitions = Petition.objects.all()
        if not (_wants_manage(request) and _is_content_editor(request)):
            petitions = petitions.filter(status__in=[Petition.STATUS_OPEN, Petition.STATUS_CLOSED])
        serializer = PetitionSerializer(petitions, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=PetitionCreateSerializer, responses=PetitionSerializer)
    def post(self, request):
        serializer = PetitionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        petition = serializer.save()
        return Response(
            PetitionSerializer(petition, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PetitionDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsOrgMember()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgContentEditor()]

    def _get_petition(self, petition_id, *, editor: bool):
        petition = Petition.objects.filter(id=petition_id).first()
        if petition is None:
            return None
        if not editor and petition.status == Petition.STATUS_DRAFT:
            return None
        return petition

    @extend_schema(responses=PetitionSerializer)
    def get(self, request, petition_id):
        petition = self._get_petition(petition_id, editor=_is_content_editor(request))
        if petition is None:
            return Response({'detail': 'Petition not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PetitionSerializer(petition, context={'request': request}).data)

    @extend_schema(request=PetitionCreateSerializer, responses=PetitionSerializer)
    def patch(self, request, petition_id):
        petition = Petition.objects.filter(id=petition_id).first()
        if petition is None:
            return Response({'detail': 'Petition not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PetitionCreateSerializer(
            petition, data=request.data, partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        petition = serializer.save()
        return Response(PetitionSerializer(petition, context={'request': request}).data)

    def delete(self, request, petition_id):
        petition = Petition.objects.filter(id=petition_id).first()
        if petition is None:
            return Response({'detail': 'Petition not found.'}, status=status.HTTP_404_NOT_FOUND)
        petition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PetitionSignView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses=PetitionSerializer)
    def post(self, request, petition_id):
        petition = Petition.objects.filter(id=petition_id).first()
        if petition is None:
            return Response({'detail': 'Petition not found.'}, status=status.HTTP_404_NOT_FOUND)
        if petition.status != Petition.STATUS_OPEN:
            return Response({'detail': 'Petition is not open.'}, status=status.HTTP_400_BAD_REQUEST)

        if PetitionSignature.objects.filter(petition=petition, user=request.user).exists():
            return Response({'detail': 'You already signed this petition.'}, status=status.HTTP_400_BAD_REQUEST)

        PetitionSignature.objects.create(
            organization=petition.organization,
            petition=petition,
            user=request.user,
        )
        award_xp(request.user, XP_PETITION_SIGN, reason='petition_sign')

        petition.refresh_from_db()
        return Response(PetitionSerializer(petition, context={'request': request}).data)


class CampaignListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOrgContentEditor()]
        return [IsOrgMember()]

    @extend_schema(responses=CampaignSerializer(many=True))
    def get(self, request):
        campaigns = Campaign.objects.annotate(signup_count=Count('signups'))
        if not (_wants_manage(request) and _is_content_editor(request)):
            campaigns = campaigns.filter(status=Campaign.STATUS_ACTIVE)
        serializer = CampaignSerializer(campaigns, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(request=CampaignCreateSerializer, responses=CampaignSerializer)
    def post(self, request):
        serializer = CampaignCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        campaign = serializer.save()
        return Response(
            CampaignSerializer(campaign, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class CampaignDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsOrgMember()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgContentEditor()]

    def _get_campaign(self, campaign_id, *, editor: bool):
        campaign = Campaign.objects.filter(id=campaign_id).first()
        if campaign is None:
            return None
        if not editor and campaign.status != Campaign.STATUS_ACTIVE:
            return None
        return campaign

    @extend_schema(responses=CampaignSerializer)
    def get(self, request, campaign_id):
        campaign = self._get_campaign(campaign_id, editor=_is_content_editor(request))
        if campaign is None:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CampaignSerializer(campaign, context={'request': request}).data)

    @extend_schema(request=CampaignCreateSerializer, responses=CampaignSerializer)
    def patch(self, request, campaign_id):
        campaign = Campaign.objects.filter(id=campaign_id).first()
        if campaign is None:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CampaignCreateSerializer(
            campaign, data=request.data, partial=True, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        campaign = serializer.save()
        return Response(CampaignSerializer(campaign, context={'request': request}).data)

    def delete(self, request, campaign_id):
        campaign = Campaign.objects.filter(id=campaign_id).first()
        if campaign is None:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampaignJoinView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses=CampaignSerializer)
    def post(self, request, campaign_id):
        campaign = Campaign.objects.filter(id=campaign_id).first()
        if campaign is None:
            return Response({'detail': 'Campaign not found.'}, status=status.HTTP_404_NOT_FOUND)
        if campaign.status != Campaign.STATUS_ACTIVE:
            return Response({'detail': 'Campaign is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        _, created = CampaignSignup.objects.get_or_create(
            organization=campaign.organization,
            campaign=campaign,
            user=request.user,
        )
        if created:
            award_xp(request.user, XP_CAMPAIGN_JOIN, reason='campaign_join')
        return Response(CampaignSerializer(campaign, context={'request': request}).data)
