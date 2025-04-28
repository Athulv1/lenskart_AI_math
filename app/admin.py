from django.contrib import admin
from app.models import Project, ProjectFile

class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1  # Number of empty forms to display for adding new files
    fields = ['file', 'created_at']
    readonly_fields = ['created_at']

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectFileInline]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

# Register with custom admin classes
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectFile)  # Keep this to also access files directly if needed