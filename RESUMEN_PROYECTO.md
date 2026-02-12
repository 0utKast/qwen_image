# Resumen de Proyecto: Qwen Studio Editor 🎨💻

Este documento detalla la arquitectura, las tecnologías y las decisiones de diseño tomadas para la creación de **Qwen Studio Editor**, una suite creativa multimodal ejecutada íntegramente de forma local en macOS.

## 1. El Concepto: "Qwen Studio Editor"
La aplicación nace como un entorno de trabajo local que permite al usuario interactuar con la inteligencia artificial generativa y visual sin depender de la nube. Está diseñada para ser un puente entre la **creación visual** (generación/edición) y la **comprensión visual** (análisis/VLM).

## 2. Tecnologías y Motores de IA
El proyecto utiliza un sistema de **motor dual** optimizado para **MLX** (el framework de aprendizaje automático de Apple):

*   **Motor de Generación y Edición (FLUX.1-schnell)**: Debido a que los pesos oficiales de *Qwen-Image 2.0* no han sido liberados públicamente por Alibaba aún, hemos integrado **FLUX.1-schnell** (vía `mflux`). Es actualmente el modelo de generación de imágenes más potente capaz de correr en local con una calidad profesional.
*   **Motor de Comprensión Visual (Qwen2-VL)**: Utilizamos **Qwen2-VL-7B-Instruct** (vía `mlx-vlm`) para todas las funciones de "Interrogación". Este modelo permite que la app analice imágenes, realice OCR (lectura de textos) y describa escenas con una precisión asombrosa.
*   **Interfaz (Gradio)**: Proporciona una UI moderna, accesible desde cualquier navegador local, lo que permite una gestión fluida de archivos y una previsualización inmediata.
*   **Traducción (Deep Translator)**: Un módulo intermedio que permite al usuario escribir prompts en español, traduciéndolos al inglés en tiempo real para obtener los mejores resultados de los modelos de IA.

## 3. Optimización para Apple Silicon (M4 Pro)
La aplicación ha sido configurada específicamente para aprovechar el hardware de los nuevos chips M4 Pro:

*   **Cuantización 4-bit**: Todos los modelos se ejecutan en versiones de 4 bits. Esto reduce drásticamente el uso de memoria RAM (VRAM) sin una pérdida perceptible de calidad, permitiendo que modelos de gran tamaño corran en un Mac Mini.
*   **Unified Memory Management**: Se utiliza la memoria unificada de Apple para mover datos entre la CPU y la GPU de forma instantánea.
*   **Metal Cache Clearing**: Implementamos una función que limpia el caché de la GPU de Apple tras cada inferencia pesada, evitando que el sistema se ralentice tras múltiples ediciones.
*   **Inferencia en Local**: Todo el procesamiento ocurre en el chip M4 Pro. No hay datos que salgan del ordenador, lo que garantiza privacidad total y latencia mínima.

## 4. Capacidades en Local
*   **Generación (Txt2Img)**: Crear imágenes desde instrucciones de texto.
*   **Edición Instruct (Img2Img)**: Cargar una imagen y pedir cambios específicos mediante texto (añadir objetos, cambiar colores, modificar estilos).
*   **Análisis Multimodal (VLM)**: Chat interactivo con una imagen. La IA puede responder preguntas complejas sobre el contenido visual.
*   **Gestión de Versiones**: Sistema de historial de sesión y control de versiones alpha para el desarrollo continuo.

---
*Este proyecto demuestra que un flujo de trabajo profesional de IA ya no requiere servidores externos, sino que puede vivir plenamente en el escritorio de un creativo.*
