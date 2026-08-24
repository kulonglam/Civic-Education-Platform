import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_alter_notification_notification_type'),
        ('tenants', '0002_organization_invites'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationpreference',
            name='whatsapp',
            field=models.BooleanField(
                default=False,
                help_text='Send civic alerts on WhatsApp (same phone number as SMS).',
            ),
        ),
        migrations.CreateModel(
            name='WhatsAppMessage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('phone', models.CharField(db_index=True, max_length=20)),
                ('message', models.TextField()),
                ('message_type', models.CharField(
                    choices=[('alert', 'Alert'), ('broadcast', 'Broadcast'), ('inbound', 'Inbound')],
                    default='alert',
                    max_length=20,
                )),
                ('direction', models.CharField(
                    choices=[('outbound', 'Outbound'), ('inbound', 'Inbound')],
                    default='outbound',
                    max_length=12,
                )),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')],
                    default='pending',
                    max_length=20,
                )),
                ('provider_reference', models.CharField(blank=True, max_length=255)),
                ('error_detail', models.TextField(blank=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='%(class)ss',
                    to='tenants.organization',
                )),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='whatsapp_messages',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'whatsapp_messages',
                'ordering': ['-created_at'],
            },
        ),
    ]
