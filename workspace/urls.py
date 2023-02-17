from django.urls import path
from . import views

app_name = 'workspace'

urlpatterns = [
    path('', views.home,name='home'),
    path('voice-tracks', views.voice_tracks,name='voice_tracks'),
    path('upload-voice', views.upload_voice,name='upload_voice'),
    path('voice-track', views.voice_track,name='voice_track'),
    path('delete-voice', views.delete_voice,name='delete_voice'),
 
    path('background-tracks', views.background_tracks,name='background_tracks'),
    path('upload-background', views.upload_background,name='upload_background'),
    path('background-track', views.background_track,name='background_track'),
    path('delete-background', views.delete_background,name='delete_background'),
 
    path('result-tracks', views.result_tracks,name='result_tracks'),
    path('result-track', views.result_track,name='result_track'),
    path('delete-result', views.delete_result,name='delete_result'),
 
    path('proceed', views.proceed,name='proceed'),
]

