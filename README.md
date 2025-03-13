
Installation :
bash
Copier
python -m venv venv
source venv/bin/activate   # ou .\venv\Scripts\activate sous Windows
pip install -r requirements.txt
Configuration :
Placer la clé OPENAI_API_KEY dans .env, etc.
Lancement local :
bash
Copier
uvicorn app.main:app --reload
Utilisation : URL pour accéder au formulaire (http://127.0.0.1:8000/).