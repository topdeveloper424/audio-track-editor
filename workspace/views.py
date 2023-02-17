from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, FileResponse
import json, os, pathlib
from django.core import serializers
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import text
from datetime import datetime
from pydub import AudioSegment
from workspace.models import VoiceTrack, BackgroundTrack, ResultTrack

VOICE_UPLOAD_DIRECTORY = "voices/"
BACKGROUND_UPLOAD_DIRECTORY = "backgrounds/"
RESULT_UPLOAD_DIRECTORY = "results/"
# Create your views here.
def home(request):
    voice_tracks = VoiceTrack.objects.all()
    background_tracks = BackgroundTrack.objects.all()
    result_tracks = ResultTrack.objects.all()
    result_tracks_top10 = result_tracks.order_by('-created_at')[:10]
    return render(request,'home.html', {'voices': voice_tracks, 'backgrounds':background_tracks, 'results': result_tracks_top10,'results_count': result_tracks.count()})

def voice_tracks(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    voice_tracks = VoiceTrack.objects.all().order_by('-created_at')
    items_per_page = 10
    paginator = Paginator(voice_tracks, items_per_page)
    items_page = []
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)    
    return render(request,'voice_tracks.html', {'voices': items_page})

@csrf_exempt
def upload_voice(request):
    if request.method == 'POST':
        track_name = request.POST.get("trackName")
        voice_track = VoiceTrack()
        voice_track.name = track_name
        voice_track.track_file.save(track_name+".mp3", request.FILES['file'], save=True)
        voice_track.save()
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def voice_track(request):
    if request.method == 'GET':
        track_id = request.GET.get("track_id")
        voice_track = VoiceTrack.objects.get(pk=track_id)
        serialized_object = serializers.serialize('json', [voice_track,])
        return HttpResponse(serialized_object,content_type="application/json")
    elif request.method == 'POST':
        track_id = request.POST.get("track_id")
        track_name = request.POST.get("track_name")
        voice_track = VoiceTrack.objects.get(pk=track_id)
        if track_name != voice_track.name:
            track_file = voice_track.track_file
            new_filename = text.slugify(track_name) + pathlib.Path(track_file.name).suffix
            new_file_path = os.path.join(settings.MEDIA_ROOT, VOICE_UPLOAD_DIRECTORY+new_filename)
            os.rename(track_file.path, new_file_path)        
            voice_track.track_file = new_file_path
            voice_track.name = track_name
            voice_track.save()
        return redirect('workspace:voice_tracks')

@csrf_exempt    
def delete_voice(request):
    if request.method == 'POST':
        track_id = request.POST.get("track_id")
        print(track_id)
        voice_track = VoiceTrack.objects.get(pk=track_id)
        voice_track.track_file.delete(save=False)
        voice_track.delete()
        response={}
        response['status'] = 'success'
        return HttpResponse(json.dumps(response),content_type="application/json")

def background_tracks(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    background_tracks = BackgroundTrack.objects.all().order_by('-created_at')
    items_per_page = 10
    paginator = Paginator(background_tracks, items_per_page)
    items_page = []
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)    

    return render(request,'background_tracks.html', {'backgrounds': items_page})

@csrf_exempt
def upload_background(request):
    if request.method == 'POST':
        track_name = request.POST.get("trackName")
        background_track = BackgroundTrack()
        background_track.name = track_name
        background_track.track_file.save(track_name+".mp3", request.FILES['file'], save=True)
        background_track.save()
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def background_track(request):
    if request.method == 'GET':
        track_id = request.GET.get("track_id")
        background_track = BackgroundTrack.objects.get(pk=track_id)
        serialized_object = serializers.serialize('json', [background_track,])
        return HttpResponse(serialized_object,content_type="application/json")
    elif request.method == 'POST':
        track_id = request.POST.get("track_id")
        track_name = request.POST.get("track_name")
        background_track = BackgroundTrack.objects.get(pk=track_id)
        if track_name != background_track.name:
            track_file = background_track.track_file
            new_filename = text.slugify(track_name) + pathlib.Path(track_file.name).suffix
            new_file_path = os.path.join(settings.MEDIA_ROOT, BACKGROUND_UPLOAD_DIRECTORY+new_filename)
            os.rename(track_file.path, new_file_path)        
            background_track.track_file = new_file_path
            background_track.name = track_name
            background_track.save()
        return redirect('workspace:background_tracks')

@csrf_exempt    
def delete_background(request):
    if request.method == 'POST':
        track_id = request.POST.get("track_id")
        print(track_id)
        background_track = BackgroundTrack.objects.get(pk=track_id)
        background_track.track_file.delete(save=False)
        background_track.delete()
        response={}
        response['status'] = 'success'
        return HttpResponse(json.dumps(response),content_type="application/json")

