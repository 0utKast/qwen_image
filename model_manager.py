import os
import mlx.core as mx
from mflux.models.flux.variants.txt2img.flux import Flux1
from mflux.models.common.config.model_config import ModelConfig
from mflux.models.common.config.config import Config
from PIL import Image
import numpy as np
import traceback
from pathlib import Path
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Importaciones para VLM (análisis de imágenes)
try:
    from mlx_vlm import load as load_vlm, generate as generate_vlm
    from mlx_vlm.utils import load_config as load_vlm_config
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False

# Cargar variables desde .env
load_dotenv()

class QwenImageGenerator:
    def __init__(self, flux_model_path="black-forest-labs/FLUX.1-schnell", vlm_model_path="mlx-community/Qwen2-VL-7B-Instruct-4bit"):
        self.flux_model_path = flux_model_path
        self.vlm_model_path = vlm_model_path
        self.model = None # Modelo mflux
        self.vlm_model = None
        self.vlm_processor = None
        self.loading = False
        self.error_message = ""
        self.engine_type = "flux"
        self.translator = GoogleTranslator(source='auto', target='en')

    def translate_prompt(self, text):
        """Traduce el texto al inglés si es necesario."""
        try:
            if not text or not text.strip():
                return text
            
            # GoogleTranslator maneja la detección de origen con 'auto'
            translated = self.translator.translate(text)
            print(f"Propuesta de Traducción: '{text}' -> '{translated}'")
            return translated
        except Exception as e:
            print(f"Error en traducción: {e}")
            return text

    def clear_vram(self):
        """Limpia el caché de la GPU de Apple (Metal)."""
        try:
            mx.metal.clear_cache()
            print("Caché de Metal (GPU) liberado.")
        except Exception as e:
            print(f"Error al limpiar caché: {e}")

    def load_model(self, quantization=4):
        """Carga el modelo FLUX para generación y edición."""
        if self.loading: return
        self.loading = True
        try:
            hf_token = os.getenv("HF_TOKEN")
            print(f"Cargando motor FLUX {self.flux_model_path}...")
            # mflux usa automáticamente el token si está en os.environ["HF_TOKEN"]
            self.model = Flux1.from_name("schnell", quantize=quantization)
            print("Motor FLUX cargado.")
            self.loading = False
            return True
        except Exception as e:
            traceback.print_exc()
            self.error_message = f"Error al cargar FLUX: {str(e)}"
            self.loading = False
            return False

    def load_vlm_engine(self):
        """Carga el motor VLM (Qwen2-VL) para análisis de imágenes."""
        if not VLM_AVAILABLE:
            self.error_message = "Módulo mlx-vlm no encontrado."
            return False
        if self.vlm_model is not None:
            return True
        try:
            print(f"Cargando motor VLM {self.vlm_model_path}...")
            self.vlm_model, self.vlm_processor = load_vlm(self.vlm_model_path)
            print("Motor VLM cargado.")
            return True
        except Exception as e:
            traceback.print_exc()
            self.error_message = f"Error al cargar VLM: {str(e)}"
            return False

    def generate_image(self, prompt, steps=4, guidance_scale=0.0, seed=-1, resolution="1024x1024", image_path=None, strength=0.8):
        """
        Genera o edita una imagen (Image-to-Image).
        strength: 0.0 (mismo que original) a 1.0 (cambio total).
        """
        if self.model is None:
            if not self.load_model():
                raise Exception(self.error_message)

        try:
            if not prompt or not prompt.strip():
                prompt = "A high-quality edited image, realistic, highly detailed"

            # Inversión de lógica: mflux usa strength como 'preservación'
            # (menor valor = más cambio). Invertimos el valor del usuario.
            mflux_strength = 1.0 - strength if image_path else None
            
            print(f"Procesando {'EDICIÓN' if image_path else 'GENERACIÓN'}: '{prompt}'...")
            print(f"Parámetros: Seed={seed}, Strength_I2I={strength} (Interno: {mflux_strength})")
            
            width, height = map(int, resolution.split('x'))
            final_seed = seed if seed != -1 else np.random.randint(0, 1000000)
            
            # Para edición (I2I), a veces necesitamos subir ligeramente los steps 
            # para que FLUX tenga margen de maniobra con el denoising.
            actual_steps = steps if not image_path else max(steps, 6)

            output = self.model.generate_image(
                seed=final_seed,
                prompt=prompt,
                num_inference_steps=actual_steps if actual_steps <= 8 else 8,
                width=width,
                height=height,
                guidance=guidance_scale,
                image_path=image_path if image_path else None,
                image_strength=mflux_strength
            )
            
            self.clear_vram() # Limpiar tras generar

            if hasattr(output, 'image'):
                return output.image
            else:
                return output
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Fallo en motor de imagen: {str(e)}")

    def interrogate_image(self, image_path, query="Describe esta imagen en detalle."):
        """Analiza una imagen usando el motor VLM."""
        if not self.load_vlm_engine():
            raise Exception(self.error_message)

        try:
            print(f"Analizando imagen: {query}...")
            # Aseguramos que el prompt tenga el formato adecuado para VLM
            formatted_prompt = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n<|vision|> {query}<|im_end|>\n<|im_start|>assistant\n"
            
            output = generate_vlm(
                self.vlm_model, 
                self.vlm_processor, 
                image_path, 
                formatted_prompt, 
                max_tokens=500
            )
            
            self.clear_vram() # Limpiar tras análisis
            return output
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Fallo en motor VLM: {str(e)}")

    def save_image(self, image, path):
        """Guarda la imagen generada en el disco."""
        try:
            image.save(path)
            return True
        except Exception as e:
            print(f"Error al guardar: {e}")
            return False
