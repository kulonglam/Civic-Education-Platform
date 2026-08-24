from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0006_phone_verified_activity_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='activity_type',
            field=models.CharField(
                choices=[
                    ('user_registered', 'User Registered'),
                    ('user_login', 'User Login'),
                    ('user_logout', 'User Logout'),
                    ('user_login_failed', 'User Login Failed'),
                    ('email_verified', 'Email Verified'),
                    ('phone_verified', 'Phone Verified'),
                    ('password_reset', 'Password Reset'),
                    ('user_suspended', 'User Suspended'),
                    ('user_unsuspended', 'User Unsuspended'),
                    ('user_role_changed', 'User Role Changed'),
                    ('user_deactivated', 'User Deactivated'),
                    ('data_exported', 'Data Exported'),
                    ('member_invited', 'Member Invited'),
                    ('member_removed', 'Member Removed'),
                    ('member_role_changed', 'Member Role Changed'),
                    ('org_settings_changed', 'Organization Settings Changed'),
                    ('sso_configured', 'SSO Configured'),
                    ('sso_login', 'SSO Login'),
                    ('bulk_import', 'Bulk Import'),
                    ('article_created', 'Article Created'),
                    ('article_updated', 'Article Updated'),
                    ('article_deleted', 'Article Deleted'),
                    ('article_submitted', 'Article Submitted for Review'),
                    ('article_approved', 'Article Approved'),
                    ('article_rejected', 'Article Rejected'),
                    ('quiz_created', 'Quiz Created'),
                    ('quiz_attempt', 'Quiz Attempt'),
                    ('certificate_issued', 'Certificate Issued'),
                    ('topic_created', 'Topic Created'),
                    ('comment_created', 'Comment Created'),
                    ('content_moderated', 'Content Moderated'),
                    ('admin_action', 'Admin Action'),
                    ('org_activated', 'Organization Activated'),
                    ('org_deactivated', 'Organization Deactivated'),
                    ('password_changed', 'Password Changed'),
                    ('session_revoked', 'Session Revoked'),
                    ('scim_user_provisioned', 'SCIM User Provisioned'),
                    ('scim_user_updated', 'SCIM User Updated'),
                    ('scim_user_deactivated', 'SCIM User Deactivated'),
                    ('support_case_opened', 'Support Case Opened'),
                    ('support_case_updated', 'Support Case Updated'),
                    ('compliance_pack_exported', 'Compliance Pack Exported'),
                    ('impersonation_started', 'Impersonation Started'),
                    ('impersonation_ended', 'Impersonation Ended'),
                ],
                db_index=True,
                max_length=50,
            ),
        ),
    ]
