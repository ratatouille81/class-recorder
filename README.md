# 🎙️ M101 Class Recorder & Ingestor (PURE CLOUD v18)

Un sistema avanzado de ingesta, transcripción y resumen técnico de clases universitarias y reuniones de estudio (Platzi e Inglés). El proyecto opera con una arquitectura **100% Cloud** utilizando Gemini (Google GenAI) para procesar archivos de video sin consumir recursos locales.

---

## 🏗️ Arquitectura del Sistema

### Motor Cloud Universal (`ingest_cloud.py` & `watcher_asus.py`)
Diseñado para operar de manera autónoma ruteando videos hacia la nube según la carpeta de origen.
- **Procesamiento Multimodal Nativo:** Utiliza la API nativa de Google GenAI (`gemini-2.5-flash`) para transcribir audio, realizar diarización (separar hablantes) y analizar video (pizarra, código, esquemas) en una sola pasada.
- **Ruteo Inteligente:** `watcher_asus.py` monitorea los directorios. Si la carpeta indica que es una clase de inglés, usa un prompt evaluativo. De lo contrario, actúa como mentor técnico.
- **Memoria Longitudinal:** Utiliza `student_profile.json` para mantener el contexto del progreso en diferentes clases.
- **Purga Automática:** Limpia de forma estricta (DELETE) los videos en la Google Files API inmediatamente después de usarlos para maximizar privacidad y liberar cuota.

---

## 📁 Estructura del Repositorio

- `watcher_asus.py`: Script de monitoreo automatizado local para carpetas en el disco extraíble. (Router)
- `ingest_cloud.py`: Script de ingesta multimodal Gemini GenAI (Soporte para múltiples materias e Inglés).
- `.gitignore`: Excluye de forma automática archivos de configuración privada (`.env`) y temporales.
- `README.md`: Documentación técnica del proyecto.

---

## 🛠️ Requisitos e Instalación

### Requisitos del Sistema
- **SO:** Windows con WSL 2 (Ubuntu 22.04+) o Linux nativo.
- **Clave API:** Google Gemini API Key.

### Instalación de Dependencias en WSL
1. Clona el repositorio dentro de tu directorio de usuario en WSL:
   ```bash
   git clone git@github.com:ratatouille81/class-recorder.git ~/class-recorder
   cd ~/class-recorder
   ```
2. Crea el entorno virtual de Python e instala las dependencias:
   ```bash
   python3 -m venv venv-ingest
   source venv-ingest/bin/activate
   pip install --upgrade pip
   pip install faster-whisper opencv-python google-genai requests pydub speechrecognition
   ```
3. Asegúrate de tener los modelos descargados en Ollama:
   ```bash
   ollama pull moondream
   ollama pull llama3.2:3b
   ```

---

## ⚙️ Guía de Uso

### 1. Ejecutar el Watcher Local (Monitoreo Continuo)
Para ejecutar de forma directa el monitor de carpetas:
```bash
./venv-ingest/bin/python watcher_asus.py
```
Para dejarlo corriendo de forma permanente en segundo plano y guardar los registros en un archivo log:
```bash
nohup ./venv-ingest/bin/python watcher_asus.py > watcher.log 2>&1 &
```

### 2. Procesar una Clase en la Nube con Gemini
Crea un archivo `.env` en la raíz del proyecto con tu clave de API de Google:
```env
GEMINI_API_KEY="tu_clave_de_api_aqui"
```
Luego ejecuta el script pasando la ruta absoluta del video:
```bash
./venv-ingest/bin/python ingest-clase.py "/mnt/d/memoriam101/Curso/clase_01.mp4"
```

---

## 📝 Contribuciones y Buenas Prácticas
1. **Seguridad:** Nunca subas el archivo `.env` al repositorio. Se encuentra protegido por defecto en `.gitignore`.
2. **Estabilidad:** Si añades soporte para nuevos formatos de video, asegúrate de actualizar la tupla de extensiones en `watcher_asus.py` (`.endswith((".mkv", ".mp4"))`).
