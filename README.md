# Qwen Studio Editor (Alpha v0.1.1) 🎨🚀

Suite creativa multimodal local optimizada para **Apple Silicon (Mac Mini M4 Pro)**. Genera, edita e interroga imágenes usando la potencia de los núcleos MLX.

## 🌟 Características

- **Motor Creativo**: Basado en **FLUX.1-schnell** (MLX 4-bit) para generación y edición Image-to-Image ultra rápida.
- **Motor Cognitivo**: Basado en **Qwen2-VL-7B** para análisis visual, OCR y descripción de escenas.
- **Edición Instruct**: Cambia elementos de tus imágenes mediante instrucciones en lenguaje natural.
- **Traducción Automática**: Soporte nativo para prompts en español (ES -> EN).
- **Optimización M4 Pro**: Gestión dinámica de VRAM y limpieza de caché de Metal para máxima fluidez.

## 🛠️ Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/TU_USUARIO/qwen_image.git
    cd qwen_image
    ```

2.  **Configurar el Token de Hugging Face**:
    Crea un archivo `.env` en la raíz con tu token:
    ```bash
    HF_TOKEN=hf_tu_token_aqui
    ```

3.  **Lanzar la aplicación**:
    Haz doble clic en `launch_qwen.command` o ejecútalo desde la terminal. El script configurará el entorno virtual y descargará los modelos automáticamente.

## 🚀 Uso de la Suite

- **Pestaña Generar**: Ideal para crear arte desde cero.
- **Pestaña Editar**: Sube tu imagen y usa el slider de *Denoising Strength* para controlar la fidelidad al original.
- **Pestaña Interrogar**: Pregunta a la IA sobre cualquier detalle de una imagen cargada.

## 📈 Roadmap de Versiones

- **v0.1.1-alpha** (Estable):
    - [x] Corregido motor VLM (Template de chat oficial).
    - [x] Invertida lógica de Denoising Strength para mejor UX.
    - [x] Añadido documento de resumen de proyecto.
- **v0.1.0-alpha**:
    - [x] Integración de mflux y mlx-vlm.
    - [x] Soporte para Image-to-Image.

## ⚖️ Licencia
Este proyecto es de uso personal y educativo. Los modelos FLUX y Qwen están sujetos a sus propias licencias de uso.

---
*Desarrollado con ❤️ para la comunidad de Apple Silicon.*
