from django.db.models import F
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.gamification.services import XP_PETITION_SIGN, XP_POLL_VOTE, award_xp
from apps.tenants.permissions import IsOrgContentEditor, IsOrgMember

from .models import Campaign, Petition, PetitionSignature, Poll, PollOption, PollVote
from .serializers import (
    CampaignCreateSerializer,
    CampaignSerializer,
    PetitionCreateSerializer,
    PetitionSerializer,
    PollCreateSerializer,
    PollSerializer,
    PollVoteSerializer,
)


class PollListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOrgContentEditor()]
        return [IsOrgMember()]

    @extend_schema(responses=PollSerializer(many=True))
    def get(self, request):
        polls = (
            Poll.objects.filter(status__in=[Poll.STATUS_OPEN, Poll.STATUS_CLOSED])
            .prefetch_related('options')
            .order_by('-created_at')
        )
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

        PollVote.objects.create(
            organization=poll.organization,
            poll=poll,
            option=option,
            user=request.user,
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
        petitions = Petition.objects.filter(status__in=[Petition.STATUS_OPEN, Petition.STATUS_CLOSED])
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
        campaigns = Campaign.objects.filter(status=Campaign.STATUS_ACTIVE)
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
