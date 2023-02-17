from django.contrib import admin
from workspace.models import VoiceTrack, BackgroundTrack, ResultTrack

# Register your models here.
admin.site.register(VoiceTrack)
admin.site.register(BackgroundTrack)
admin.site.register(ResultTrack)
