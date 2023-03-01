from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, StreamingHttpResponse
import json, os, pathlib, io
from django.core import serializers
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import text
from pydub import AudioSegment
from workspace.models import VoiceTrack, BackgroundTrack, ResultTrack, FrequencyTrack, ProgressBar
import zipfile

VOICE_UPLOAD_DIRECTORY = "voices/"
BACKGROUND_UPLOAD_DIRECTORY = "backgrounds/"
FREQUENCY_UPLOAD_DIRECTORY = "frequency/"
RESULT_UPLOAD_DIRECTORY = "results/"
# Create your views here.
def home(request):
    voice_tracks = VoiceTrack.objects.all()
    background_tracks = BackgroundTrack.objects.all()
    result_tracks = ResultTrack.objects.all()
    frequency_tracks = FrequencyTrack.objects.all()
    result_tracks_top10 = result_tracks.order_by('-created_at')[:10]
    return render(request,'home.html', {'voices': voice_tracks, 'backgrounds':background_tracks,'frequencies':frequency_tracks, 'results': result_tracks_top10,'results_count': result_tracks.count()})

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
        db_level = request.POST.get("dbLevel")
        background_track = BackgroundTrack()
        background_track.db_level = db_level
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
        db_level = request.POST.get("db_level")
        background_track = BackgroundTrack.objects.get(pk=track_id)
        background_track.db_level = int(db_level)
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

def frequency_tracks(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    frequency_tracks = FrequencyTrack.objects.all().order_by('-created_at')
    items_per_page = 10
    paginator = Paginator(frequency_tracks, items_per_page)
    items_page = []
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)    

    return render(request,'frequency_tracks.html', {'frequencies': items_page})

@csrf_exempt
def upload_frequency(request):
    if request.method == 'POST':
        track_name = request.POST.get("trackName")
        db_level = request.POST.get("dbLevel")
        frequency_track = FrequencyTrack()
        frequency_track.db_level = db_level
        frequency_track.name = track_name
        frequency_track.track_file.save(track_name+".mp3", request.FILES['file'], save=True)
        frequency_track.save()
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def frequency_track(request):
    if request.method == 'GET':
        track_id = request.GET.get("track_id")
        frequency_track = FrequencyTrack.objects.get(pk=track_id)
        serialized_object = serializers.serialize('json', [frequency_track,])
        return HttpResponse(serialized_object,content_type="application/json")
    elif request.method == 'POST':
        track_id = request.POST.get("track_id")
        track_name = request.POST.get("track_name")
        db_level = request.POST.get("db_level")
        frequency_track = FrequencyTrack.objects.get(pk=track_id)
        frequency_track.db_level = int(db_level)
        if track_name != frequency_track.name:
            track_file = frequency_track.track_file
            new_filename = text.slugify(track_name) + pathlib.Path(track_file.name).suffix
            new_file_path = os.path.join(settings.MEDIA_ROOT, FREQUENCY_UPLOAD_DIRECTORY+new_filename)
            os.rename(track_file.path, new_file_path)        
            frequency_track.track_file = new_file_path
            frequency_track.name = track_name
        frequency_track.save()
        return redirect('workspace:frequency_tracks')

