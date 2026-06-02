# src/core/monitors.py
from PyQt6.QtGui import QGuiApplication

def gestionar_pantallas(ventana_proyector):
    """
    Detecta los monitores conectados. Si hay más de uno, envía la ventana 
    del proyector al segundo monitor en pantalla completa. Si solo hay uno,
    lo deja como ventana normal para poder desarrollar y hacer pruebas.
    """
    # Obtener la lista de pantallas detectadas por el sistema operativo
    pantallas = QGuiApplication.screens()
    
    print(f"[LuminaCast] Monitores detectados: {len(pantallas)}")

    if len(pantallas) > 1:
        # El índice 1 suele ser la pantalla secundaria (Proyector/TV)
        pantalla_secundaria = pantallas[1]
        geometria_secundaria = pantalla_secundaria.geometry()
        
        # Mover la ventana a las coordenadas de la segunda pantalla
        ventana_proyector.move(geometria_secundaria.left(), geometria_secundaria.top())
        
        # Activar el modo pantalla completa nativo (sin bordes ni barra de tareas)
        ventana_proyector.showFullScreen()
        print("[LuminaCast] Éxito: Proyección activada en pantalla secundaria a pantalla completa.")
    else:
        # Entorno de desarrollo o laptop sin proyector conectado
        ventana_proyector.show()
        print("[LuminaCast] Advertencia: Solo un monitor detectado. Modo ventana activado para pruebas.")