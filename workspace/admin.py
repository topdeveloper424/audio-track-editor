from django.contrib import admin
from workspace.models import VoiceTrack, BackgroundTrack, ResultTrack, FrequencyTrack, ProgressBar

# Register your models here.
admin.site.register(VoiceTrack)
admin.site.register(BackgroundTrack)
admin.site.register(ResultTrack)
admin.site.register(FrequencyTrack)
admin.site.register(ProgressBar)
