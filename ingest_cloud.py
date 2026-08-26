import os
import sys
import json
import time
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Cargar API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY no encontrada en el archivo .env")
    sys.exit(1)

# Inicializar cliente de la nueva SDK google-genai
client = genai.Client(api_key=api_key)

def procesar_clase(video_path, subject_name):
    print(f"☁️ [Cloud Engine] Ingestando clase: {os.path.basename(video_path)} | Tema: {subject_name}")
    video_dir = os.path.dirname(video_path)
    
    # Archivos de salida
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    markdown_path = os.path.join(video_dir, f"Resumen_{timestamp}.md")
    deck_path = os.path.join(video_dir, f"Flashcards_{timestamp}.csv")
    profile_path = os.path.join(video_dir, "student_profile.json")

    # Leer memoria longitudinal
    student_profile = "Sin historial previo."
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            student_profile = f.read()

    uploaded_file = None
    try:
        # 1. Subida Segura
        print(f"☁️ Subiendo a Google Cloud (Files API)...")
        uploaded_file = client.files.upload(file=video_path)
        print(f"☁️ Archivo subido: {uploaded_file.name}. Esperando procesamiento...")
        
        # Esperar a que el video sea procesado por Google
        while True:
            file_info = client.files.get(name=uploaded_file.name)
            if file_info.state == "ACTIVE":
                break
            elif file_info.state == "FAILED":
                raise Exception("Fallo en el procesamiento del video en la nube.")
            time.sleep(5)
            
        print("☁️ Procesamiento de video en la nube listo. Iniciando análisis Gemini...")

        # 2. Prompting Dinámico
        if "ingle" in subject_name.lower() or "english" in subject_name.lower():
            system_instruction = """Eres un Tutor de Inglés evaluador de nivel nativo. 
            Analiza el video (que contiene una pizarra) y el audio (diarizando entre 'Tutor' y 'Estudiante').
            Devuelve tu respuesta EXACTAMENTE en este formato JSON, sin markdown extra alrededor:
            {
              "markdown_resumen": "# Resumen de Clase... (incluye correcciones gramaticales, ratio de habla, temas de pizarra)",
              "csv_flashcards": "front,back\\nword,definition",
              "perfil_actualizado": "Resumen conciso del nivel actual del estudiante, errores recurrentes y temas a mejorar."
            }"""
        else:
            system_instruction = f"""Eres el 'M101 Incremental Mentor', un experto técnico en {subject_name}.
            Analiza la clase en video, extrayendo explicaciones teóricas, código en pantalla y la explicación del profesor.
            Devuelve tu respuesta EXACTAMENTE en este formato JSON, sin markdown extra alrededor:
            {
              "markdown_resumen": "# Resumen Técnico... (incluye Lo aprendido hoy, Conceptos Clave, Práctica M101, Glosario)",
              "csv_flashcards": "front,back\\nconcepto,explicación",
              "perfil_actualizado": "Resumen conciso del progreso del estudiante en esta materia y conceptos que requieren refuerzo."
            }"""
        
        prompt = f"Analiza esta clase. Historial del estudiante (Memoria Longitudinal): {student_profile}"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        # 3. Guardado de Archivos
        data = json.loads(response.text)
        
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(data.get("markdown_resumen", ""))
        
        with open(deck_path, "w", encoding="utf-8") as f:
            f.write(data.get("csv_flashcards", ""))
            
        with open(profile_path, "w", encoding="utf-8") as f:
            f.write(data.get("perfil_actualizado", ""))
            
        print(f"✅ Artefactos generados correctamente en {video_dir}")
        print(f"📊 Tokens usados: Input {response.usage_metadata.prompt_token_count} | Output {response.usage_metadata.candidates_token_count}")
        
        # Opción 2 del CEO: Trituradora local de videos
        print(f"🗑️ Eliminando video original del disco local para liberar espacio...")
        try:
            os.remove(video_path)
            print("🗑️ Video local eliminado con éxito.")
        except Exception as e:
            print(f"⚠️ No se pudo borrar el video local: {e}")
        
    except Exception as e:
        print(f"❌ Error en Cloud Engine: {e}")
        
    finally:
        # 4. RUTINA DE PURGA ESTRICTA (Independientemente de si hubo error)
        if uploaded_file:
            print("🧹 Purgando archivo de Google Cloud por seguridad...")
            try:
                client.files.delete(name=uploaded_file.name)
                print("🧹 Purga exitosa.")
            except Exception as e:
                print(f"⚠️ Error al purgar el archivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python ingest_cloud.py <ruta_del_video> <subject_name>")
        sys.exit(1)
    procesar_clase(sys.argv[1], sys.argv[2])
