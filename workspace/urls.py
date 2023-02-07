from django.urls import path
from . import views

app_name = 'workspace'

urlpatterns = [
    path('', views.home,name='home'),
    path('upload-voice', views.upload_voice,name='upload_voice'),
    path('upload-background', views.upload_background,name='upload_background'),
    path('proceed', views.proceed,name='proceed'),
    path('download-result', views.download_result,name='download_result'),
]

