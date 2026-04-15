"""
Módulo de validación.
Valida estructura, tipos, continuidad temporal y valores básicos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


# Columnas obligatorias del archivo de entrada
COLUMNAS_OBLIGATORIAS = [
    "timestamp",
    "irradiancia_poa",
    "temp_ambiente",
    "temp_celda",
    "viento",
    "disponibilidad",
    "potencia_activa",
    "consigna",
    "horas_solares",
]


@dataclass
class ResultadoValidacion:
    """Resultado de la validación."""
    es_valido: bool
    errores: List[str]
    advertencias: List[str]
    dataframe: pd.DataFrame


def validar_columnas(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Verifica que el DataFrame contenga todas las columnas obligatorias.
    """
    errores: List[str] = []
    columnas_actuales = set(df.columns.str.strip())

    for col in COLUMNAS_OBLIGATORIAS:
        if col not in columnas_actuales:
            errores.append(f"Falta la columna obligatoria: '{col}'")

    return len(errores) == 0, errores


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia nombres de columnas quitando espacios y pasándolas a minúsculas.
    """
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    return df


def convertir_timestamp(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Convierte la columna timestamp a datetime.
    """
    errores: List[str] = []
    df = df.copy()

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%H:%M", errors="coerce")
    except Exception as exc:
        errores.append(f"Error al convertir 'timestamp': {exc}")
        return df, errores

    nulos = df["timestamp"].isna().sum()
    if nulos > 0:
        errores.append(
            f"Se encontraron {nulos} registros con fecha/hora inválida en 'timestamp'."
        )

    return df, errores


def convertir_numericas(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Convierte columnas numéricas al tipo adecuado.
    """
    errores: List[str] = []
    advertencias: List[str] = []
    df = df.copy()

    columnas_numericas = [
        "irradiancia_poa",
        "temp_ambiente",
        "temp_celda",
        "viento",
        "disponibilidad",
        "potencia_activa",
        "consigna",
        "horas_solares",
    ]

    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Reglas de relleno controlado
    if "irradiancia_poa" in df.columns:
        vacios = df["irradiancia_poa"].isna().sum()
        if vacios > 0:
            df["irradiancia_poa"] = df["irradiancia_poa"].fillna(0)
            advertencias.append(
                f"Se rellenaron {vacios} valores vacíos en 'irradiancia_poa' con 0."
            )

    for col in ["temp_ambiente", "temp_celda", "viento"]:
        if col in df.columns:
            vacios = df[col].isna().sum()
            if vacios > 0:
                df[col] = df[col].interpolate(method="linear", limit_direction="both")
                restantes = df[col].isna().sum()

                if restantes == 0:
                    advertencias.append(
                        f"Se interpolaron {vacios} valores vacíos en '{col}'."
                    )
                else:
                    errores.append(
                        f"La columna '{col}' aún contiene {restantes} valores vacíos tras interpolación."
                    )

    for col in ["disponibilidad", "potencia_activa", "consigna", "horas_solares"]:
        if col in df.columns:
            nulos = df[col].isna().sum()
            if nulos > 0:
                errores.append(
                    f"La columna '{col}' contiene {nulos} valores no numéricos o vacíos."
                )

    return df, errores, advertencias


def validar_continuidad_minutal(df: pd.DataFrame) -> List[str]:
    """
    Verifica que el intervalo entre registros sea de 1 minuto.
    """
    advertencias: List[str] = []
    df = df.copy().sort_values("timestamp").reset_index(drop=True)

    diferencias = df["timestamp"].diff().dropna()
    diferencias_invalidas = diferencias[diferencias != pd.Timedelta(minutes=1)]

    if not diferencias_invalidas.empty:
        advertencias.append(
            f"Se detectaron {len(diferencias_invalidas)} saltos o interrupciones "
            "en la continuidad de 1 minuto."
        )

    return advertencias


def validar_rangos_basicos(df: pd.DataFrame) -> List[str]:
    """
    Revisa rangos básicos razonables para variables operativas.
    No detiene la ejecución; solo genera advertencias.
    """
    advertencias: List[str] = []

    rangos = {
        "irradiancia_poa": (0, 1500),
        "temp_ambiente": (-20, 60),
        "temp_celda": (-20, 100),
        "viento": (0, 60),
        "disponibilidad": (0, 100),
        "potencia_activa": (0, None),   # sin máximo fijo en este MVP
        "consigna": (0, None),
        "horas_solares": (0, 1),        # sugerido como bandera 0/1
    }

    for columna, (minimo, maximo) in rangos.items():
        if minimo is not None:
            fuera_min = (df[columna] < minimo).sum()
            if fuera_min > 0:
                advertencias.append(
                    f"La columna '{columna}' tiene {fuera_min} valores menores a {minimo}."
                )

        if maximo is not None:
            fuera_max = (df[columna] > maximo).sum()
            if fuera_max > 0:
                advertencias.append(
                    f"La columna '{columna}' tiene {fuera_max} valores mayores a {maximo}."
                )

    return advertencias


def validar_archivo(df: pd.DataFrame) -> ResultadoValidacion:
    """
    Ejecuta toda la validación del archivo.
    """
    errores: List[str] = []
    advertencias: List[str] = []

    df = normalizar_columnas(df)

    ok_columnas, errores_columnas = validar_columnas(df)
    errores.extend(errores_columnas)

    if not ok_columnas:
        return ResultadoValidacion(
            es_valido=False,
            errores=errores,
            advertencias=advertencias,
            dataframe=df,
        )

    df, errores_fecha = convertir_timestamp(df)
    errores.extend(errores_fecha)

    df, errores_numericos, advertencias_numericas = convertir_numericas(df)
    errores.extend(errores_numericos)
    advertencias.extend(advertencias_numericas)

    if errores:
        return ResultadoValidacion(
            es_valido=False,
            errores=errores,
            advertencias=advertencias,
            dataframe=df,
        )

    advertencias.extend(validar_continuidad_minutal(df))
    advertencias.extend(validar_rangos_basicos(df))

    # Ordenamos por tiempo
    df = df.sort_values("timestamp").reset_index(drop=True)

    return ResultadoValidacion(
        es_valido=True,
        errores=errores,
        advertencias=advertencias,
        dataframe=df,
    )