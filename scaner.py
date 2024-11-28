import cv2
import pytesseract
import subprocess

# Configurar la ruta a Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Verifica si Tesseract puede ejecutarse correctamente
try:
    subprocess.run([pytesseract.pytesseract.tesseract_cmd, '--version'], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar Tesseract: {e}")
except FileNotFoundError as e:
    print(f"No se encuentra el archivo ejecutable de Tesseract: {e}")

def process_image(image_path):
    # Leer la imagen
    image = cv2.imread(image_path)
    
    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar binarización para mejorar el texto
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Extraer texto usando Tesseract
    text = pytesseract.image_to_string(binary, lang='eng')
    
    # Mostrar el texto extraído
    print("Texto detectado:")
    print(text)

# Ruta de ejemplo a una imagen
image_path = "image.jpg"  # Cambia esto a la ruta de tu imagen
process_image(image_path)
