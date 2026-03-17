# App de consulta de stock (Excel local o SharePoint)

Aplicación web simple en Flask para consultar stock por SKU a partir de un archivo Excel.

## Qué soporta

- 📁 Excel en carpeta local (`.xlsx`) — incluyendo carpetas sincronizadas de SharePoint/OneDrive.
- 🌐 URL de SharePoint/Microsoft Graph (descarga con token Bearer).
- 🔎 Búsqueda por SKU parcial (por ejemplo, `ABC` encuentra `ABC-123`).
- 🧠 Detección automática de columna SKU (`sku`, `codigo`, `producto`, etc.) o selección manual.

## Requisitos

- Python 3.10+

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Abrir en navegador: `http://localhost:5000`

## Uso rápido

1. Elegir origen de datos:
   - **Archivo local**: ruta del archivo, por ejemplo `/datos/stock.xlsx`.
   - **SharePoint/Graph**: URL directa al contenido + token Bearer.
2. Opcional: indicar hoja y nombre de columna SKU.
3. Escribir SKU a buscar.
4. Presionar **Consultar**.

## Tests

```bash
pytest
```
