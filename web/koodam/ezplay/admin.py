from django.contrib import admin

# Register your models here.
from ezplay.models import Snippet, RecentSnippets

class SnippetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Snippet, SnippetAdmin)

class RecentSnippetsAdmin(admin.ModelAdmin):
    pass
admin.site.register(RecentSnippets, RecentSnippetsAdmin)
