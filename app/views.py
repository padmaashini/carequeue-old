from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import pygame
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
import io


def home(request):
    return HttpResponse("Welcome to CareQueue API")

def audio_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text

@csrf_exempt
@require_http_methods(["POST"])
def parse_audio(request):
    print(request.FILES)
    if 'audio' in request.FILES:
        audio_file = request.FILES['audio']
        print('audio', audio_file)

        audio = AudioSegment.from_file_using_temporary_files(io.BytesIO(audio_file.read()))
        audio = audio.set_frame_rate(44100).set_channels(1)  # Ensure compatibility
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio.export(temp_path.name, format='wav')

        # Process the converted audio file for speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path.name) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return JsonResponse({'error': 'Speech Recognition could not understand audio'}, status=400)
            except sr.RequestError as e:
                return JsonResponse({'error': 'Could not request results from Speech Recognition service; {0}'.format(e)}, status=500)

        # Delete the temporary file
        temp_path.close()

        # Return the converted text
        return JsonResponse({'message': 'Audio processed', 'text': text})
        # # old 
        #  # Use tempfile to create a temporary file
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', mode='wb+') as destination:
        #     for chunk in audio_file.chunks():
        #         destination.write(chunk)
        
        # file_path = destination.name  # Get the path of the saved file
        # print(file_path)

        # recognizer = sr.Recognizer()
        # with sr.AudioFile(audio_file) as source:
        #     audio_data = recognizer.record(source)
        #     try:
        #         text = recognizer.recognize_google(audio_data)
        #     except sr.UnknownValueError:
        #         return JsonResponse({'error': 'Speech Recognition could not understand audio'}, status=400)
        #     except sr.RequestError as e:
        #         return JsonResponse({'error': 'Could not request results from Speech Recognition service; {0}'.format(e)}, status=500)
        # # # Play the audio
        # # try:
        # #     pygame.mixer.init()
        # #     pygame.mixer.music.load(file_path)
        # #     pygame.mixer.music.play()
        # #     while pygame.mixer.music.get_busy(): 
        # #         pygame.time.Clock().tick(10)
        # # except Exception as e:
        # #     return JsonResponse({'error': 'Failed to play audio', 'details': str(e)}, status=500)

        # return JsonResponse({'message': 'Audio processed', 'text': text})
    else:
        return JsonResponse({'error': 'No audio file provided'}, status=400)
    # data = request.POST.get('text', '')
    # print('data', data)
    # return JsonResponse({'message': 'Audio Received', 'data': data})
