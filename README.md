macOS y Linux:
source venv/bin/activate

source venv/Scripts/activate -- Git bash

PowerShell:
.\venv\Scripts\Activate.ps1

Windows:
.\venv\Scripts\activate

#Commit
git add .
git commit -m "Aquí escribes qué hiciste"

#Subir datos
git push origin main


ESTRUCUTA DE ARCHIVOS

LuminaCast/
├── assets/
│   ├── fondos/
│   └── icono.ico
├── data/
│   ├── bible-data-es-spa-main/
│   ├── biblias/
│   ├── bible-data-es-spa-main.zip
│   └── RVR1960 - Spanish.json
├── src/
│   ├── core/
│   ├── database/
│   └── ui/
│       ├── __init__.py
│       └── main.py
├── .gitignore
├── importar_biblia.py
├── importar_biblias.py
├── lumina_cast.db
├── notas.txt
├── README.md
├── requirements.txt
└── ter