@csrf_exempt    
def delete_frequency(request):
    if request.method == 'POST':
        track_id = request.POST.get("track_id")
        print(track_id)
        frequency_track = FrequencyTrack.objects.get(pk=track_id)
        frequency_track.track_file.delete(save=False)
        frequency_track.delete()
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
        background_track["db_level"] = result_track.background_track.db_level
        frequency_track = {}
        if result_track.frequency_track:
            frequency_track["name"] = result_track.frequency_track.name
            frequency_track["url"] = result_track.frequency_track.track_file.url
            frequency_track["db_level"] = result_track.frequency_track.db_level

        result_json = {}
        result_json["name"] = result_track.name
        result_json["pk"] = result_track.pk
        response = {}
        response["result"] = result_json
        response["voice"] = voice_track
        response["background"] = background_track
        response["frequency"] = frequency_track
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
def zip_result(request):
    voice_id = None
    if 'voice_id' in request.GET:
        voice_id = request.GET.get('voice_id')
    voice_track = VoiceTrack.objects.get(pk=voice_id)
    zip_name = voice_track.name + " Subliminals.zip"
    result_tracks = ResultTrack.objects.filter(voice_track__pk = voice_id).order_by('-created_at')
    if result_tracks.count() > 0:
        sio = io.BytesIO()
        zf = zipfile.ZipFile(sio, "w")

        for result_track in result_tracks:
            zf.write(result_track.track_file.path, result_track.name+".mp3")
        zf.close()
        response = HttpResponse(sio.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="'+zip_name+'"'
        return response

def insert_new_progress():
    progress_bar = ProgressBar()
    progress_bar.progress_val = 0
    progress_bar.is_running = False
    progress_bar.save()

def proceed(request):
    if request.method == 'GET':
        response={}
        progress_bar = ProgressBar.objects.first()
        if progress_bar == None:
            insert_new_progress()
            progress_bar = ProgressBar.objects.first()
        if progress_bar.is_running:
            response['status'] = 'failed'
            return HttpResponse(json.dumps(response),content_type="application/json")

        voice_track_id = request.GET['voice_track_id']
        background_track_ids_str = request.GET['background_track_ids']
        background_track_ids = background_track_ids_str.split(",")
        frequency_track_id = None
        if "frequency_track_id" in request.GET:
            frequency_track_id = request.GET['frequency_track_id']
            if frequency_track_id == "":
                frequency_track_id = None

        handle_proceed(voice_track_id, background_track_ids, frequency_track_id)
        response['status'] = 'success'
        return HttpResponse(json.dumps(response),content_type="application/json")

def handle_proceed(voice_track_id, background_track_ids, frequency_track_id):
    progress_bar = ProgressBar.objects.first()
    progress_bar.progress_val = 0
    progress_bar.is_running = True
    progress_bar.save()
    result_track_list = []
    voice_track = VoiceTrack.objects.get(pk=voice_track_id)
    frequency_track = None
    if frequency_track_id:
        frequency_track = FrequencyTrack.objects.get(pk=frequency_track_id)

    total_size = len(background_track_ids) * 3
    chunk_size = 1
    progress = 0

    for background_track_id in background_track_ids:
        voice = AudioSegment.from_mp3(voice_track.track_file.path)

        background_track = BackgroundTrack.objects.get(pk=background_track_id)
        volume_level = background_track.db_level
        background = AudioSegment.from_mp3(background_track.track_file.path)
        voice = voice + int(volume_level)

        progress += chunk_size
        percent = int(progress / total_size * 100)
        progress_bar.progress_val = percent
        progress_bar.save()

        background = background.overlay(voice)
        if frequency_track:
            voice = AudioSegment.from_mp3(frequency_track.track_file.path)
            voice = voice + int(frequency_track.db_level)
            background = background.overlay(voice)
        voice = None

        progress += chunk_size
        percent = int(progress / total_size * 100)
        progress_bar.progress_val = percent
        progress_bar.save()

        result_filename = voice_track.name + " [" + background_track.name +"]"
        result_filename = text.slugify(result_filename)
        result_file_path = os.path.join(settings.MEDIA_ROOT, RESULT_UPLOAD_DIRECTORY + result_filename + ".mp3")
        background.export(result_file_path, format='mp3')

        result_track = ResultTrack()
        result_track.voice_track = voice_track
        result_track.background_track = background_track
        result_track.frequency_track = frequency_track
        result_track.name = voice_track.name + " [" + background_track.name +"]"
        result_track.track_file = RESULT_UPLOAD_DIRECTORY + result_filename + ".mp3"
        result_track.save()
        result_track_list.append(result_track)

        progress += chunk_size
        percent = int(progress / total_size * 100)
        progress_bar.progress_val = percent
        progress_bar.save()

    progress_bar.progress_val = 100
    progress_bar.is_running = False
    progress_bar.save()

def get_progress(request):
    progress_val = 0
    is_running = False
    progress_bar = ProgressBar.objects.first()
    if progress_bar:
        progress_val = progress_bar.progress_val
        is_running = progress_bar.is_running

    response = {}
    response['percent'] = progress_val
    response['is_running'] = is_running
    return HttpResponse(json.dumps(response),content_type="application/json")

