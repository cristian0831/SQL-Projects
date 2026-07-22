# Open-Meteo API — Notas de referencia

Documentación de la API que consume [weather_scraper.py](weather_scraper.py).

## Endpoint utilizado

```
GET https://api.open-meteo.com/v1/forecast
```

API de pronóstico meteorológico de [Open-Meteo](https://open-meteo.com/), gratuita y sin necesidad de API key para uso no comercial.

## Parámetros usados en este proyecto

| Parámetro | Valor en el script | Descripción |
|---|---|---|
| `latitude` / `longitude` | Coordenadas de cada ciudad (`CIUDADES`) | Ubicación del pronóstico. Acepta un solo par o listas separadas por coma para consultar varias ubicaciones en una sola llamada. |
| `daily` | `temperature_2m_max` | Variable diaria a devolver. Es una lista separada por comas; se pueden pedir varias variables a la vez (ver más abajo). |
| `timezone` | `America/Bogota` | Ajusta las fechas/horas devueltas a la zona horaria indicada en vez de UTC. |
| `forecast_days` | `7` | Cantidad de días de pronóstico a futuro (por defecto 7, máximo 16). |

## Otras variables `daily` disponibles

La API ofrece muchas más variables agregadas por día que se podrían sumar al parámetro `daily`:

- `temperature_2m_max`, `temperature_2m_min`
- `apparent_temperature_max`, `apparent_temperature_min`
- `precipitation_sum`, `rain_sum`, `snowfall_sum`
- `precipitation_hours`, `precipitation_probability_max`
- `windspeed_10m_max`, `windgusts_10m_max`, `winddirection_10m_dominant`
- `sunrise`, `sunset`, `uv_index_max`
- `shortwave_radiation_sum`, `et0_fao_evapotranspiration`

## Otros parámetros relevantes de la API

- `hourly`: variables por hora (temperatura, humedad, viento, presión, etc.) en vez de resúmenes diarios.
- `current` / `current_weather=true`: condición actual instantánea.
- `past_days`: incluye días históricos recientes junto con el pronóstico.
- `start_date` / `end_date`: rango de fechas específico (formato `YYYY-MM-DD`), alternativa a `forecast_days`.
- `temperature_unit`, `windspeed_unit`, `precipitation_unit`: unidades de medida (por defecto Celsius, km/h, mm).
- `models`: permite elegir el modelo meteorológico (ej. ECMWF, GFS, ICON) en vez del modelo combinado por defecto.

## Formato de respuesta

La respuesta es JSON con esta estructura relevante para `guardar()`:

```json
{
  "daily": {
    "time": ["2026-07-22", "2026-07-23", "..."],
    "temperature_2m_max": [24.1, 23.8, "..."]
  }
}
```

Los arreglos dentro de `daily` están alineados por índice: la fecha en `time[i]` corresponde al valor en `temperature_2m_max[i]`.

## Límites y buenas prácticas

- No requiere autenticación ni API key para el tier gratuito.
- Límite de uso justo (~10,000 llamadas/día) para uso no comercial; existe un tier comercial con API key para mayor volumen.
- Se recomienda manejar reintentos con backoff ante errores 429/5xx, tal como implementa `fetch()` en el script.
