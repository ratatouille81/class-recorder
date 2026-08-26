# PRD: Módulo de Tutoría de Inglés (M101 Class Recorder)

## 1. Problema y Contexto
El sistema actual está optimizado para clases técnicas unidireccionales (ej. Platzi) extrayendo código y resúmenes mediante un motor local. Surge la necesidad de crear un **Centro de Conocimiento Reforzado** para clases particulares de inglés (1-a-1). Esto requiere diarización precisa (identificar Tutor vs Estudiante), comprensión profunda de matices lingüísticos (gramática, idioms, corrección de pronunciación) y una **memoria longitudinal** para evaluar el progreso a lo largo de las sesiones.

## 2. Alcance (In Scope)
*   **Motor Principal:** Arquitectura 100% Cloud utilizando **Gemini (Google GenAI)** para procesamiento multimodal nativo (Audio + Video sincronizados).
*   **Análisis Multimodal:**
    *   Diarización (identificación automática de quién habla).
    *   Extracción de contenido de la pizarra (gramática, estructuras, vocabulario).
*   **Generación de Artefactos de Estudio:**
    *   Documento Markdown estructurado con correcciones y temario.
    *   Archivo CSV formateado para importar directamente a **Anki / Quizlet** (Flashcards).
*   **Memoria Longitudinal:** Sistema de caché o perfil de estado (`student_profile.json`) que acumula las debilidades y fortalezas de clases anteriores para generar repaso cruzado.

## 3. No-Alcance (Out of Scope)
*   Procesamiento 100% local (Local LLM/Whisper) para este módulo específico.
*   Interfaz de chat interactiva en tiempo real (el output se centra en artefactos estáticos generados post-clase).

## 4. Requisitos Funcionales
1.  **Ingesta Segura:** Subida automática del archivo `.mp4`/`.mkv` a la API de Google (`Google Files API`).
2.  **Prompting Estructurado:** Prompt maestro que instruya al modelo a actuar como un evaluador lingüístico, prestando atención a: *Phrasal verbs*, errores de conjugación, *speaking ratio* (quién habló más) y temas gramaticales visuales.
3.  **Persistencia del Perfil:** El sistema debe inyectar el resumen de la clase actual al "Perfil del Estudiante" para usarlo de contexto en la siguiente clase.
4.  **Generación de Archivos:** Outputs separados limpios (`resumen_N.md` y `flashcards_N.csv`).

## 5. Requisitos No-Funcionales (Concurrencia, Observabilidad y Carga)
*   **Eficiencia de Host:** Consumo de GPU local igual a 0%. Consumo de RAM mínimo.
*   **Telemetría y Control de Costos:** El script debe loguear (en `watcher.log` o un nuevo log) el **conteo de tokens** consumidos (Input/Output) tras cada ejecución para llevar un control estricto de la facturación mensual.
*   **Resiliencia de Red:** Manejo de excepciones durante la subida de archivos pesados (retries en caso de desconexión).

## 6. Modelo de Datos (Alto Nivel)
*   `Input`: Ruta local del archivo de video.
*   `Student State`: `perfil_estudiante.json` (Contiene historial de temas vistos y errores comunes).
*   `API Payload`: Video Reference (Google URI) + System Prompt + Student State.
*   `Output Files`: 
    *   `docs/clases_ingles/clase_YYYYMMDD.md`
    *   `docs/clases_ingles/decks/clase_YYYYMMDD.csv`

## 7. Riesgos Detectados
*   **Cuello de botella de red (Upload):** Si el video de 1 hora pesa más de 500MB y el ancho de banda local es bajo, la ejecución del script puede tardar mucho solo en la fase de subida.
*   **Costos imprevistos:** Si no se limpia correctamente el contexto o no se aplican técnicas de *Context Caching*, el costo mensual de $11 USD podría elevarse.

## 7. Decisiones de Arquitectura Aprobadas (CEO)
*   **Activación (Routing Automático):** El `watcher_asus.py` será modificado para enrutar inteligentemente los videos. Detectará si el archivo proviene de Google Meet (por nomenclatura del archivo o ruta) y lo enviará al **Motor Cloud (Módulo Inglés)**. Si es un video estándar de Platzi, lo enviará al **Motor Local**.
*   **Purga y Almacenamiento:** Aunque la privacidad no es crítica, se implementará una rutina de limpieza (DELETE) inmediata en el script de ingesta (o un job recurrente) para purgar la Google Files API después de la generación de artefactos, manteniendo la cuota de almacenamiento limpia.

*(Fase Discovery completada y aprobada por el CEO)*
