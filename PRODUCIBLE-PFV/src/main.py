"""
Punto de entrada del sistema Producible FV.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from exportador import exportar_a_excel
from procesador import (
    calcular_energia_minutal,
    generar_resumen_diario,
    generar_resumen_horario,
)
from validador import validar_archivo


def configurar_logging() -> None:
    """
    Configura el sistema de logs del proyecto.
    """
    Path("logs").mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename="logs/producible.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )


def cargar_archivo(ruta_entrada: str) -> pd.DataFrame:
    """
    Carga un archivo CSV o Excel.
    """
    ruta = Path(ruta_entrada)

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_entrada}")

    extension = ruta.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(ruta)
    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(ruta)

    raise ValueError(
        "Formato no soportado -- Usa un archivo .csv, .xlsx o .xls"
    )


def imprimir_mensajes_validacion(errores: list[str], advertencias: list[str]) -> None:
    """
    Imprime errores y advertencias de validación.
    """
    if errores:
        print("\nERRORES DE VALIDACIÓN:")
        for error in errores:
            print(f" - {error}")
            logging.error(error)

    if advertencias:
        print("\nADVERTENCIAS:")
        for advertencia in advertencias:
            print(f" - {advertencia}")
            logging.warning(advertencia)


def main() -> int:
    """
    Función principal del programa.
    """
    configurar_logging()

    parser = argparse.ArgumentParser(
        description="Sistema Producible de Energía Parque Fotovoltaico"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta del archivo de entrada (.csv o .xlsx)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Ruta del archivo Excel de salida",
    )

    args = parser.parse_args()

    try:
        logging.info("Inicio del proceso")
        logging.info("Archivo de entrada: %s", args.input)
        logging.info("Archivo de salida: %s", args.output)

        print("1) Cargando archivo de entrada...")
        df = cargar_archivo(args.input)
        print(f"   Archivo cargado correctamente. Registros: {len(df)}")
        logging.info("Archivo cargado correctamente. Registros: %s", len(df))

        print("2) Validando archivo...")
        resultado = validar_archivo(df)
        imprimir_mensajes_validacion(resultado.errores, resultado.advertencias)

        if not resultado.es_valido:
            logging.error("Proceso detenido: el archivo no pasó la validación.")
            print("\nProceso detenido: el archivo no pasó la validación.")
            return 1

        print("3) Procesando datos minutales...")
        df_procesado = calcular_energia_minutal(resultado.dataframe)
        logging.info("Cálculo minutal completado")

        print("4) Generando resumen horario...")
        df_horario = generar_resumen_horario(df_procesado)
        logging.info("Resumen horario generado. Registros: %s", len(df_horario))

        print("5) Generando resumen diario...")
        df_diario = generar_resumen_diario(df_procesado)
        logging.info("Resumen diario generado")

        print("6) Exportando resultados a Excel...")
        ruta_final = exportar_a_excel(
            df_minutal=df_procesado,
            df_horario=df_horario,
            df_diario=df_diario,
            ruta_salida=args.output,
        )

        logging.info("Archivo exportado correctamente: %s", ruta_final)
        print("\nProceso finalizado con éxito.")
        print(f"Archivo generado en: {ruta_final}")
        return 0

    except Exception as exc:
        logging.exception("Error durante la ejecución")
        print(f"\nError durante la ejecución: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())