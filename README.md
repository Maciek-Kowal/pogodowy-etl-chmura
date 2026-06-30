# Zautomatyzowany Pipeline ETL: Dane Pogodowe

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)](https://pandas.pydata.org/)
[![Google BigQuery](https://img.shields.io/badge/Google_Cloud-BigQuery-4285F4.svg)](https://cloud.google.com/bigquery)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automation-2088FF.svg)](https://github.com/features/actions)

## Podsumowanie Projektu
Projekt to w pełni zautomatyzowany rurociąg danych realizujący proces ETL. Skrypt codziennie pobiera aktualne dane pogodowe dla wybranych polskich miast, przetwarza je do postaci analitycznej i ładuje do chmurowej hurtowni danych (Google BigQuery). 

Głównym celem projektu jest demonstracja umiejętności wyjścia poza analizę statycznych plików CSV i budowa bezobsługowego systemu pracującego na "żywych" danych, w architekturze chmurowej, z wykorzystaniem standardów branżowych (GCP, CI/CD).

## Architektura Rozwiązania i Technologie

Proces został podzielony na trzy odizolowane logicznie etapy, kontrolowane przez chmurowy harmonogram:

1. **Ekstrakcja**
   * **Źródło:** [Open-Meteo API](https://open-meteo.com/) (Darmowe, publiczne REST API).
   * **Narzędzia:** Python (`requests`).
   * **Działanie:** Wykonanie zapytań HTTP GET na podstawie zdefiniowanego słownika współrzędnych geograficznych (Katowice, Warszawa, Gniezno, Kołobrzeg). Pobranie zagnieżdżonych struktur JSON.

2. **Transformacja**
   * **Narzędzia:** Python (`pandas`).
   * **Działanie:** Spłaszczenie zagnieżdżonych struktur JSON (`json_normalize`), rzutowanie typów danych (np. konwersja ciągów znaków na obiekty `datetime`), czyszczenie oraz standaryzacja nazw kolumn do formatu bazodanowego.

3. **Ładowanie**
   * **Cel:** Google BigQuery.
   * **Narzędzia:** Python (`pandas-gbq`, `google-auth`).
   * **Działanie:** Bezpieczna autoryzacja za pomocą Google Service Account Key. System z dopisywaniem danych – nowe pomiary są codziennie dodawane do tabeli analitycznej, zachowując pełną historię do późniejszych analiz i wizualizacji.

4. **Automatyzacja**
   * **Narzędzia:** GitHub Actions.
   * **Działanie:** Repozytorium zawiera zdefiniowany przepływ pracy (Workflow w formacie YAML), który inicjuje proces uruchamiania wirtualnego serwera (Ubuntu), instaluje zależności i odpala skrypt główny punktualnie o 6:00 UTC za pomocą harmonogramu CRON.

## Wartość Biznesowa
* **Bezobsługowość:** Całkowite wyeliminowanie czynnika ludzkiego z procesu gromadzenia danych.
* **Skalowalność:** Dodanie nowych miast lub metryk sprowadza się do aktualizacji jednego słownika konfiguracyjnego w kodzie.
* **Bezpieczeństwo:** Uwierzytelnianie z GCP odbywa się przy pomocy bezpiecznych kluczy asymetrycznych ukrytych w sekretach GitHuba, zabezpieczając infrastrukturę przed wyciekiem.

## Struktura Repozytorium

* `main.py` - Główny skrypt aplikacyjny zawierający logikę ETL.
* `requirements.txt` - Lista zależności środowiska Python.
* `.github/workflows/etl.yml` - Konfiguracja potoku automatyzacji dla GitHub Actions.
* `.gitignore` - Wykluczenia plików środowiskowych i kluczy autoryzacyjnych.

## Uruchomienie Lokalne

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/Maciek-Kowal/pogodowy-etl-chmura.git
   ```
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```

3. Umieść klucz Service Account z Google Cloud (plik `.json`) w katalogu głównym i nazwij go `gcp-klucz.json` (plik jest ignorowany przez `.gitignore`).

4. W pliku `main.py` podmień zmienną `ID_PROJEKTU` na swoje ID z GCP.

5. Uruchom proces:
   ```bash
   python main.py
   ```