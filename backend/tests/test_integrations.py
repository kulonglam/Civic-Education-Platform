import pytest
from django.core.management import call_command
from io import StringIO
from rest_framework import status

from apps.core.integrations import (
    STATUS_DUMMY,
    STATUS_EAGER,
    STATUS_LIVE,
    build_integrations_report,
    check_pypdf,
    check_stripe,
    check_tutor_provider,
)


@pytest.mark.django_db
class TestIntegrationsModule:
    def test_stripe_dummy_in_test_settings(self, settings):
        settings.BILLING_PROVIDER = 'dummy'
        row = check_stripe()
        assert row['status'] == STATUS_DUMMY

    def test_tutor_provider_unset_is_dummy(self, settings):
        settings.TUTOR_PROVIDER = 'auto'
        settings.ANTHROPIC_API_KEY = ''
        settings.OPENAI_API_KEY = ''
        settings.OPENAI_BASE_URL = ''
        row = check_tutor_provider()
        assert row['status'] == STATUS_DUMMY
        assert row['meta']['provider'] == 'stub'

    def test_tutor_provider_anthropic_key_is_live(self, settings):
        settings.TUTOR_PROVIDER = 'auto'
        settings.ANTHROPIC_API_KEY = 'sk-ant-test'
        row = check_tutor_provider()
        assert row['status'] == STATUS_LIVE
        assert row['meta']['provider'] == 'anthropic'

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
        assert response.data['database'] == STATUS_LIVE
        assert response.data['cache'] == STATUS_LIVE
        assert response.data['status'] == 'ready'
        assert response.status_code == status.HTTP_200_OK
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
