import speech_recognition as sr
from datetime import datetime

def detectar_idioma(audio, recognizer):
    idiomas = ['es-ES', 'en-US']
    resultados = {}
    for idioma in idiomas:
        try:
            texto = recognizer.recognize_google(audio, language=idioma)
            resultados[idioma] = texto
        except sr.UnknownValueError:
            resultados[idioma] = ""
        except sr.RequestError:
            resultados[idioma] = ""
    idioma_elegido = max(resultados, key=lambda k: len(resultados[k]))
    return resultados[idioma_elegido], idioma_elegido

if __name__ == "__main__":
    indice_fuente = 2  # Mezcla estéreo (Realtek(R) Audio)

    r = sr.Recognizer()
    with sr.Microphone(device_index=indice_fuente) as source:
        print("🔧 Ajustando al ruido ambiente...")
        r.adjust_for_ambient_noise(source, duration=2)
        print("🎧 Escuchando el audio del sistema... (Presiona Ctrl+C para detener)")

        nombre_archivo = f"transcripcion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            while True:
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                    try:
                        texto, idioma = detectar_idioma(audio, r)
                        print(f"[{idioma}] {texto}")
                        archivo.write(f"[{idioma}] {texto}\n")
                        archivo.flush()
                    except sr.UnknownValueError:
                        print("🤔 No se entendió el audio.")
                except KeyboardInterrupt:
                    print("\n🛑 Transcripción detenida por el usuario.")
                    break
                except Exception as e:
                    print("⚠️ Error:", e)
