# Plan architektury aplikacji: Treningowy Asystent Kolarza

## 1. Cel dokumentu

Ten dokument opisuje docelową architekturę aplikacji „Treningowy Asystent Kolarza”, zakres MVP oraz plan dalszej rozbudowy. Celem jest przygotowanie spójnej bazy projektowej dla backendu, frontendu, bazy danych i przyszłej warstwy AI.

---

## 2. Cel biznesowy i produktowy

Aplikacja ma wspierać kolarza w codziennym treningu poprzez:

- tworzenie i utrzymywanie profilu sportowca,
- import rzeczywistych treningów z plików `.FIT`,
- analizę obciążeń i intensywności,
- planowanie jednostek treningowych w kalendarzu,
- przygotowanie danych pod moduł AI do rekomendacji planu.

### 2.1 Główne korzyści dla użytkownika

- Jedno miejsce do monitorowania obciążeń treningowych.
- Automatyzacja analizy po imporcie treningu.
- Lepsza kontrola progresu dzięki historii i planowi.
- Gotowość do personalizacji planów przez AI w kolejnych etapach.

---

## 3. Zakres funkcjonalny

## 3.1 Moduł: Profil kolarza

### Cel
Dostarczenie parametrów bazowych do wyliczeń i planowania.

### Dane MVP

- FTP (`ftp_watts`)
- Waga (`weight_kg`)
- HR max (`hr_max`)
- HR progowy (`hr_threshold`)

### Dane rozszerzone

- Poziom doświadczenia (`beginner/intermediate/advanced`)
- Dostępny czas treningowy (h/tydzień)
- Cele (np. poprawa FTP, przygotowanie do wyścigu)
- Ograniczenia zdrowotne / preferencje treningowe

### Operacje

- Utworzenie profilu
- Edycja profilu
- Walidacja zakresów wartości
- Wersjonowanie (opcjonalnie, etap późniejszy)

---

## 3.2 Moduł: Import treningów `.FIT`

### Cel
Wczytanie realnych danych treningowych i zapis strukturalny w bazie.

### Źródła plików

- Garmin
- Zwift
- Wahoo
- Inne platformy zgodne z `.FIT`

### Zakres ekstrakcji

- Czas trwania
- Dystans
- Prędkość średnia/maksymalna
- Moc: średnia, NP
- Tętno: średnie/maksymalne
- Kadencja: średnia/maksymalna

### Biblioteki (Python)

- `fitparse`
- `fitdecode`

### Logika po imporcie

1. Upload pliku
2. Parsowanie rekordów
3. Wyliczenie metryk (`NP`, `IF`, `TSS`)
4. Zapis nagłówka treningu do `workouts`
5. Opcjonalny zapis próbek do `workout_samples`

---

## 3.3 Moduł: Analiza treningów

### Cel
Standaryzacja obliczeń obciążenia i intensywności.

### Metryki

- **NP (Normalized Power)** – znormalizowana moc wysiłku
- **IF (Intensity Factor)** – relacja intensywności do FTP
- **TSS (Training Stress Score)** – wskaźnik obciążenia treningowego
- Rozkład czasu w strefach mocy i HR

### Uwagi implementacyjne

- Obliczenia wykonywane po imporcie oraz przy ręcznej edycji danych.
- Wzory oparte o standardowe podejście FTP-based.
- Warto dodać testy jednostkowe dla algorytmów metryk.

---

## 3.4 Moduł: Kalendarz i planowanie

### Cel
Połączenie danych wykonanych i planowanych treningów w jednym widoku.

### Funkcje MVP

- Widok tygodniowy/miesięczny
- Dodawanie planowanego treningu ręcznie
- Podgląd wykonanych treningów
- Oznaczanie kolorami typu/strefy treningu

### Frontend

- React
- FullCalendar

### Backend API

- `POST /import-fit` – import pliku `.FIT`
- `GET /workouts` – lista treningów wykonanych
- `GET /calendar` – dane kalendarza
- `POST /plan-workout` – dodanie treningu planowanego

### Rozszerzenia (po MVP)

- Edycja/usuwanie planu
- Powtarzalne jednostki (template)
- Filtry po typie i strefie

---

## 3.5 Moduł: AI (etap docelowy)

### Cel
Generowanie spersonalizowanych planów i rekomendacji treningowych.

### Wejście do AI

- Parametry profilu (FTP, HR, waga)
- Dostępność dni i godzin treningowych
- Historia obciążeń (`TSS`, `IF`, strefy)
- Cele i ograniczenia

### Wyjście z AI

- Plan tygodniowy/miesięczny
- Sugestie zmian objętości/intensywności
- Notatki trenerskie i ostrzeżenia

### Integracja

- Moduł AI jako osobna warstwa backendowa
- Integracja przez REST z dostawcą modelu
- Start od darmowych tierów: Gemini API / OpenRouter

---

## 4. Architektura techniczna

## 4.1 Backend (Flask)

### Odpowiedzialności

- Upload i walidacja plików `.FIT`
- Parsowanie i transformacja danych
- Obliczanie metryk treningowych
- Udostępnianie REST API
- Orkiestracja planowania i integracji AI

