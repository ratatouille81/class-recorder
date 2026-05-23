import speech_recognition as sr
from moviepy.editor import VideoFileClip
import os
from pydub import AudioSegment
import tempfile
from datetime import datetime

class TranscriptorVideo:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def extraer_audio(self, ruta_video):
        """Extrae el audio del video y lo guarda temporalmente"""
        try:
            video = VideoFileClip(ruta_video)
            # Crear archivo temporal para el audio
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            video.audio.write_audiofile(temp_audio.name)
            video.close()
            return temp_audio.name
        except Exception as e:
            raise Exception(f"Error al extraer audio: {str(e)}")

    def transcribir_audio(self, ruta_audio):
        """Transcribe el audio a texto usando Google Speech Recognition"""
        try:
            with sr.AudioFile(ruta_audio) as source:
                audio = self.recognizer.record(source)
                texto = self.recognizer.recognize_google(audio, language='es-ES')
                return texto
        except sr.UnknownValueError:
            return "No se pudo entender el audio"
        except sr.RequestError as e:
            return f"Error en la solicitud a Google Speech Recognition: {str(e)}"
        except Exception as e:
            return f"Error durante la transcripción: {str(e)}"

    def procesar_video(self, ruta_video):
        """Procesa el video completo y guarda la transcripción"""
        try:
            # Extraer audio
            ruta_audio = self.extraer_audio(ruta_video)
            
            # Transcribir audio
            texto = self.transcribir_audio(ruta_audio)
            
            # Crear archivo de texto con el mismo nombre base
            nombre_base = os.path.splitext(ruta_video)[0]
            ruta_texto = f"{nombre_base}_transcripcion.txt"
            
            with open(ruta_texto, 'w', encoding='utf-8') as archivo:
                archivo.write(texto)
            
            # Limpiar archivo temporal
            os.unlink(ruta_audio)
            
            return ruta_texto
            
        except Exception as e:
            raise Exception(f"Error en el procesamiento: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    transcriptor = TranscriptorVideo()
    try:
        ruta_video = "circuito_electronico.mp4"  # Nombre del archivo descargado
        ruta_texto = transcriptor.procesar_video(ruta_video)
        print(f"Transcripción guardada en: {ruta_texto}")
    except Exception as e:
        print(f"Error: {str(e)}")

indice_mezcla = 2  # Cambia este número por el índice correcto

r = sr.Recognizer()

with sr.Microphone(device_index=indice_mezcla) as source:
    print("Ajustando al ruido ambiente...")
    r.adjust_for_ambient_noise(source, duration=2)
    print("Escuchando el audio del sistema... (Presiona Ctrl+C para detener)")
    nombre_archivo = f"transcripcion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        while True:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                try:
                    texto = r.recognize_google(audio, language='es-ES')
                    print(texto)
                    archivo.write(texto + "\n")
                    archivo.flush()
                except sr.UnknownValueError:
                    print("No se entendió el audio.")
            except KeyboardInterrupt:
                print("\nTranscripción detenida.")
                break
            except Exception as e:
                print("Error:", e) 