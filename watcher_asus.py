import os
import time
import cv2
import base64
import requests
from faster_whisper import WhisperModel
from datetime import datetime

# CONFIGURACIÓN M101 - ASUS (v16 INCREMENTAL MENTOR)
WATCH_DIR = "/mnt/d/memoriam101"
LOG_FILE = os.path.join(WATCH_DIR, "procesados.log")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_VISION = "moondream"
MODEL_LLM = "llama3.2:3b"

print("🚀 Iniciando M101 Mentor Evolutivo v16...")
whisper_model = WhisperModel("small", device="cuda", compute_type="float16")

def extract_frames(video_path, count=6):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = total_frames // (count + 1)
    frames_b64 = []
    for i in range(1, count + 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (1280, 720))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frames_b64.append(base64.b64encode(buffer).decode('utf-8'))
    cap.release()
    return frames_b64

def ask_vision(image_b64):
    prompt = "Technical OCR: Describe menus, software names, and any visible code or maps."
    try:
        res = requests.post(OLLAMA_URL, json={"model": MODEL_VISION, "prompt": prompt, "images": [image_b64], "stream": False})
        return res.json().get("response", "")
    except: return ""
def wait_for_file_stability(file_path, wait_seconds=3, timeout=600):
    """Espera hasta que el archivo esté completamente escrito (su tamaño no cambie)"""
    print(f"⏳ Verificando estabilidad del archivo: {os.path.basename(file_path)}")
    last_size = -1
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_size = os.path.getsize(file_path)
        except OSError:
            current_size = -1
        
        if current_size == last_size and current_size > 0:
            print(f"✅ Archivo listo y estable. Tamaño: {current_size} bytes.")
            return True
        
        last_size = current_size
        time.sleep(wait_seconds)
    print(f"⚠️ Tiempo de espera agotado esperando estabilidad de {file_path}")
    return False

def procesar_video_v16(path):
    print(f"🎬 Ingesta Mentor v16: {os.path.basename(path)}")
    # Detectamos la carpeta actual del video
    video_dir = os.path.dirname(path)
    subject_name = os.path.relpath(video_dir, WATCH_DIR).replace(os.sep, "_")
    if subject_name == ".": subject_name = "General"
    
    # El archivo se guarda DENTRO de la carpeta donde está el video
    master_file_path = os.path.join(video_dir, f"Master_{subject_name}.md")

    try:
        # Contexto dinámico para Whisper basado en el nombre de la carpeta
        segments, info = whisper_model.transcribe(
            path, 
            language=None, 
            initial_prompt=f"Esta es una clase sobre {subject_name}. Términos técnicos relacionados con {subject_name}."
        )
        audio_text = " ".join([segment.text for segment in segments])
        
        frames = extract_frames(path, count=5)
        visual_context = "\n".join([f"- Captura {i+1}: {ask_vision(img)}" for i, img in enumerate(frames)])

        final_prompt = f"""[SYSTEM] 
        Eres el 'M101 Incremental Mentor'. Tu misión es crear una guía de estudio técnica.
        CONTEXTO DE LA MATERIA: {subject_name}
        
        [REGLAS CRÍTICAS]
        - Céntrate exclusivamente en los temas hablados en el audio y vistos en pantalla.
        - Usa el nombre de la materia '{subject_name}' para guiar el tono técnico.
        - PROHIBIDO inventar contextos de otras materias (ej. no hables de mapas si la materia es programación).
        - Genera un título descriptivo real basado en el contenido.
        - Fidelidad total al audio procesado.
        
        [DATOS DE ENTRADA]
        AUDIO DE LA CLASE: {audio_text}
        VISIÓN DE PANTALLA: {visual_context}
        
        [ESTRUCTURA DE SALIDA]
        ### [Título descriptivo]

        **Lo aprendido hoy:**
        (Resumen detallado de la clase)

        **Conceptos Clave (Nivel Pro):**
        (Explicación técnica de 2 funciones avanzadas)

        **Práctica M101 (Reto del día):**
        (Un ejercicio práctico relacionado)

        **Glosario Técnico:**
        (Definiciones de términos detectados)
        """

        res = requests.post(OLLAMA_URL, json={"model": MODEL_LLM, "prompt": final_prompt, "stream": False})
        final_markdown = res.json().get("response", "")

        with open(master_file_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- \n*Clase M101 v16 ({info.language}): {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
            f.write(final_markdown)
        
        with open(LOG_FILE, "a") as log: log.write(f"{path}\n")
        print(f"✅ Guía evolutiva lista.")

    except Exception as e:
        print(f"❌ Error v16: {e}")

if __name__ == "__main__":
    print(f"👀 M101 Watcher v16 (INCREMENTAL) activo...")
    while True:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f: procesados = f.read().splitlines()
        else: procesados = []
        for root, dirs, files in os.walk(WATCH_DIR):
            for file in files:
                if file.endswith((".mkv", ".mp4")):
                    full_path = os.path.join(root, file)
                    if full_path not in procesados:
                        if wait_for_file_stability(full_path):
                            procesar_video_v16(full_path)
        time.sleep(20)
