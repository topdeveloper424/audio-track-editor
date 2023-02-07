from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, FileResponse
import json, os
from datetime import datetime
from pydub import AudioSegment

VOICE_UPLOAD_DIRECTORY = "uploads/voices"
BACKGROUND_UPLOAD_DIRECTORY = "uploads/backgrounds"
RESULT_UPLOAD_DIRECTORY = "uploads/results"

# Create your views here.
def home(request):
    voice_list =os.listdir(VOICE_UPLOAD_DIRECTORY)
    background_list = os.listdir(BACKGROUND_UPLOAD_DIRECTORY)
    result_list = os.listdir(RESULT_UPLOAD_DIRECTORY)
    return render(request,'home.html', {'voices': voice_list, 'backgrounds':background_list, 'results': result_list})

@csrf_exempt    
def upload_voice(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'], True)
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def upload_background(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'], False)
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

@csrf_exempt    
def proceed(request):
    if request.method == 'POST':
        volume_level = request.POST['level']
        handle_proceed(volume_level)
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

def handle_uploaded_file(f, is_voice):
    file_name = ""
    if is_voice:
        file_name = VOICE_UPLOAD_DIRECTORY + "/"+os.path.splitext(f.name)[0]+"_"
    else:
        file_name = BACKGROUND_UPLOAD_DIRECTORY + "/"+os.path.splitext(f.name)[0]+"_"
    timestr = datetime.now().strftime("%Y%m%d%H%M%S%f")
    file_name = file_name + timestr + ".mp3"
    with open(file_name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def handle_proceed(volume_level):
    voice_list =os.listdir(VOICE_UPLOAD_DIRECTORY)
    background_list = os.listdir(BACKGROUND_UPLOAD_DIRECTORY)
    generated_list = []
    for voice_track in voice_list:
        voice_file_path = os.path.join(VOICE_UPLOAD_DIRECTORY, voice_track)
        # read voice and increase volume by level db
        voice = AudioSegment.from_mp3(voice_file_path)
        louder_song = voice + int(volume_level)

        for background_track in background_list:
            background = AudioSegment.from_mp3(os.path.join(BACKGROUND_UPLOAD_DIRECTORY, background_track))
            generated = background.overlay(louder_song)
            pos = voice_track.rfind("_")
            voice_file_name = voice_track[:pos]
            pos = background_track.rfind("_")
            background_file_name = background_track[:pos]
            new_file_name = os.path.join(RESULT_UPLOAD_DIRECTORY, voice_file_name+"_"+background_file_name+"_"+datetime.now().strftime("%Y%m%d%H%M%S")+".mp3")
            generated.export(new_file_name, format='mp3')
            generated_list.append(new_file_name)
    print(generated_list)
    remove_old_files()
    response={}
    response['status'] = 'success'
    return HttpResponse(json.dumps(response),content_type="application/json")

def download_result(request):
    file_path = os.path.join(RESULT_UPLOAD_DIRECTORY, request.GET['filename'])
    if os.path.exists(file_path):
        fh = open(file_path, 'rb')
        return FileResponse(fh, as_attachment=True)
    raise Http404

def remove_old_files():
    voice_list =os.listdir(VOICE_UPLOAD_DIRECTORY)
    background_list = os.listdir(BACKGROUND_UPLOAD_DIRECTORY)
    for voice_track in voice_list:
        voice_file_path = os.path.join(VOICE_UPLOAD_DIRECTORY, voice_track)
        os.remove(voice_file_path)

    for background_track in background_list:
        background_file_path = os.path.join(BACKGROUND_UPLOAD_DIRECTORY, background_track)
        os.remove(background_file_path)

