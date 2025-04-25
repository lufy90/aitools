from django.contrib import admin
from .models import Annotation, Step, Action
from django.utils.html import format_html


class BaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'created_by')
    search_fields = ('name', 'description')
    list_filter = ('created_by', 'created_at')
#    readonly_fields = ('created_by',)

    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    class Meta:
        abstract = True

class AnnotationAdmin(BaseAdmin):
    pass


class StepAdmin(BaseAdmin):
    exclude = ("bbox_start", "bbox_end", "description", "created_by")
    readonly_fields = ['connect_pc', 'current_pos', 'current_start', 'current_end',
            'image',
            ]

    def connect_pc(self, obj):
        return format_html('<a class="button" href="https://example.com" target="_blank">Connect</a>')

    def current_pos(self, obj):
        return format_html('<p>1,2</p>')

    connect_pc.shot_description = "Connect PC"

    def current_start(self, obj):
        return format_html('<p>1,2</p>')

    def current_end(self, obj):
        return format_html('<p>1,2</p>')


class ActionAdmin(BaseAdmin):
    pass

admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Step, StepAdmin)
admin.site.register(Action, ActionAdmin)
