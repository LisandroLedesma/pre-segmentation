# Pre-segmentation Tool

Genera coordenadas de puntos y bounding boxes en formato SAM2 para usar en Kaggle.

## Objetivo

Crear coordenadas de anotación para modelos de segmentación SAM2, permitiendo seleccionar puntos (Foreground/Background) y bounding boxes directamente sobre imágenes.

## Uso

1. **Carga una imagen** (PNG, JPG, JPEG, GIF, BMP)
2. **Haz clic** en la imagen para agregar puntos
3. **Selecciona el tipo**: Foreground (1) o Background (0)
4. **Copia/Descarga** el JSON en formato SAM2

## Ejecutar localmente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run src/app.py
```

Abre `http://localhost:8501` en tu navegador.
