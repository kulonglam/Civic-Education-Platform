import pytest
from django.core.management import call_command
from io import StringIO
from rest_framework import status

from apps.core.integrations import (
    STATUS_DUMMY,
    STATUS_EAGER,
    STATUS_LIVE,
    build_integrations_report,
    check_anthropic,
    check_pypdf,
    check_stripe,
)


@pytest.mark.django_db
class TestIntegrationsModule:
    def test_stripe_dummy_in_test_settings(self, settings):
        settings.BILLING_PROVIDER = 'dummy'
        row = check_stripe()
        assert row['status'] == STATUS_DUMMY

    def test_anthropic_unset_is_dummy(self, settings):
        settings.ANTHROPIC_API_KEY = ''
        row = check_anthropic()
        assert row['status'] == STATUS_DUMMY

    def test_pypdf_installed(self):
        row = check_pypdf()
        assert row['status'] == STATUS_LIVE

    def test_build_report_has_summary(self):
        report = build_integrations_report(include_infra=True)
        assert 'summary' in report
        assert 'integrations' in report
        assert len(report['integrations']) >= 8


@pytest.mark.django_db
class TestReadinessEndpoint:
    def test_ready_includes_celery(self, api_client, settings):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        response = api_client.get('/api/ready/')
        assert 'celery' in response.data
        assert response.data['celery'] == STATUS_EAGER
        assert response.data['status'] in ('ready', 'degraded')
        assert 'integrations/status/' in response.data['observability']['integrations']


@pytest.mark.django_db
class TestIntegrationsStatusEndpoint:
    def test_requires_platform_admin(self, api_client, org, citizen_user):
        from tests.conftest import bind_client_to_org

        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/integrations/status/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_gets_report(self, api_client, org, admin_user):
        from tests.conftest import bind_client_to_org

        bind_client_to_org(api_client, admin_user, org)
        response = api_client.get('/api/integrations/status/')
        assert response.status_code == status.HTTP_200_OK
        assert 'integrations' in response.data
        assert 'summary' in response.data


@pytest.mark.django_db
class TestCheckIntegrationsCommand:
    def test_command_runs(self):
        out = StringIO()
        call_command('check_integrations', stdout=out)
        assert 'Integration status' in out.getvalue()

    def test_json_output(self):
        out = StringIO()
        call_command('check_integrations', '--json', stdout=out)
        assert '"integrations"' in out.getvalue()
