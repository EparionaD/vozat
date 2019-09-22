from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Radio, ProgramasRadiales

import time
import vlc
import sys
import os
import io
import threading
import fnmatch
import collections

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/home/eparionad/Dropbox/Tesis/CredencialesApiGoogle/Tesis-59cc7659afbc.json'

def inicio(request):
    return HttpResponse("Inicio")


#datos = ProgramasRadiales.objects.all().values()

def obtener_nombre_programa(codigo):

    datos = ProgramasRadiales.objects.filter(id=codigo).values()

    #lista = []

    for dat in datos:
        c = dat.get('nombre')
        nombre_programa = c.replace(' ', '')
        h = dat.get('inicio')
        hora = h.strftime('%H:%M')
        fecha_programa = time.strftime('%d-%m-%y')
        completo = str(codigo)+'-'+nombre_programa+'-'+fecha_programa+'-'+hora
        #lista += [completo]

    return completo

#print(obtener_nombre_programa())

def obtener_tiempo_programa(codigo):

    datos = ProgramasRadiales.objects.filter(id=codigo).values()
    #lista = []

    for dat in datos:
        c = dat.get('duracion')
        #lista += [c]

    return c

#print(obtener_tiempo_programa())

def obtener_web_programa(codigo):

    url = ProgramasRadiales.objects.filter(id=codigo).values('radios__web')

    #lista = []

    for dat in url:
        c = dat.get('radios__web')
        #lista += [c]

    return c

#print(obtener_web_programa())

def grabar_audio(carpeta, nombre, stream, tiempo):

    convertidor = "--sout=#transcode{acodec=flac,ab=320,channels=1,samplerate=16000}:std{access=file,mux=raw,dst='%s/%s.flac'} --run-time=%s --stop-time=%s" % (carpeta, nombre, tiempo, tiempo)
    instancia = vlc.Instance(convertidor)
    reproductor = instancia.media_player_new()
    medios = instancia.media_new(stream)
    medios.get_mrl()
    reproductor.set_media(medios)
    reproductor.play()
    time.sleep(tiempo)

def crear_carpetas(nombre):
    
    #dia = time.gmtime()
    dia = time.localtime()
    fecha = time.strftime('%d-%m-%Y', dia)
    carpeta = '/home/eparionad/Descargas/%s' % os.path.join(fecha, nombre)

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    return carpeta


def programa_principal():

    datos1 = ProgramasRadiales.objects.all()


    #dia = time.gmtime()
    dia = time.localtime()

    dia_actual = dia.tm_wday

    hora = time.strftime('%H:%M')

    for dato in datos1:
        hora_pro = (dato.inicio).strftime('%H:%M')

        if hora_pro == hora:
            for x in dato.dias:
                if str(dia_actual) == str(x):

                    codigo = dato.id
                    nc = dato.nombre
                    nombre_carpeta = nc.replace(' ', '')
                    nombre_archivo = obtener_nombre_programa(codigo)
                    url = obtener_web_programa(codigo)
                    inicio_pro = obtener_tiempo_programa(codigo)
                    duracion_total = inicio_pro * 60
                    carpeta = crear_carpetas(nombre_carpeta)
                    audio = threading.Thread(target=grabar_audio, args=(carpeta, nombre_archivo, url, duracion_total))
                    audio.start()
                    print(nombre_archivo)
                    print(url)
                    print(inicio_pro)
                    print(nombre_carpeta)
                else:
                    print('No hace nada')

        else:
            print('No es el momento')

    print(hora)

#print(programa_principal())
programa_principal()

def transcribe_file():
        #Transcribe the given audio file asynchronously.
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    #speech_file = 'gs://audiosparareconocimiento/1-Tusnoticias-09-03-18-08:51.flac'
    gcs_uri = 'gs://audiosparareconocimiento/1-Tusnoticias-09-03-18-08:51.flac'

    # [START migration_async_request]
    """with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()"""

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code='es-PE')

    """audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code='es-PE')"""

    # [START migration_async_response]
    operation = client.long_running_recognize(config, audio)
    # [END migration_async_request]

    print('Waiting for operation to complete...')
    response = operation.result(timeout=900)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        with open('/home/eparionad/Descargas/audio.txt', 'a') as f:
            f.write(result.alternatives[0].transcript)
        #print('Transcript: {}'.format(result.alternatives[0].transcript))
    # [END migration_async_response]
# [END def_transcribe_file]

def contar_palabras():

    palabras_filtradas = []

    with open('/home/eparionad/Descargas/texto/audio.txt') as archivo:
        texto = archivo.read()
        palabras = texto.split()

        for palabra in palabras:
            #sin_tilde = ''.join((c for c in unicodedata.normalize('NFD',palabra) if unicodedata.category(c) != 'Mn'))
            palabras_filtradas += [palabra.lower()]

        contar = collections.Counter(palabras_filtradas)
        borrar = ['como','supo','casi','esta','cómo','todo','toda','cual','cuál','este','esta','esto','tanto','alla','allá',
        'caso','todos','todas','estos','pero','sabes','hizo','hace','hacer','sino','paso','pasó','solo','sólo','para','porque',
        'tiene','está','pues','algo','desde','también','tienen','debe','tener','aqui','aquí','sera','será','buen']

        for clave in list(contar.keys()):
            if clave in borrar or len(clave) < 4:
                del contar[clave]

    with open('/home/eparionad/Descargas/texto/palabras.csv', 'a') as csv:
        csv.write('Palabras,Cantidad\n')

        for palabra, cantidad in contar.items():
            csv.write('%s,%s\n' % (palabra,cantidad))

    print(contar)

print(contar_palabras())


def enviar_audio():

    datos =  ProgramasRadiales.objects.all()

    ruta_parcial = '/home/eparionad/Descargas'
    #tiempo = time.gmtime()
    tiempo = time.localtime()
    fecha = time.strftime('%d-%m-%Y', tiempo)

    for dato in datos:
        nc = dato.nombre
        programa = nc.replace(' ', '')

        ruta_total = os.path.join(ruta_parcial, '09-03-2018', programa)

        for carpetas in os.walk(ruta_total):
            for carpeta in carpetas:
                for archivos in carpeta:
                    if fnmatch.fnmatch(archivos, '*.flac'):
                        nombre = archivos.replace('flac', 'txt')
                        #print(nombre)
                        if not os.path.exists(os.path.join(ruta_total,nombre)):
                            #audio_grabado = transcribe_file()
                            print('LLamo a la funcion')

                        else:
                            print('No hago nada')

        #print(ruta_total)

print(enviar_audio())