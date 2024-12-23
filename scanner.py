import cv2
import pytesseract
import subprocess
import os
import re
import pandas as pd

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


def extract_data_from_text(text):
    """Filtrar datos (empresa, fecha y monto total) usando expresiones regulares más robustas."""
    
    # Expresiones regulares mejoradas
    empresa_pattern = r"(?:GOMAS(?: Y REPUESTOS)?|IMPORTADORA(?: Y EXPORTADORA)?[\w\s]+(?:LIMITADA)?)"
    fecha_pattern = r"\b\d{1,2}/\d{1,2}/\d{4}\b"  # Solo fechas, excluye horas
    monto_pattern = r"(?i)total[:\s]*\$?\s?(\d{1,3}(?:[.,]\d{3})*(?:\.\d{2})?)"
    
    # Buscar todas las coincidencias posibles
    empresas = re.findall(empresa_pattern, text, re.IGNORECASE)
    fechas = re.findall(fecha_pattern, text)
    montos = re.findall(monto_pattern, text)
    
    # Procesar resultados
    empresa = empresas[0].strip() if empresas else "Empresa no encontrada"
    fecha = fechas[0] if fechas else "Fecha no encontrada"
    total = montos[-1].replace(",", ".") if montos else "Monto no encontrado"  # Tomar el último monto encontrado
    
    return empresa, fecha, total

# Ejemplo de prueba
texto = """
IMPORTADORA Y EXPORTADORA +) INMAN LIMITADA
SAN FRANCISCO 735,PUERTO VARAS

Tel: +560968576766

Fecha: 3/12/2024 20:28 IMP:PC-202310311553

Can. Pre. Descripcion Suma

=1x 2 Articulo 2 PESO
1x7,990 -15% Artículo 7990 PES 6, 782

Total 6,790 PESO
Entregado 6,790

Fac.Simpli.No, 3454

NO HACEMOS DEVOLUCION EN EFECTIVO!
PERIODO DE CAMBIA EN 15 DIAS!SALVO TARA.
MUCHAS GRACIAS POR SU VISITA
"""

empresa, fecha, total = extract_data_from_text(texto)
print("Empresa:", empresa)
print("Fecha:", fecha)
print("Monto Total:", total)

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
