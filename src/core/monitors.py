from PyQt6.QtGui import QGuiApplication
from database.db_manager import obtener_configuracion

def gestionar_pantallas(ventana_proyector, ventana_stage=None):
    """
    Detecta los monitores conectados y envía las ventanas (Audiencia e Interna) 
    según la configuración elegida por el usuario.
    """
    pantallas = QGuiApplication.screens()
    print(f"[LuminaCast] Monitores detectados: {len(pantallas)}")

    idx_audience = obtener_configuracion("pantalla_audience")
    idx_stage = obtener_configuracion("pantalla_stage")

    # 1. Configurar Proyector Principal (Audiencia)
    idx_aud = int(idx_audience) if idx_audience and idx_audience.isdigit() else (1 if len(pantallas) > 1 else 0)
    if idx_aud < len(pantallas):
        pantalla_destino = pantallas[idx_aud]
        geometria = pantalla_destino.geometry()
        ventana_proyector.move(geometria.left(), geometria.top())
        
        if idx_aud > 0:
            ventana_proyector.showFullScreen()
            print(f"[LuminaCast] Audiencia activada en monitor {idx_aud} (FullScreen).")
        else:
            ventana_proyector.show()
            print(f"[LuminaCast] Audiencia activada en ventana (Monitor Principal).")

    # 2. Configurar Stage Display (Interno)
    if ventana_stage:
        if idx_stage and idx_stage.isdigit() and int(idx_stage) < len(pantallas):
            idx_stg = int(idx_stage)
            geo_stage = pantallas[idx_stg].geometry()
            ventana_stage.move(geo_stage.left(), geo_stage.top())
            ventana_stage.showFullScreen()
            print(f"[LuminaCast] Stage Display activado en monitor {idx_stg} (FullScreen).")
        else:
            print("[LuminaCast] Stage Display no configurado o sin monitor válido. Quedará en segundo plano.")
            # Descomenta la siguiente línea si quieres que se abra en ventana flotante aunque no haya monitor
            # ventana_stage.show()