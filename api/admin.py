from django.contrib import admin
from .models import SystemPrompt

@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'prompt')
    list_editable = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('name', 'prompt', 'is_active')
        }),
    )
