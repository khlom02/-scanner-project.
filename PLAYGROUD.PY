import cv2
import pytesseract
import subprocess
import os
import re
import pandas as pd
import spacy

# Cargar el modelo en español de spaCy
nlp = spacy.load("es_core_news_md")  # Usa tu modelo entrenado si es necesario

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

def match_patterns(pattern_list, text):
    """Buscar coincidencias usando una lista de patrones."""
    for pattern in pattern_list:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return "No encontrado"

def extract_data_from_text(text):
    """Filtrar datos (empresa, fecha y monto total) usando expresiones regulares más robustas."""
    
    # Expresiones regulares mejoradas
    patterns = {
        "empresa": [
             r"(?:GOMAS(?: Y REPUESTOS)?|IMPORTADORA(?: Y EXPORTADORA)?[\w\s]+(?:LIMITADA)?|TRICOT|CENCOSUD RETAIL(?:SANTA(?: ISABEL)?)?)",
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",  # Nuevos formatos de empresas
        ],
        "fecha": [
            r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # dd/mm/yyyy
            r"\b\d{4}-\d{1,2}-\d{1,2}\b",  # yyyy-mm-dd
        ],
        "monto": [
            r"(?i)total[:\s]*\$?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)",
            r"(?i)importe[:\s]*\$?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)",
        ]
    }
    
    # Buscar todas las coincidencias posibles
    empresa = match_patterns(patterns["empresa"], text)
    fecha = match_patterns(patterns["fecha"], text)
    total = match_patterns(patterns["monto"], text)
    
    # Procesar los datos
    total = total.replace(",", ".") if total != "No encontrado" else "Monto no encontrado"
    
    return empresa, fecha, total

def log_missing_data(file_path, data):
    """Registrar los casos con datos faltantes."""
    with open("errores_log.txt", "a") as log_file:
        log_file.write(f"Archivo: {file_path} - Datos incompletos: {data}\n")

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
    print(text)

    # Filtrar los datos relevantes (empresa, fecha, monto)
    empresa, fecha, total = extract_data_from_text(text)

    # Si falta algún dato, registrar el error
    if empresa == "No encontrado" or fecha == "No encontrado" or total == "Monto no encontrado":
        log_missing_data(image_path, {"empresa": empresa, "fecha": fecha, "total": total})
    
    # Imprimir los datos extraídos
    print(f"Datos extraídos de {image_path}:")
    print(f"Empresa: {empresa}")
    print(f"Fecha: {fecha}")
    print(f"Total: {total}")
    
    return empresa, fecha, total

def process_images_in_folder(folder_path, lang='spa'):
    """Procesar todas las imágenes en una carpeta específica y escribir en un archivo Excel."""
    if not os.path.exists(folder_path):
        print(f"Error: La ruta {folder_path} no existe.")
        return
    
    # Lista para almacenar los datos extraídos
    data = []

    # Iterar sobre los archivos en la carpeta
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Verificar si es un archivo de imagen (puedes ajustar los tipos según sea necesario)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            empresa, fecha, total = process_image(file_path, lang)
            data.append([empresa, fecha, total])

    # Crear un DataFrame de pandas y exportarlo a un archivo Excel
    if data:
        df = pd.DataFrame(data, columns=["Empresa", "Fecha", "Total"])
        excel_path = os.path.join(folder_path, "datos_extraidos.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"Datos exportados a {excel_path}")

# Ruta de la carpeta donde están las imágenes
folder_path = r"C:\Users\MIGUE\OneDrive\Desktop\imagenes"  # Cambia la ruta si es necesario

# Procesar todas las imágenes dentro de la carpeta
process_images_in_folder(folder_path, lang='spa')  # Detectar texto en español
