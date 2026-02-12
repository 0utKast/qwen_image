import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import threading
from datetime import datetime
from model_manager import QwenImageGenerator

# Configuración estética
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class QwenImageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Qwen-Image 2.0 Local Explorer")
        self.geometry("1100x750")

        # Inicializar generador de IA
        self.generator = QwenImageGenerator()
        self.current_image = None

        # Layout principal (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra Lateral (Configuración)
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Qwen-Image 2.0", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Parámetros en Sidebar
        self.steps_label = ctk.CTkLabel(self.sidebar_frame, text="Inference Steps:")
        self.steps_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.steps_slider = ctk.CTkSlider(self.sidebar_frame, from_=10, to=150, number_of_steps=28)
        self.steps_slider.set(50)
        self.steps_slider.grid(row=2, column=0, padx=20, pady=(0, 10))

        self.guidance_label = ctk.CTkLabel(self.sidebar_frame, text="Guidance Scale:")
        self.guidance_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        self.guidance_slider = ctk.CTkSlider(self.sidebar_frame, from_=1.0, to=20.0, number_of_steps=19)
        self.guidance_slider.set(7.5)
        self.guidance_slider.grid(row=4, column=0, padx=20, pady=(0, 10))

        self.res_label = ctk.CTkLabel(self.sidebar_frame, text="Resolution:")
        self.res_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.res_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["512x512", "768x768", "1024x1024", "2048x2048 (2K)"])
        self.res_menu.set("1024x1024")
        self.res_menu.grid(row=6, column=0, padx=20, pady=(0, 10))

        self.seed_label = ctk.CTkLabel(self.sidebar_frame, text="Seed (-1 = Random):")
        self.seed_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.seed_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="-1")
        self.seed_entry.insert(0, "-1")
        self.seed_entry.grid(row=8, column=0, padx=20, pady=(0, 10))

        # Status y Modelo
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", text_color="gray")
        self.status_label.grid(row=11, column=0, padx=20, pady=10)

        # Área Principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Input de Prompt
        self.prompt_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Describe la imagen que quieres generar...", height=50, font=ctk.CTkFont(size=14))
        self.prompt_entry.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="ew")

        self.generate_btn = ctk.CTkButton(self.main_frame, text="Generate Image", height=50, font=ctk.CTkFont(size=14, weight="bold"), command=self.start_generation)
        self.generate_btn.grid(row=0, column=1, padx=(0, 20), pady=(10, 10))

        # Preview de Imagen
        self.preview_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#1a1a1a")
        self.preview_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(self.preview_frame, text="La preview de la imagen aparecerá aquí", text_color="gray")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        # Acciones de Imagen
        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        self.save_btn = ctk.CTkButton(self.actions_frame, text="Save Local", state="disabled", fg_color="#2ecc71", hover_color="#27ae60", command=self.save_image)
        self.save_btn.pack(side="right", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # Diálogo de Carga de Modelo Inicial
        self.after(500, self.initial_model_check)

    def initial_model_check(self):
        if not self.generator.check_model_exists():
            self.status_label.configure(text="Status: Model Missing", text_color="#e74c3c")
            tk.messagebox.showwarning("Modelo no encontrado", 
                f"No se han encontrado los pesos en: {self.generator.model_path}\n\n"
                "Por favor, descarga los pesos desde Hugging Face y colócalos en esa carpeta.")
        else:
            self.status_label.configure(text="Status: Loading Model...", text_color="#f1c40f")
            threading.Thread(target=self.load_model_bg, daemon=True).start()

    def load_model_bg(self):
        success = self.generator.load_model()
        if success:
            self.status_label.configure(text="Status: Model Ready", text_color="#2ecc71")
        else:
            self.status_label.configure(text="Status: Load Error", text_color="#e74c3c")
            tk.messagebox.showerror("Error", self.generator.error_message)

    def start_generation(self):
        prompt = self.prompt_entry.get()
        if not prompt:
            tk.messagebox.showwarning("Atención", "Por favor, escribe un prompt.")
            return

        if self.generator.model is None:
            tk.messagebox.showerror("Error", "El modelo no está cargado.")
            return

        self.generate_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.status_label.configure(text="Status: Generating...", text_color="#f1c40f")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        # Obtener parámetros
        params = {
            "steps": int(self.steps_slider.get()),
            "guidance_scale": self.guidance_slider.get(),
            "seed": int(self.seed_entry.get()),
            "resolution": self.res_menu.get()
        }

        threading.Thread(target=self.generation_thread, args=(prompt, params), daemon=True).start()

    def generation_thread(self, prompt, params):
        try:
            image = self.generator.generate_image(prompt, **params)
            self.after(0, self.display_image, image)
        except Exception as e:
            self.after(0, self.handle_error, str(e))

    def display_image(self, image):
        self.current_image = image
        
        # Redimensionar para la preview pero manteniendo el ratio
        preview_size = (800, 600)
        img_copy = image.copy()
        img_copy.thumbnail(preview_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_copy)
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo # Keep reference

        self.generate_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.status_label.configure(text="Status: Generation Complete", text_color="#2ecc71")
        self.progress_bar.stop()
        self.progress_bar.set(1)

    def handle_error(self, message):
        self.generate_btn.configure(state="normal")
        self.status_label.configure(text="Status: Error", text_color="#e74c3c")
        self.progress_bar.stop()
        self.progress_bar.set(0)
        tk.messagebox.showerror("Error de Generación", message)

    def save_image(self):
        if self.current_image:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qwen_gen_{timestamp}.png"
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            save_path = os.path.join(desktop, filename)
            
            if self.generator.save_image(self.current_image, save_path):
                tk.messagebox.showinfo("Éxito", f"Imagen guardada en:\n{save_path}")

if __name__ == "__main__":
    app = QwenImageApp()
    app.mainloop()
