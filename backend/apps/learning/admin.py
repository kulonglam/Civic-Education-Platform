from django.contrib import admin

from .models import Article, Bookmark, Category, Course, CourseLesson, MediaAsset

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(MediaAsset)
admin.site.register(Bookmark)
admin.site.register(Course)
admin.site.register(CourseLesson)
