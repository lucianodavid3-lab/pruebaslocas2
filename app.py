from __future__ import annotations

import io
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@dataclass
class StockQueryResult:
    records: list[dict]
    columns: list[str]
    source_description: str


class StockService:
    """Servicio para leer y consultar stock desde Excel local o SharePoint."""

    CANDIDATE_SKU_COLUMNS = ["sku", "codigo", "cod", "producto", "item", "id"]

    def load_excel_from_local(self, file_path: str, sheet_name: str | None = None) -> pd.DataFrame:
        if not file_path:
            raise ValueError("Debes indicar una ruta de archivo.")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No existe el archivo: {file_path}")

        return pd.read_excel(file_path, sheet_name=sheet_name or 0)

    def load_excel_from_sharepoint_url(
        self,
        file_url: str,
        access_token: str,
        sheet_name: str | None = None,
    ) -> pd.DataFrame:
        if not file_url:
            raise ValueError("Debes indicar la URL del archivo en SharePoint.")
        if not access_token:
            raise ValueError("Debes indicar un token de acceso para SharePoint/Graph.")

        response = requests.get(
            file_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        response.raise_for_status()

        return pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name or 0)

    def find_sku_column(self, df: pd.DataFrame, custom_column: str | None = None) -> str:
        normalized = {str(col).strip().lower(): col for col in df.columns}

        if custom_column:
            key = custom_column.strip().lower()
            if key not in normalized:
                raise ValueError(
                    f"La columna '{custom_column}' no existe. Columnas detectadas: {list(df.columns)}"
                )
            return normalized[key]

        for candidate in self.CANDIDATE_SKU_COLUMNS:
            if candidate in normalized:
                return normalized[candidate]

        raise ValueError(
            "No se detectó una columna SKU automáticamente. Indica 'Nombre columna SKU'."
        )

    def query_stock(
        self,
        df: pd.DataFrame,
        sku_value: str,
        sku_column: str | None = None,
    ) -> StockQueryResult:
        if not sku_value:
            raise ValueError("Debes indicar un SKU a buscar.")

        sku_col = self.find_sku_column(df, sku_column)

        mask = (
            df[sku_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.contains(sku_value.strip().lower(), na=False)
        )
        matches = df[mask].fillna("")

        return StockQueryResult(
            records=matches.to_dict(orient="records"),
            columns=list(matches.columns),
            source_description=f"Coincidencias en columna '{sku_col}'",
        )


service = StockService()


@app.get("/")
def index():
    return render_template("index.html", result=None, error=None)


@app.post("/query")
def query():
    source_type = request.form.get("source_type", "local")
    local_path = request.form.get("local_path", "").strip()
    sharepoint_url = request.form.get("sharepoint_url", "").strip()
    token = request.form.get("token", "").strip()
    sku = request.form.get("sku", "").strip()
    sku_column = request.form.get("sku_column", "").strip() or None
    sheet_name = request.form.get("sheet_name", "").strip() or None

    try:
        if source_type == "sharepoint":
            df = service.load_excel_from_sharepoint_url(sharepoint_url, token, sheet_name)
            source_description = f"Fuente SharePoint: {sharepoint_url}"
        else:
            df = service.load_excel_from_local(local_path, sheet_name)
            source_description = f"Fuente local: {local_path}"

        result = service.query_stock(df, sku, sku_column)
        result.source_description = source_description

        return render_template("index.html", result=result, error=None)
    except Exception as exc:  # noqa: BLE001
        return render_template("index.html", result=None, error=str(exc))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
