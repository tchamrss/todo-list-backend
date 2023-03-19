from django.contrib import admin
from videoflix_app.models import Video
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
#admin.site.register(Video)
# Register your models here.
class VideoAdmin(ImportExportModelAdmin):
    fields = ('title','description', 'created_at', 'video_file', 'genres','playtime','picture', 'likes') 
    list_display = ('title','description', 'genres','playtime','picture', 'likes')
    search_fields = ('title',)
class VideoResource(resources.ModelResource):

    class Meta:
        model = Video

admin.site.register(Video, VideoAdmin)
