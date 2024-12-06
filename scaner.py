import cv2
import pytesseract
import subprocess
import os

# Configurar la ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Verificar si Tesseract está configurado correctamente
try:
    subprocess.run([pytesseract.pytesseract.tesseract_cmd, '--version'], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar Tesseract: {e}")
except FileNotFoundError as e:
    print(f"No se encuentra el archivo ejecutable de Tesseract: {e}")

def validate_image_path(image_path):
    """Verificar si la ruta de la imagen existe y es válida."""
    if not os.path.exists(image_path):
        print(f"Error: La ruta {image_path} no existe.")
        return False
    return True

def resize_for_display(image, max_width=800, max_height=600):
    """Redimensiona la imagen para que se ajuste dentro de un tamaño máximo."""
    height, width = image.shape[:2]
    if width > max_width or height > max_height:
        scaling_factor = min(max_width / width, max_height / height)
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_image
    return image

def process_image(image_path, lang='spa'):
    """Procesar una imagen y extraer texto usando Tesseract OCR."""
    # Validar la ruta de la imagen
    if not validate_image_path(image_path):
        return

    # Leer la imagen
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: No se pudo cargar la imagen desde {image_path}. Verifica la ruta.")
        return

    # Escalado para mejorar el OCR
    scale_percent = 140  # Escalar al 140%
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    
    # Binarización adaptativa
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 16
    )

    # Reducir ruido
    denoised = cv2.GaussianBlur(binary, (5, 7), 0)

    # Extraer texto usando Tesseract con el idioma especificado
    text = pytesseract.image_to_string(denoised, lang=lang)  # Usar el argumento 'lang'

    # Mostrar el texto extraído
    print("Texto detectado:")
    print(text)

    # Mostrar imágenes procesadas para depurar (redimensionadas)
    cv2.imshow("Original", resize_for_display(image))
    cv2.imshow("Grises", resize_for_display(gray))
    cv2.imshow("Binarizada", resize_for_display(binary))
    cv2.imshow("Sin Ruido", resize_for_display(denoised))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Ruta de ejemplo a una imagen
image_path = "segunda_imagen.jpg"  # Cambia esto a la ruta de tu imagen
process_image(image_path, lang='spa')  # Detectar texto en español
