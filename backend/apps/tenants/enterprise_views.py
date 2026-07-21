"""Enterprise org APIs: SSO config, departments, bulk import, platform org console."""

from datetime import timedelta

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.models import Subscription
from apps.billing.services import require_sso
from apps.core.permissions import IsAdmin
from apps.learning.models import Article
from apps.quizzes.models import Certificate, QuizAttempt
from apps.tenants.context import get_current_organization
from apps.tenants.models import Department, Membership, Organization, OrganizationSsoConfig
from apps.tenants.permissions import IsOrgOwnerOrAdmin
from apps.tenants.serializers import (
    BulkImportSerializer,
    DepartmentSerializer,
    OrganizationSsoConfigSerializer,
)
from apps.tenants.services import bulk_provision_members


def _org_support_snapshot(organization):
    """Read-only metrics for platform support (no impersonation)."""
    sub = (
        Subscription.objects.filter(organization=organization)
        .select_related('plan')
        .first()
    )
    thirty_days_ago = timezone.now() - timedelta(days=30)
    return {
        'id': str(organization.id),
        'name': organization.name,
        'slug': organization.slug,
        'tagline': organization.tagline,
        'is_active': organization.is_active,
        'force_mfa_for_admins': organization.force_mfa_for_admins,
        'audit_retention_days': organization.audit_retention_days,
        'member_count': organization.memberships.count(),
        'department_count': organization.departments.count(),
        'plan_code': sub.plan.code if sub and sub.plan_id else None,
        'plan_name': sub.plan.name if sub and sub.plan_id else None,
        'published_articles': Article.objects.filter(
            organization=organization, status='published'
        ).count(),
        'pending_review_articles': Article.objects.filter(
            organization=organization, status='pending_review'
        ).count(),
        'controlled_documents': Article.objects.filter(
            organization=organization, is_controlled_document=True
        ).count(),
        'quiz_attempts': QuizAttempt.objects.filter(organization=organization).count(),
        'certificates_issued': Certificate.objects.filter(organization=organization).count(),
        'active_learners_30d': (
            QuizAttempt.objects.filter(
                organization=organization,
                attempted_at__gte=thirty_days_ago,
            )
            .values('user_id')
            .distinct()
            .count()
        ),
        'created_at': organization.created_at,
    }


class OrganizationSsoConfigView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    def get(self, request):
        organization = get_current_organization()
        require_sso(organization)
        config, _ = OrganizationSsoConfig.objects.get_or_create(organization=organization)
        return Response(OrganizationSsoConfigSerializer(config).data)

    def put(self, request):
        organization = get_current_organization()
        require_sso(organization)
        config, _ = OrganizationSsoConfig.objects.get_or_create(organization=organization)
        serializer = OrganizationSsoConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(
            request.user,
            'sso_configured',
            {'enabled': config.enabled, 'issuer': config.issuer},
            organization=organization,
            request=request,
        )
        return Response(OrganizationSsoConfigSerializer(config).data)


class DepartmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = DepartmentSerializer
    pagination_class = None

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return Department.objects.none()
        return Department.objects.filter(organization=organization)

    def perform_create(self, serializer):
        organization = get_current_organization()
        name = serializer.validated_data['name']
        slug = serializer.validated_data.get('slug') or slugify(name)
        serializer.save(organization=organization, slug=slug)


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return Department.objects.none()
        return Department.objects.filter(organization=organization)


class BulkMemberImportView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=BulkImportSerializer, responses={200: dict})
    def post(self, request):
        organization = get_current_organization()
        serializer = BulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        result = bulk_provision_members(
            organization=organization,
            rows=data['rows'],
            invited_by=request.user,
            dry_run=data['dry_run'],
            send_invites=data['send_invites'],
        )
        if not data['dry_run']:
            log_activity(
                request.user,
                'bulk_import',
                {
                    'created_memberships': result['created_memberships'],
                    'invites_sent': result['invites_sent'],
                    'error_count': len(result['errors']),
                },
                organization=organization,
                request=request,
            )
        return Response(result)


class PlatformOrganizationListView(APIView):
    """Platform admin: list/search all tenants."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        qs = Organization.objects.annotate(member_count=Count('memberships'))
        search = (request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(slug__icontains=search)
        active = request.query_params.get('is_active')
        if active in ('true', 'false'):
            qs = qs.filter(is_active=active == 'true')

        results = []
        for org in qs.order_by('name')[:200]:
            sub = (
                Subscription.objects.filter(organization=org)
                .select_related('plan')
                .first()
            )
            results.append(
                {
                    'id': str(org.id),
                    'name': org.name,
                    'slug': org.slug,
                    'tagline': org.tagline,
                    'is_active': org.is_active,
                    'member_count': org.member_count,
                    'plan_code': sub.plan.code if sub and sub.plan_id else None,
                    'created_at': org.created_at,
                }
            )
        return Response({'results': results, 'count': len(results)})


class PlatformOrganizationDetailView(APIView):
    """Platform admin: activate/deactivate or view read-only support metrics."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, org_id):
        organization = get_object_or_404(Organization, id=org_id)
        return Response(_org_support_snapshot(organization))

    def patch(self, request, org_id):
        organization = get_object_or_404(Organization, id=org_id)
        is_active = request.data.get('is_active')
        if is_active is None:
            return Response({'detail': 'is_active is required.'}, status=status.HTTP_400_BAD_REQUEST)
        organization.is_active = bool(is_active)
        organization.save(update_fields=['is_active', 'updated_at'])
        log_activity(
            request.user,
            'org_activated' if organization.is_active else 'org_deactivated',
            {'org_slug': organization.slug, 'org_id': str(organization.id)},
            organization=organization,
            request=request,
        )
        return Response(_org_support_snapshot(organization))


class PlatformUsageSummaryView(APIView):
    """Cross-org usage rollup for ministry-of-education style operators."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        orgs = Organization.objects.annotate(member_count=Count('memberships')).order_by('name')
        rows = []
        totals = {
            'organizations': 0,
            'active_organizations': 0,
            'members': 0,
            'published_articles': 0,
            'quiz_attempts': 0,
            'certificates': 0,
            'active_learners_30d': 0,
        }
        for org in orgs[:200]:
            snap = _org_support_snapshot(org)
            rows.append({
                'id': snap['id'],
                'name': snap['name'],
                'slug': snap['slug'],
                'is_active': snap['is_active'],
                'plan_code': snap['plan_code'],
                'member_count': snap['member_count'],
                'published_articles': snap['published_articles'],
                'quiz_attempts': snap['quiz_attempts'],
                'certificates_issued': snap['certificates_issued'],
                'active_learners_30d': snap['active_learners_30d'],
            })
            totals['organizations'] += 1
            if snap['is_active']:
                totals['active_organizations'] += 1
            totals['members'] += snap['member_count']
            totals['published_articles'] += snap['published_articles']
            totals['quiz_attempts'] += snap['quiz_attempts']
            totals['certificates'] += snap['certificates_issued']
            totals['active_learners_30d'] += snap['active_learners_30d']

        return Response({
            'totals': totals,
            'organizations': rows,
            'generated_at': timezone.now(),
            'window_start': thirty_days_ago,
        })
