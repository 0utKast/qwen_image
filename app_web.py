import gradio as gr
import os
from PIL import Image
from model_manager import QwenImageGenerator
from datetime import datetime

# Inicializar generador
generator = QwenImageGenerator()

# Directorio de salida
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estado global para la galería
session_history = []

def process_generation(prompt, steps, guidance, seed, resolution, use_translation):
    try:
        final_prompt = generator.translate_prompt(prompt) if use_translation else prompt
        image = generator.generate_image(final_prompt, steps, guidance, seed, resolution)
        filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        generator.save_image(image, filepath)
        
        session_history.insert(0, filepath) # Añadir al inicio
        return image, None, session_history
    except Exception as e:
        return None, f"Error: {str(e)}", session_history

def process_editing(input_image, prompt, strength, steps, guidance, seed, resolution, use_translation):
    if input_image is None:
        return None, "Error: Por favor, carga una imagen original para editar.", session_history
    try:
        final_prompt = generator.translate_prompt(prompt) if use_translation else prompt
        # Guardar imagen temporal para el motor
        temp_input = os.path.join(OUTPUT_DIR, "temp_input.png")
        input_image.save(temp_input)
        
        image = generator.generate_image(final_prompt, steps, guidance, seed, resolution, image_path=temp_input, strength=strength)
        
        filename = f"edit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        generator.save_image(image, filepath)
        
        session_history.insert(0, filepath)
        return image, None, session_history
    except Exception as e:
        return None, f"Error: {str(e)}", session_history

def process_analysis(input_image, query):
    if input_image is None:
        return "Error: Cargue una imagen para analizar."
    try:
        temp_input = os.path.join(OUTPUT_DIR, "temp_analyze.png")
        input_image.save(temp_input)
        response = generator.interrogate_image(temp_input, query)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Construir la interfaz Gradio
with gr.Blocks(title="Qwen Studio Editor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 Qwen Studio Editor")
    gr.Markdown("Suite creativa integral para Mac Mini M4 Pro (Powered by FLUX MLX & Qwen2-VL)")
    
    with gr.Tabs():
        # --- PESTAÑA 1: GENERACIÓN ---
        with gr.TabItem("✨ Generar"):
            with gr.Row():
                with gr.Column(scale=1):
                    gen_prompt = gr.Textbox(label="Prompt (Español o Inglés)", placeholder="Un gato astronauta en Marte...", lines=3)
                    use_translation = gr.Checkbox(label="Traducción automática (ES -> EN)", value=True)
                    with gr.Accordion("Parámetros", open=False):
                        gen_steps = gr.Slider(1, 4, 4, step=1, label="Steps")
                        gen_guidance = gr.Slider(0.0, 10.0, 0.0, step=0.1, label="Guidance")
                        gen_seed = gr.Number(-1, label="Seed")
                        gen_res = gr.Dropdown(["512x512", "768x768", "1024x1024"], value="1024x1024", label="Resolución")
                    gen_btn = gr.Button("Generar Arte", variant="primary")
                with gr.Column(scale=1):
                    gen_output = gr.Image(label="Resultado")
                    gen_error = gr.Markdown()
                    gen_file = gr.File(label="Descargar", visible=False)

        # --- PESTAÑA 2: EDICIÓN (Instruct-Editing) ---
        with gr.TabItem("🖌️ Editar (I2I)"):
            with gr.Row():
                with gr.Column(scale=1):
                    edit_input = gr.Image(label="Imagen Original", type="pil")
                    edit_prompt = gr.Textbox(label="Instrucción de Edición", placeholder="Cambia el cielo a un atardecer púrpura...")
                    edit_use_translation = gr.Checkbox(label="Traducción automática (ES -> EN)", value=True)
                    edit_strength = gr.Slider(0.0, 1.0, 0.8, step=0.05, label="Fuerza de Cambio (Denoising)")
                    with gr.Accordion("Avanzado", open=False):
                        edit_steps = gr.Slider(1, 4, 4, step=1, label="Steps")
                        edit_res = gr.Dropdown(["512x512", "768x768", "1024x1024"], value="1024x1024", label="Resolución")
                    edit_btn = gr.Button("Aplicar Cambios", variant="primary")
                with gr.Column(scale=1):
                    edit_output = gr.Image(label="Imagen Editada")
                    edit_error = gr.Markdown()

        # --- PESTAÑA 3: ANÁLISIS (VLM) ---
        with gr.TabItem("👁️ Interrogar (VLM)"):
            with gr.Row():
                with gr.Column(scale=1):
                    vlm_input = gr.Image(label="Imagen para Analizar", type="pil")
                    vlm_query = gr.Textbox(label="¿Qué quieres saber?", value="Describe esta imagen en detalle.")
                    vlm_btn = gr.Button("Analizar", variant="primary")
                with gr.Column(scale=1):
                    vlm_output = gr.Textbox(label="Respuesta de Qwen AI", lines=10)

    # Galería de Sesión
    gr.Markdown("### 🕒 Historial de la Sesión")
    gallery = gr.Gallery(label="Mis Creaciones", columns=4, height="auto")

    # Lógica de los botones
    gen_btn.click(
        process_generation, 
        inputs=[gen_prompt, gen_steps, gen_guidance, gen_seed, gen_res, use_translation], 
        outputs=[gen_output, gen_error, gallery]
    )
    
    edit_btn.click(
        process_editing,
        inputs=[edit_input, edit_prompt, edit_strength, edit_steps, gen_guidance, gen_seed, edit_res, edit_use_translation],
        outputs=[edit_output, edit_error, gallery]
    )
    
    vlm_btn.click(
        process_analysis,
        inputs=[vlm_input, vlm_query],
        outputs=[vlm_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", inbrowser=True)
