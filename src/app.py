import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import json

# Import utilities
from utils.image_processing import draw_points_on_image, get_image_info
from utils.sam2_formatter import format_coordinates_for_sam2, export_sam2_json, get_sam2_preview
from utils.coordinate_utils import add_point_coordinate, add_bounding_box_coordinate, get_coordinates_summary, clear_coordinates

# Configuración de la página
st.set_page_config(
    page_title="Pre-segmentation Tool",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🔎 Pre-segmentation Tool")
    st.markdown("Carga una imagen y selecciona puntos o bounding boxes para obtener sus coordenadas")
    
    # Inicializar session state
    if 'coordinates' not in st.session_state:
        st.session_state.coordinates = []
    if 'last_click_coords' not in st.session_state:
        st.session_state.last_click_coords = None
    
    # Sidebar para controles
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Modo de selección
        selection_mode = st.radio(
            "Modo de selección:",
            ["Puntos", "Bounding Box"]
        )
        
        # Color del pincel
        stroke_color = st.color_picker("Color del pincel:", "#FF0000")
        
        # Grosor del pincel
        stroke_width = st.slider("Grosor del pincel:", 1, 10, 3)
        
        # Botón para limpiar
        if st.button("🗑️ Limpiar todo"):
            st.session_state.clear()
            st.rerun()
    
    # Carga de imagen
    uploaded_file = st.file_uploader(
        "📁 Carga una imagen",
        type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        help="Selecciona una imagen para comenzar"
    )
    
    if uploaded_file is not None:
        # Procesar imagen
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # Mostrar información de la imagen
        image_info = get_image_info(image)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ancho", f"{image_info['width']}px")
        with col2:
            st.metric("Alto", f"{image_info['height']}px")
        with col3:
            st.metric("Formato", image_info['format'])
        
        # Mostrar imagen clickeable con puntos
        st.subheader("🎨 Imagen cargada - Haz clic para agregar puntos")
        
        # Controles para agregar coordenadas
        if selection_mode == "Puntos":
            st.write("**Agregar puntos SAM2:**")
            
            # Tipo de punto para SAM2
            point_type = st.radio(
                "Tipo de punto:",
                ["Foreground", "Background"],
                horizontal=True
            )
            
            # Usar st_clickable_image para detectar clicks
            from streamlit_image_coordinates import streamlit_image_coordinates
            
            # Mostrar imagen clickeable con puntos dibujados
            if st.session_state.coordinates:
                # Si hay puntos, mostrar imagen con puntos dibujados
                image_with_points = draw_points_on_image(image, st.session_state.coordinates)
                coordinates = streamlit_image_coordinates(
                    image_with_points,
                    key="image_click"
                )
            else:
                # Si no hay puntos, mostrar imagen original
                coordinates = streamlit_image_coordinates(
                    image,
                    key="image_click"
                )
            
            if coordinates is not None:
                x_click, y_click = coordinates["x"], coordinates["y"]
                
                # Solo agregar punto si las coordenadas son diferentes a la última procesada
                # Esto evita que se agreguen puntos al cambiar el tipo de punto
                last_coords = st.session_state.get('last_click_coords', None)
                current_coords = (x_click, y_click)
                
                if last_coords != current_coords:
                    st.session_state.last_click_coords = current_coords
                    
                    new_coord = add_point_coordinate(st.session_state.coordinates, x_click, y_click, point_type)
                    st.session_state.coordinates.append(new_coord)
                    st.success(f"Punto {point_type} agregado: ({x_click}, {y_click}) - Label: {new_coord['Label']}")
                    st.rerun()
                else:
                    st.info(f"Click detectado en: ({x_click}, {y_click}) - Haz click en otra posición para agregar un nuevo punto")
            
            # También permitir entrada manual
            st.write("**O ingresa coordenadas manualmente:**")
            col1, col2 = st.columns(2)
            with col1:
                x_point = st.number_input("X:", min_value=0, max_value=image.width, value=0, key="x_point")
            with col2:
                y_point = st.number_input("Y:", min_value=0, max_value=image.height, value=0, key="y_point")
            
            if st.button("➕ Agregar punto manual"):
                new_coord = add_point_coordinate(st.session_state.coordinates, x_point, y_point, point_type)
                st.session_state.coordinates.append(new_coord)
                st.success(f"Punto {point_type} agregado: ({x_point}, {y_point}) - Label: {new_coord['Label']}")
                st.rerun()
        
        else:  # Bounding Box
            st.write("**Agregar bounding box SAM2:**")
            
            # Mostrar imagen normal para bounding boxes
            st.image(image, caption="Imagen para bounding boxes", width='stretch')
            
            col1, col2 = st.columns(2)
            with col1:
                x_rect = st.number_input("X:", min_value=0, max_value=image.width, value=0, key="x_rect")
                width_rect = st.number_input("Ancho:", min_value=1, max_value=image.width, value=50, key="width_rect")
            with col2:
                y_rect = st.number_input("Y:", min_value=0, max_value=image.height, value=0, key="y_rect")
                height_rect = st.number_input("Alto:", min_value=1, max_value=image.height, value=50, key="height_rect")
            
            if st.button("➕ Agregar bounding box"):
                new_coord = add_bounding_box_coordinate(st.session_state.coordinates, x_rect, y_rect, width_rect, height_rect)
                st.session_state.coordinates.append(new_coord)
                st.success(f"Bounding box agregado: ({x_rect}, {y_rect}, {width_rect}, {height_rect})")
                st.rerun()
        
        # Interfaz para selección de coordenadas
        st.subheader("📍 Selección de coordenadas")
        
        # Mostrar coordenadas actuales
        if st.session_state.coordinates:
            st.subheader("📍 Coordenadas actuales")
            
            # Mostrar tabla con botones de eliminación
            for i, coord in enumerate(st.session_state.coordinates):
                # Crear un contenedor para cada coordenada
                with st.container():
                    col_info, col_delete, col_copy, col_edit = st.columns([5, 1, 1, 1])
                    
                    with col_info:
                        # Información de la coordenada
                        coord_text = f"**{coord['Tipo']}** - Índice: {coord['Índice']}"
                        if "Label" in coord:  # Es un punto
                            coord_text += f"<br>📍 X: {coord['X']}, Y: {coord['Y']}, Label: {coord['Label']}"
                        else:  # Es un bounding box
                            coord_text += f"<br>📦 X: {coord['X']}, Y: {coord['Y']}, Ancho: {coord['Ancho']}, Alto: {coord['Alto']}"
                        st.markdown(coord_text, unsafe_allow_html=True)
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{i}", help="Eliminar"):
                            st.session_state.coordinates.pop(i)
                            st.rerun()
                    
                    with col_copy:
                        if st.button("📋", key=f"copy_{i}", help="Copiar"):
                            if "Label" in coord:
                                sam2_data = [{"point_coords": [[coord["X"], coord["Y"]]], "point_labels": [coord["Label"]]}]
                            else:
                                sam2_data = [{"box": [coord["X"], coord["Y"], coord["X"] + coord["Ancho"], coord["Y"] + coord["Alto"]]}]
                            st.code(json.dumps(sam2_data, indent=2), language="json")
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{i}", help="Editar"):
                            st.session_state[f"edit_mode_{i}"] = True
                            st.rerun()
                
                # Modo de edición
                if f"edit_mode_{i}" in st.session_state and st.session_state[f"edit_mode_{i}"]:
                    st.write("**Editar coordenadas:**")
                    edit_col1, edit_col2, edit_col3 = st.columns(3)
                    
                    with edit_col1:
                        if "Label" in coord:
                            new_x = st.number_input("X:", value=coord["X"], key=f"edit_x_{i}")
                            new_y = st.number_input("Y:", value=coord["Y"], key=f"edit_y_{i}")
                        else:
                            new_x = st.number_input("X:", value=coord["X"], key=f"edit_x_{i}")
                            new_y = st.number_input("Y:", value=coord["Y"], key=f"edit_y_{i}")
                    
                    with edit_col2:
                        if "Label" in coord:
                            new_label = st.selectbox("Label:", [0, 1], index=coord["Label"], key=f"edit_label_{i}")
                        else:
                            new_width = st.number_input("Ancho:", value=coord["Ancho"], key=f"edit_width_{i}")
                            new_height = st.number_input("Alto:", value=coord["Alto"], key=f"edit_height_{i}")
                    
                    with edit_col3:
                        if st.button("💾 Guardar", key=f"save_{i}"):
                            if "Label" in coord:
                                st.session_state.coordinates[i]["X"] = new_x
                                st.session_state.coordinates[i]["Y"] = new_y
                                st.session_state.coordinates[i]["Label"] = new_label
                            else:
                                st.session_state.coordinates[i]["X"] = new_x
                                st.session_state.coordinates[i]["Y"] = new_y
                                st.session_state.coordinates[i]["Ancho"] = new_width
                                st.session_state.coordinates[i]["Alto"] = new_height
                            del st.session_state[f"edit_mode_{i}"]
                            st.rerun()
                        
                        if st.button("❌ Cancelar", key=f"cancel_{i}"):
                            del st.session_state[f"edit_mode_{i}"]
                            st.rerun()
                
                # Separador visual entre coordenadas
                st.markdown("---")
            
            # Botones de acción globales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copiar para SAM2"):
                    sam2_text = get_sam2_preview(st.session_state.coordinates)
                    st.code(sam2_text, language="json")
            
            with col2:
                if st.button("💾 Descargar JSON SAM2"):
                    json_str, filename = export_sam2_json(st.session_state.coordinates)
                    st.download_button(
                        label="Descargar SAM2 JSON",
                        data=json_str,
                        file_name=filename,
                        mime="application/json"
                    )
            
            with col3:
                if st.button("🗑️ Limpiar coordenadas"):
                    st.session_state.coordinates = clear_coordinates(st.session_state.coordinates)
                    st.rerun()
        else:
            st.info("👆 Agrega coordenadas usando los controles de arriba")
    
    else:
        st.info("👆 Carga una imagen para comenzar")
        
        # Mostrar ejemplo de uso
        st.subheader("📖 Cómo usar:")
        st.markdown("""
        1. **Carga una imagen** usando el botón de arriba
        2. **Selecciona el modo** (Puntos o Bounding Box)
        3. **Para puntos**: Elige si es Foreground (1) o Background (0)
        4. **Ingresa coordenadas** usando los controles numéricos
        5. **Visualiza** las coordenadas en la tabla
        6. **Copia/Descarga** el formato SAM2 para usar en Kaggle
        """)

if __name__ == "__main__":
    main()
