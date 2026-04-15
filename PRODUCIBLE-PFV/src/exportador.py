"""
Módulo de exportación.
Genera el archivo Excel de salida-
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from openpyxl.styles import Font


def aplicar_formato_hoja(worksheet) -> None:
    """
    Aplica formato general a una hoja de Excel:
    - encabezados en negritas
    - congelar primera fila
    - ajustar ancho de columnas
    """
    worksheet.freeze_panes = "A2"

    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter

        for cell in column_cells:
            valor = "" if cell.value is None else str(cell.value)
            if len(valor) > max_length:
                max_length = len(valor)

        worksheet.column_dimensions[column_letter].width = max_length + 2


def aplicar_formato_numerico(worksheet) -> None:
    """
    Aplica formato numérico simple a celdas con números.
    """
    for row in worksheet.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, (int, float)):
                cell.number_format = "0.000"


def exportar_a_excel(
    df_minutal: pd.DataFrame,
    df_horario: pd.DataFrame,
    df_diario: pd.DataFrame,
    ruta_salida: str,
) -> str:
    """
    Exporta los resultados a un archivo Excel con tres hojas:
    - datos_minutales_procesados
    - resumen_horario
    - resumen_diario
    """
    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df_minutal.to_excel(
            writer,
            sheet_name="datos_minutales_procesados",
            index=False,
        )
        df_horario.to_excel(
            writer,
            sheet_name="resumen_horario",
            index=False,
        )
        df_diario.to_excel(
            writer,
            sheet_name="resumen_diario",
            index=False,
        )

        hoja_minutal = writer.sheets["datos_minutales_procesados"]
        hoja_horaria = writer.sheets["resumen_horario"]
        hoja_diaria = writer.sheets["resumen_diario"]

        for hoja in [hoja_minutal, hoja_horaria, hoja_diaria]:
            aplicar_formato_hoja(hoja)
            aplicar_formato_numerico(hoja)

    return os.path.abspath(ruta_salida)