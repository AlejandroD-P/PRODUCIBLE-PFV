"""
Módulo de procesamiento
Realiza el cálculo de energía minutal y el resumen horario/diario.
"""

from __future__ import annotations

import pandas as pd


def calcular_energia_minutal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la energía minutal estimada en kWh.

    Fórmula:
    energia_minutal_kwh = (potencia_activa_mw * 1000 / 60) * (disponibilidad / 100)
    """
    df = df.copy()

    df["factor_disponibilidad"] = df["disponibilidad"] / 100.0
    df["energia_minutal_kwh"] = (
        (df["potencia_activa"] * 1000.0) / 60.0
    ) * df["factor_disponibilidad"]

    df["calidad_dato"] = "OK"

    columnas_criticas = [
        "irradiancia_poa",
        "temp_ambiente",
        "temp_celda",
        "viento",
        "disponibilidad",
        "potencia_activa",
    ]

    mascara_nulos = df[columnas_criticas].isna().any(axis=1)
    df.loc[mascara_nulos, "calidad_dato"] = "INCOMPLETO"

    return df


def generar_resumen_horario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa la información por hora y genera el resumen horario.
    """
    df = df.copy()
    df["hora"] = df["timestamp"].dt.floor("h")

    resumen = (
        df.groupby("hora", as_index=False)
        .agg(
            energia_horaria_kwh=("energia_minutal_kwh", "sum"),
            promedio_irradiancia_poa=("irradiancia_poa", "mean"),
            promedio_temp_ambiente=("temp_ambiente", "mean"),
            promedio_temp_celda=("temp_celda", "mean"),
            promedio_viento=("viento", "mean"),
            promedio_disponibilidad=("disponibilidad", "mean"),
            promedio_potencia_activa_mw=("potencia_activa", "mean"),
            promedio_consigna_mw=("consigna", "mean"),
            registros=("timestamp", "count"),
            registros_incompletos=("calidad_dato", lambda x: (x != "OK").sum()),
        )
    )

    columnas_redondear = [
        "energia_horaria_kwh",
        "promedio_irradiancia_poa",
        "promedio_temp_ambiente",
        "promedio_temp_celda",
        "promedio_viento",
        "promedio_disponibilidad",
        "promedio_potencia_activa_mw",
        "promedio_consigna_mw",
    ]

    resumen[columnas_redondear] = resumen[columnas_redondear].round(3)

    return resumen


def generar_resumen_diario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen diario general del archivo procesado.
    """
    energia_total = df["energia_minutal_kwh"].sum()
    irradiancia_promedio = df["irradiancia_poa"].mean()
    temp_ambiente_promedio = df["temp_ambiente"].mean()
    temp_celda_promedio = df["temp_celda"].mean()
    viento_promedio = df["viento"].mean()
    disponibilidad_promedio = df["disponibilidad"].mean()
    potencia_activa_promedio = df["potencia_activa"].mean()
    consigna_promedio = df["consigna"].mean()
    total_registros = len(df)
    registros_incompletos = int((df["calidad_dato"] != "OK").sum())

    fecha_inicio = df["timestamp"].min()
    fecha_fin = df["timestamp"].max()

    resumen_diario = pd.DataFrame(
        [
            {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "energia_total_kwh": round(energia_total, 3),
                "irradiancia_promedio": round(irradiancia_promedio, 3),
                "temp_ambiente_promedio": round(temp_ambiente_promedio, 3),
                "temp_celda_promedio": round(temp_celda_promedio, 3),
                "viento_promedio": round(viento_promedio, 3),
                "disponibilidad_promedio": round(disponibilidad_promedio, 3),
                "potencia_activa_promedio_mw": round(potencia_activa_promedio, 3),
                "consigna_promedio_mw": round(consigna_promedio, 3),
                "total_registros": total_registros,
                "registros_incompletos": registros_incompletos,
            }
        ]
    )

    return resumen_diario