from PyQt6.QtGui import QGuiApplication
from database.db_manager import obtener_configuracion

def gestionar_pantallas(ventana_proyector):
    """
    Detecta los monitores conectados y envía la ventana del proyector 
    según la configuración elegida por el usuario en la base de datos.
    """
    pantallas = QGuiApplication.screens()
    print(f"[LuminaCast] Monitores detectados: {len(pantallas)}")

    # Leer qué pantalla eligió el usuario para Audiencia
    idx_guardado = obtener_configuracion("pantalla_audience")
    
    # Si no hay nada guardado, asume el 1 (segundo monitor) o 0 si solo hay un monitor
    idx = int(idx_guardado) if idx_guardado and idx_guardado.isdigit() else (1 if len(pantallas) > 1 else 0)

    # Verificar que el monitor seleccionado realmente exista (por si se desconectó el HDMI)
    if idx < len(pantallas):
        pantalla_destino = pantallas[idx]
        geometria = pantalla_destino.geometry()
        
        # Mover la ventana a las coordenadas de la pantalla configurada
        ventana_proyector.move(geometria.left(), geometria.top())
        
        # Si es un monitor secundario (índice > 0), lo ponemos en FullScreen
        if idx > 0:
            ventana_proyector.showFullScreen()
            print(f"[LuminaCast] Éxito: Proyección activada en pantalla secundaria ({idx}) a pantalla completa.")
        else:
            ventana_proyector.show()
            print(f"[LuminaCast] Proyección activada en ventana (Monitor Principal).")
    else:
        # Modo de contingencia (fallback)
        ventana_proyector.show()
        print("[LuminaCast] Advertencia: Monitor configurado no disponible. Modo ventana activado.")