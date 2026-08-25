"""Fail-closed tenancy, append-only audit, and WORM replica."""

import pytest
from rest_framework import status

from apps.audit.services import log_activity
from apps.learning.models import Article
from apps.tenants.context import reset_tenant_fail_closed, set_tenant_fail_closed


@pytest.mark.django_db
class TestFailClosedTenancy:
    def test_manager_hides_rows_without_org_when_fail_closed(
        self, org, category, editor_user
    ):
        article = Article.objects.create(
            title='Tenant lesson',
            content='Body',
            category=category,
            author=editor_user,
            organization=org,
            status='published',
        )
        token = set_tenant_fail_closed(True)
        try:
            assert Article.objects.count() == 0
            assert Article.all_objects.filter(id=article.id).exists()
        finally:
            reset_tenant_fail_closed(token)

    def test_public_article_list_without_tenant_is_empty(
        self, api_client, org, category, editor_user
    ):
        Article.objects.create(
            title='Visible only with tenant',
            content='Body',
            category=category,
            author=editor_user,
            organization=org,
            status='published',
        )
        empty = api_client.get('/api/articles/')
        assert empty.status_code == status.HTTP_200_OK
        assert empty.data['count'] == 0

        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        scoped = api_client.get('/api/articles/')
        assert scoped.status_code == status.HTTP_200_OK
        assert scoped.data['count'] == 1


@pytest.mark.django_db
class TestAuditAppendOnly:
    def test_hashed_log_cannot_be_updated(self, citizen_user, org):
        entry = log_activity(citizen_user, 'admin_action', {'n': 1}, organization=org)
        entry.activity_type = 'user_login'
        with pytest.raises(ValueError, match='append-only'):
            entry.save()

    def test_worm_replica_written(self, settings, tmp_path, citizen_user, org):
        worm = tmp_path / 'audit-worm.jsonl'
        settings.AUDIT_WORM_PATH = str(worm)
        log_activity(citizen_user, 'admin_action', {'source': 'test'}, organization=org)
        text = worm.read_text(encoding='utf-8')
        assert 'admin_action' in text
        assert 'integrity_hash' in text
