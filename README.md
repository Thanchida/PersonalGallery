# PersonalGallery

## Routes

- `GET /`: Home page
- `GET /upload`: Upload form
- `POST /upload`: Handle upload + caption generation + persistence
- `GET /gallery`: Display uploaded images with captions
- `POST /api/caption`: Optional API route returning caption JSON

## Installation

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows (Command Prompt):

```bat
py -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Run the App

```bash
python3 app.py
```

Open in browser:

```text
http://localhost:5000
```

## Example Predictions

- Image: `dog.jpg`
  Caption: `a dog running on the grass`

- Image: `beach.jpg`
  Caption: `people walking on a beach`
