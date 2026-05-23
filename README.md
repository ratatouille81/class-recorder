# 🎙️ M101 Class Recorder & Ingestor

Un sistema avanzado y modular de ingesta, transcripción y resumen técnico de clases universitarias y reuniones de estudio. El proyecto opera con un esquema **híbrido y redundante** que permite procesar videos tanto de forma 100% local (sin conexión a Internet) como en la nube (con modelos avanzados de Gemini), guardando directamente las guías de estudio estructuradas en formato Markdown en un disco extraíble (`D:\memoriam101`).

---

## 🏗️ Arquitectura del Sistema

El proyecto consta de dos motores principales de ingesta técnica de clases:

### 1. Motor Local Inalámbrico (`watcher_asus.py`)
Diseñado para operar de manera completamente autónoma y local (offline) aprovechando la aceleración por hardware de la GPU dedicada.
- **Transcripción de Audio:** Utiliza `faster-whisper` (modelo `small`) acelerado por GPU (NVIDIA RTX 4050 con CUDA) para transcribir el audio en tiempo real con precisión. Incluye soporte de inicialización fonética para corregir acrónimos técnicos (ej. "Cujis" -> "QGIS").
- **Análisis de Video (Frame Extraction):** Emplea OpenCV para extraer fotogramas clave de la clase de manera proporcional al tiempo total del video.
- **Reconocimiento Visual (OCR):** Procesa los fotogramas mediante el modelo de visión local `moondream` a través de **Ollama** para detectar código en pantalla, menús de software y diagramas.
- **Generador de Resúmenes:** Utiliza el modelo local `llama3.2:3b` vía Ollama para estructurar e integrar el audio y el contexto visual en una guía de estudio interactiva con glosarios y retos evolutivos prácticos.
- **Monitoreo Inteligente:** Cuenta con detección de estabilidad de tamaño de archivos para evitar procesar videos mientras están siendo copiados o descargados en el disco extraíble.

### 2. Motor Cloud de Alta Fidelidad (`ingest-clase.py`)
Un pipeline complementario diseñado para cuando se dispone de conexión a Internet y se requiere un nivel superior de detalle analítico en el video.
- **Procesamiento de Video Nativo:** Sube el archivo directamente a la **Google Files API** de forma segura.
- **Inferencia Avanzada:** Emplea el modelo multimodal `gemini-flash-latest` (a través del SDK oficial de Google GenAI) para analizar simultáneamente audio, código, gestos y diapositivas.
- **Carga de Credenciales Segura:** Cuenta con un cargador manual de archivos `.env` resistente a ejecuciones no interactivas en segundo plano dentro de WSL.

---

## 📁 Estructura del Repositorio

- `watcher_asus.py`: Script de monitoreo automatizado local para carpetas en el disco extraíble.
- `ingest-clase.py`: Script manual para ingesta de alta fidelidad asistida por Gemini Cloud.
- `transcriptor_tiempo_real.py`: Herramienta de transcripción y extracción de audio para videos individuales con Google Speech API.
- `resumen.py`: Utilidad de grabación y transcripción directa de audio del sistema (mezcla estéreo).
- `.gitignore`: Excluye de forma automática archivos de configuración privada (`.env`) y temporales.
- `README.md`: Documentación técnica del proyecto.

---

## 🛠️ Requisitos e Instalación

### Requisitos del Sistema
- **SO:** Windows con WSL 2 (Ubuntu 22.04+).
- **GPU:** NVIDIA compatible con CUDA 11.8+ (RTX 4050 recomendado).
- **Plataforma LLM:** Ollama (instalado en WSL) con los modelos `moondream` y `llama3.2:3b`.

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
