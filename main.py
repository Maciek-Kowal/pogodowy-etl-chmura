import requests
import pandas as pd
from google.oauth2 import service_account
import pandas_gbq

LOKALIZACJE = {
    "Katowice": (50.2584, 19.0275),
    "Warszawa": (52.2298, 21.0118),
    "Gniezno": (52.5348, 17.5826),
    "Kołobrzeg": (54.1757, 15.5833)
}

ID_PROJEKTU = "pogoda-etl"
TABELA_DOCELOWA = "dane_pogodowe.pomiary_codzienne"


def pobierz_dane_pogodowe(konfiguracja_miast):
    print("Rozpoczynam pobieranie danych...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": [coords[0] for coords in konfiguracja_miast.values()],
        "longitude": [coords[1] for coords in konfiguracja_miast.values()],
        "current_weather": True,
        "timezone": "Europe/Warsaw"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json(), list(konfiguracja_miast.keys())
    return None, None


def transformuj_dane(dane_json, nazwy_miast):
    print("Rozpoczynam transformację danych...")
    df = pd.json_normalize(dane_json)
    df['miasto'] = nazwy_miast
    df = df[['miasto', 'current_weather.time', 'current_weather.temperature', 'current_weather.windspeed']]
    df = df.rename(columns={
        'current_weather.time': 'data_pomiaru',
        'current_weather.temperature': 'temperatura_c',
        'current_weather.windspeed': 'wiatr_kmh'
    })
    df['data_pomiaru'] = pd.to_datetime(df['data_pomiaru'])
    return df


def zaladuj_do_bigquery(df, projekt_id, tabela):
    print("Rozpoczynam ładowanie danych do Google BigQuery...")
    dane_uwierzytelniajace = service_account.Credentials.from_service_account_file('gcp-klucz.json')

    pandas_gbq.to_gbq(
        df,
        destination_table=tabela,
        project_id=projekt_id,
        credentials=dane_uwierzytelniajace,
        if_exists='append'
    )
    print("Sukces! Dane wylądowały w chmurze.")


if __name__ == "__main__":
    surowe_dane, miasta = pobierz_dane_pogodowe(LOKALIZACJE)

    if surowe_dane:
        czyste_dane = transformuj_dane(surowe_dane, miasta)
        zaladuj_do_bigquery(czyste_dane, ID_PROJEKTU, TABELA_DOCELOWA)