from django.contrib import admin

from .models import DiscussionComment, DiscussionTopic

admin.site.register(DiscussionTopic)
admin.site.register(DiscussionComment)