def result_tracks(request):
    voice_tracks = VoiceTrack.objects.all()
    background_tracks = BackgroundTrack.objects.all()
    default_page = 1
    page = request.GET.get('page', default_page)
    voice_id = None
    if 'voice_id' in request.GET:
        voice_id = request.GET.get('voice_id')
    background_id = None
    if 'background_id' in request.GET:
        background_id = request.GET.get('background_id')

    result_tracks = None
    if voice_id == None and background_id == None:
        result_tracks = ResultTrack.objects.all().order_by('-created_at')
    else:
        if voice_id:
            result_tracks = ResultTrack.objects.filter(voice_track__pk = voice_id).order_by('-created_at')
        if background_id:
            result_tracks = ResultTrack.objects.filter(background_track__pk = background_id).order_by('-created_at')

    items_per_page = 10
    paginator = Paginator(result_tracks, items_per_page)
    items_page = []
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)    

    return render(request,'result_tracks.html', {'results': items_page, 'voices':voice_tracks, 'backgrounds':background_tracks})

@csrf_exempt    
def result_track(request):
    if request.method == 'GET':
        track_id = request.GET.get("track_id")
        result_track = ResultTrack.objects.select_related('voice_track').select_related('background_track').get(pk=track_id)
        voice_track = {}
        voice_track["name"] = result_track.voice_track.name
        voice_track["url"] = result_track.voice_track.track_file.url
        background_track = {}
        background_track["name"] = result_track.background_track.name
        background_track["url"] = result_track.background_track.track_file.url

        result_json = {}
        result_json["name"] = result_track.name
        result_json["pk"] = result_track.pk
        result_json["db_level"] = result_track.db_level
        response = {}
        response["result"] = result_json
        response["voice"] = voice_track
        response["background"] = background_track
        return HttpResponse(json.dumps(response),content_type="application/json")
    elif request.method == 'POST':
        track_id = request.POST.get("track_id")
        track_name = request.POST.get("track_name")
        result_track = ResultTrack.objects.get(pk=track_id)
        if track_name != result_track.name:
            track_file = result_track.track_file
            new_filename = text.slugify(track_name) + pathlib.Path(track_file.name).suffix
            new_file_path = os.path.join(settings.MEDIA_ROOT, RESULT_UPLOAD_DIRECTORY+new_filename)
            os.rename(track_file.path, new_file_path)        
            result_track.track_file = new_file_path
            result_track.name = track_name
            result_track.save()
        return redirect('workspace:result_tracks')

@csrf_exempt    
def delete_result(request):
    if request.method == 'POST':
        track_id = request.POST.get("track_id")
        print(track_id)
        result_track = ResultTrack.objects.get(pk=track_id)
        result_track.track_file.delete(save=False)
        result_track.delete()
        response={}
        response['status'] = 'success'
        return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def proceed(request):
    if request.method == 'POST':
        volume_level = request.POST['level']
        voice_track_id = request.POST['voice_track_id']
        background_track_ids_str = request.POST['background_track_ids']
        background_track_ids = background_track_ids_str.split(",")
        handle_proceed(volume_level, voice_track_id, background_track_ids)
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")


def handle_proceed(volume_level, voice_track_id, background_track_ids):
    result_track_list = []
    voice_track = VoiceTrack.objects.get(pk=voice_track_id)
    voice = AudioSegment.from_mp3(voice_track.track_file.path)
    louder_song = voice + int(volume_level)
    for background_track_id in background_track_ids:
        background_track = BackgroundTrack.objects.get(pk=background_track_id)
        background = AudioSegment.from_mp3(background_track.track_file.path)
        generated = background.overlay(louder_song)
        result_filename = voice_track.name + "_" + background_track.name +"_"+ str(volume_level)
        result_filename = text.slugify(result_filename)
        result_file_path = os.path.join(settings.MEDIA_ROOT, RESULT_UPLOAD_DIRECTORY + result_filename + ".mp3")
        generated.export(result_file_path, format='mp3')

        result_track = ResultTrack()
        result_track.db_level = int(volume_level)
        result_track.voice_track = voice_track
        result_track.background_track = background_track
        result_track.name = result_filename
        result_track.track_file = RESULT_UPLOAD_DIRECTORY + result_filename + ".mp3"
        result_track.save()
        result_track_list.append(result_track)

    serialized_object = serializers.serialize('json', result_track_list)
    return HttpResponse(serialized_object,content_type="application/json")