### Proponowana struktura modułów

- `api/` – endpointy REST
- `services/` – logika domenowa (fit import, metrics, planning, ai)
- `repositories/` – dostęp do bazy
- `models/` – encje i schematy
- `utils/` – funkcje pomocnicze

---

## 4.2 Frontend (React)

### Widoki

- Onboarding/profil sportowca
- Kalendarz treningowy
- Lista treningów + szczegóły
- Formularz planowania treningu

### Zasady UI

- Czytelny podział: plan vs wykonanie
- Szybkie dodawanie jednostek
- Widoczne metryki kluczowe (TSS/IF/NP)

---

## 4.3 Baza danych (SQLite/PostgreSQL)

### Tabele główne

- `users`
- `athlete_profile`
- `workouts`
- `planned_workouts`
- `workout_samples` (opcjonalnie)

### Wstępny schemat logiczny (uproszczony)

- `users (id, email, password_hash, created_at)`
- `athlete_profile (id, user_id, ftp_watts, weight_kg, hr_max, hr_threshold, experience_level, weekly_hours, goals, limitations, updated_at)`
- `workouts (id, user_id, source, started_at, duration_sec, distance_m, avg_power, np_power, if_value, tss, avg_hr, max_hr, avg_cadence, created_at)`
- `planned_workouts (id, user_id, planned_date, type, duration_sec, target_zone, notes, created_at)`
- `workout_samples (id, workout_id, ts_offset_sec, power, hr, cadence, speed)`

---

## 4.4 Warstwa AI

### Odpowiedzialności

- Przygotowanie danych wejściowych (feature engineering)
- Budowa promptów systemowych i użytkownika
- Walidacja odpowiedzi modelu
- Translacja odpowiedzi do struktury planu i zapis do DB

### Zasady bezpieczeństwa

- Ograniczenie dostępu modelu do minimum danych
- Maskowanie danych wrażliwych
- Logowanie wejścia/wyjścia modułu AI (z anonimizacją)

---

## 5. Przepływ danych (end-to-end)

1. **Onboarding** – użytkownik uzupełnia profil.
2. **Import FIT** – plik trafia do backendu.
3. **Przetwarzanie** – parser wyciąga dane i liczy metryki.
4. **Persistencja** – zapis do `workouts` (+ opcjonalnie próbki).
5. **Prezentacja** – frontend pokazuje dane na liście i w kalendarzu.
6. **Planowanie ręczne** – użytkownik dodaje jednostki do planu.
7. **AI (opcjonalnie)** – generuje propozycję planu i zapisuje do DB.

---

## 6. API MVP – propozycja kontraktów

### `POST /import-fit`

- multipart: `file`
- response: status importu + podsumowanie metryk

### `GET /workouts`

- query: zakres dat, paginacja
- response: lista treningów wykonanych

### `GET /calendar`

- query: `from`, `to`
- response: zdarzenia planowane + wykonane

### `POST /plan-workout`

- body: data, typ, czas, strefa, notatki
- response: utworzony rekord planu

---

## 7. Walidacje i reguły domenowe

- FTP > 0
- Waga > 0
- HR max > HR progowy
- Trening nie może mieć ujemnego czasu/dystansu
- Jeden trening importowany raz (hash pliku lub identyfikator sesji)

---

## 8. Niefunkcjonalne wymagania MVP

- Czas importu pojedynczego pliku FIT: docelowo < 3 sek (typowy plik)
- Stabilność obliczeń metryk (deterministyczność)
- Prosty mechanizm logowania błędów i monitoringu
- Możliwość migracji z SQLite do PostgreSQL bez zmian w logice domenowej

---

## 9. Roadmapa wdrożenia

## Faza 1 (MVP)

1. Profil kolarza
2. Import `.FIT`
3. Metryki: NP, IF, TSS, strefy
4. Kalendarz podstawowy
5. Manualne planowanie

## Faza 2

1. Rozszerzone statystyki i trendy
2. Lepsze zarządzanie planem (edycja, kopiowanie tygodni)
3. Integracja z zewnętrznymi źródłami danych

## Faza 3 (AI)

1. Generator planu tygodniowego
2. Rekomendacje obciążenia
3. Adaptacja planu na podstawie historii i realizacji

---

## 10. Ryzyka projektowe i mitigacje

- **Jakość danych FIT** → fallback parser + walidacje.
- **Różnice źródeł (Garmin/Zwift/Wahoo)** → warstwa normalizacji danych.
- **Niewłaściwe rekomendacje AI** → ograniczenia regułowe i review użytkownika.
- **Skalowanie analizy próbek** → zapis próbek opcjonalny lub agregacje.

---

## 11. Podsumowanie

Dokument definiuje kompletny plan architektury dla pierwszej wersji aplikacji oraz kierunek dalszego rozwoju. Priorytetem jest dostarczenie solidnego MVP opartego o profil sportowca, import FIT, analizę metryk i kalendarz planowania. Warstwa AI jest projektowana jako naturalne rozszerzenie, które można wdrożyć po ustabilizowaniu fundamentów danych i logiki domenowej.
