import os
from huggingface_hub import snapshot_download

def download_qwen_image_model(model_id="mlx-community/Qwen2-VL-7B-Instruct-4bit", local_dir="models/Qwen-Image-2.0-7B-Instruct-MLX"):
    """
    Descarga el modelo especificado desde Hugging Face.
    Asegura que se descarguen los archivos necesarios para MLX.
    """
    print(f"Iniciando descarga del modelo {model_id}...")
    
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
        
    try:
        # Priorizamos descargar archivos .npz o .safetensors únicos (no sharded)
        # y los archivos de configuración.
        snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            # Evitamos descargar los pesos sharded de transformers si existen los npz de MLX
            ignore_patterns=["*.msgpack", "*.bin", "*.h5"],
            revision="main"
        )
        print(f"\n¡Descarga completada! Los pesos están en: {local_dir}")
        return True
    except Exception as e:
        print(f"\nError durante la descarga: {e}")
        print("\nTIP: Si el modelo es privado, asegúrate de haber ejecutado 'huggingface-cli login'.")
        return False

if __name__ == "__main__":
    # Nota: Usamos Qwen2-VL-7B como base compatible con MLX hasta que 
    # los pesos específicos de Qwen-Image 2.0 estén listados bajo ese ID exacto.
    # El usuario puede cambiar este ID si tiene acceso a uno más específico.
    download_qwen_image_model()
