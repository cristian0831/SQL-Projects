# Open-Meteo API — Reference Notes

Documentation for the API consumed by [weather_scraper.py](weather_scraper.py).

## Endpoint used

```
GET https://api.open-meteo.com/v1/forecast
```

Weather forecast API from [Open-Meteo](https://open-meteo.com/), free and requiring no API key for non-commercial use.

## Parameters used in this project

| Parameter | Value in the script | Description |
|---|---|---|
| `latitude` / `longitude` | Coordinates of each city (`CITIES`) | Forecast location. Accepts a single pair or comma-separated lists to query multiple locations in a single call. |
| `daily` | `temperature_2m_max` | Daily variable to return. It's a comma-separated list; multiple variables can be requested at once (see below). |
| `timezone` | `America/Bogota` | Adjusts the returned dates/times to the specified timezone instead of UTC. |
| `forecast_days` | `7` | Number of forecast days ahead (default 7, maximum 16). |

## Other available `daily` variables

The API offers many more daily-aggregated variables that could be added to the `daily` parameter:

- `temperature_2m_max`, `temperature_2m_min`
- `apparent_temperature_max`, `apparent_temperature_min`
- `precipitation_sum`, `rain_sum`, `snowfall_sum`
- `precipitation_hours`, `precipitation_probability_max`
- `windspeed_10m_max`, `windgusts_10m_max`, `winddirection_10m_dominant`
- `sunrise`, `sunset`, `uv_index_max`
- `shortwave_radiation_sum`, `et0_fao_evapotranspiration`

## Other relevant API parameters

- `hourly`: hourly variables (temperature, humidity, wind, pressure, etc.) instead of daily summaries.
- `current` / `current_weather=true`: instantaneous current conditions.
- `past_days`: includes recent historical days alongside the forecast.
- `start_date` / `end_date`: specific date range (`YYYY-MM-DD` format), an alternative to `forecast_days`.
- `temperature_unit`, `windspeed_unit`, `precipitation_unit`: units of measurement (default Celsius, km/h, mm).
- `models`: lets you choose the weather model (e.g. ECMWF, GFS, ICON) instead of the default combined model.

## Response format

The response is JSON with this structure relevant to `save()`:

```json
{
  "daily": {
    "time": ["2026-07-22", "2026-07-23", "..."],
    "temperature_2m_max": [24.1, 23.8, "..."]
  }
}
```

The arrays inside `daily` are aligned by index: the date at `time[i]` corresponds to the value at `temperature_2m_max[i]`.

## Limits and best practices

- No authentication or API key required for the free tier.
- Fair-use limit (~10,000 calls/day) for non-commercial use; a commercial tier with an API key exists for higher volume.
- It's recommended to handle retries with backoff on 429/5xx errors, as implemented by `fetch()` in the script.
