import os
import sys
import time
import subprocess
from datetime import datetime

# CONFIGURACIÓN M101 - CLOUD WATCHER (v18 100% NUBE)
WATCH_DIR = "/mnt/d/memoriam101"
LOG_FILE = os.path.join(WATCH_DIR, "procesados.log")

print("🚀 Iniciando M101 Cloud Watcher v18...")

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

if __name__ == "__main__":
    print(f"👀 M101 Watcher v18 (PURE CLOUD) activo...")
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
                            # EXTRAER SUBJECT NAME
                            folder_name = os.path.relpath(root, WATCH_DIR).replace(os.sep, "_")
                            if folder_name == ".": folder_name = "General"
                            
                            print(f"🔀 [Router] Derivando {file} a Motor Cloud (Materia: {folder_name})...")
                            try:
                                python_exe = sys.executable if 'sys' in dir() else "python3" 
                                subprocess.run([python_exe, "ingest_cloud.py", full_path, folder_name], check=True)
                                with open(LOG_FILE, "a") as log: log.write(f"{full_path}\n")
                            except subprocess.CalledProcessError as e:
                                print(f"❌ Fallo en el Motor Cloud: {e}")
        time.sleep(20)
