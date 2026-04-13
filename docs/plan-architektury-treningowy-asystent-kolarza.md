# Plan architektury aplikacji: Treningowy Asystent Kolarza

> Uzupełnienie techniczne i playbook dla AI Agenta znajduje się w pliku `docs/specyfikacja-techniczna-i-playbook-agenta-ai.md`.

## 1. Cel dokumentu

**Założenie MVP: aplikacja jednoosobowa (single-athlete), bez rejestracji i logowania użytkowników.**

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
- Preferowane dni treningowe (`preferred_training_days`)
- Maksymalny czas jazdy na dzień (`max_ride_time_per_day_min`)
- Preferencja środowiska treningu (`indoor_vs_outdoor_preference`)

### Operacje

- Utworzenie profilu
- Edycja profilu
- Walidacja zakresów wartości
- Wersjonowanie (opcjonalnie, etap późniejszy)

### 3.1b Moduł: Test FTP (MVP)

### Cel
Wyznaczenie i aktualizacja FTP na bazie ustandaryzowanego testu.

### Obsługiwane protokoły
- Ramp test (preferowany)
- Protokół 20-minutowy

### Dane wejściowe
- Seria próbek mocy z importu FIT (`workout_samples`)
- Ręcznie podany wynik testu

### Dane wyjściowe
- Sugerowane FTP
- Aktualizacja profilu sportowca (`ftp_watts`)

### Status
- Faza 1 MVP

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
5. Wymagany zapis próbek do `workout_samples` (pod Power Curve i test FTP)

---

## 3.3 Moduł: Analiza treningów

### Cel
Standaryzacja obliczeń obciążenia i intensywności.

### Metryki

- **NP (Normalized Power)** – znormalizowana moc wysiłku
- **IF (Intensity Factor)** – relacja intensywności do FTP
- **TSS (Training Stress Score)** – wskaźnik obciążenia treningowego
- **ATL (Acute Training Load)** – średnia obciążenia z 7 dni
- **CTL (Chronic Training Load)** – średnia obciążenia z 42 dni
- **TSB (Training Stress Balance)** – bilans świeżości, liczony jako `TSB = CTL - ATL`
- Rozkład czasu w strefach mocy i HR

### Uwagi implementacyjne

- Obliczenia wykonywane po imporcie oraz przy ręcznej edycji danych.
- Wzory oparte o standardowe podejście FTP-based.
- Warstwa backendowa musi liczyć `TSS`, `ATL`, `CTL`, `TSB` deterministycznie (bez udziału AI).
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
- Status treningu: `planned`, `completed`, `skipped`, `moved`
- Drag & drop do przenoszenia jednostek w kalendarzu
- Auto-adjust planu po pominięciu treningu (przesunięcie jednostek)

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
- Żywy kalendarz z adaptacją planu tydzień-po-tygodniu (Garmin-level UX)

---

## 3.5 Moduł: AI (etap docelowy)

### Cel
Generowanie spersonalizowanych planów i rekomendacji treningowych.

### Granica odpowiedzialności: Hybrid AI (bardzo ważne)

Najlepszy efekt daje podział odpowiedzialności:

- **Backend deterministyczny (reguły + wzory):**
  - `TSS`
  - `CTL/ATL/TSB`
  - strefy treningowe
  - monitorowanie progresu metryk
- **Warstwa AI (decyzje planistyczne):**
  - co trenować
  - ile godzin trenować
  - jakie interwały zaproponować

### Wejście do AI

- Parametry profilu (FTP, HR, waga)
- Dostępność dni i godzin treningowych
- Historia obciążeń (`TSS`, `IF`, strefy)
- Cele i ograniczenia

### Wyjście z AI

- Plan tygodniowy/miesięczny
- Sugestie zmian objętości/intensywności
- Notatki trenerskie i ostrzeżenia
- Decyzje adaptacyjne po niewykonanych treningach (priorytety i kolejność przesunięć)

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
- Żywy status treningu (`planned/completed/skipped/moved`)
- Intuicyjny drag & drop między dniami
- Widoczna informacja o automatycznych przesunięciach planu

---

## 4.3 Baza danych (SQLite/PostgreSQL)

> Dla single-athlete deployment na home server dopuszczalne i rekomendowane jest SQLite także produkcyjnie. PostgreSQL zalecany tylko przy przejściu na multi-user.

### Tabele główne

- `athlete_profile`
- `workouts`
- `planned_workouts`
- `workout_samples` (wymagane od Fazy 1)
- `daily_load_metrics` (agregaty obciążenia dziennego)
- `workout_insights` (komentarze rule-based i AI)

### Wstępny schemat logiczny (uproszczony)

- `athlete_profile (id, ftp_watts, weight_kg, hr_max, hr_threshold, experience_level, weekly_hours, goals, limitations, preferred_training_days, max_ride_time_per_day_min, indoor_vs_outdoor_preference, updated_at)`
- `workouts (id, source, started_at, duration_sec, distance_m, avg_power, np_power, if_value, tss, avg_hr, max_hr, avg_cadence, created_at)`
- `planned_workouts (id, planned_date, type, duration_sec, target_zone, status, moved_from_date, notes, created_at, updated_at)`
- `workout_samples (id, workout_id, ts_offset_sec, power, hr, cadence, speed)`
- `daily_load_metrics (id, metric_date, tss_day, atl_7d, ctl_42d, tsb, created_at)`
- `workout_insights (id, workout_id, insight_type, severity, message, generated_by, created_at)`

---

## 4.4 Warstwa AI

### Odpowiedzialności

- Przygotowanie danych wejściowych (feature engineering)
- Budowa promptów systemowych i użytkownika
- Walidacja odpowiedzi modelu
- Translacja odpowiedzi do struktury planu i zapis do DB
- Generowanie sugestii adaptacyjnych po zmianach realizacji planu
- Generowanie komentarzy trenerskich (insights)

### Zasady bezpieczeństwa

- Ograniczenie dostępu modelu do minimum danych
- Maskowanie danych wrażliwych
- Logowanie wejścia/wyjścia modułu AI (z anonimizacją)

---

## 5. Przepływ danych (end-to-end)

1. **Onboarding** – użytkownik uzupełnia profil.
2. **Import FIT** – plik trafia do backendu.
3. **Przetwarzanie** – parser wyciąga dane i liczy metryki.
4. **Persistencja** – zapis do `workouts` + wymagany zapis próbek do `workout_samples`.
5. **Prezentacja** – frontend pokazuje dane na liście i w kalendarzu.
6. **Planowanie ręczne** – użytkownik dodaje jednostki do planu.
7. **Status realizacji** – trening otrzymuje status (`completed`, `skipped`, `moved`).
8. **Adaptacja planu** – silnik planowania przesuwa zaległe jednostki i aktualizuje kalendarz.
9. **AI (opcjonalnie)** – generuje propozycję planu i korekty mikrocyklu.
10. **Insights** – system generuje komentarze rule-based i/lub AI.

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

### `PATCH /planned-workouts/{id}/status`

- body: `status` (`planned|completed|skipped|moved`)
- response: zaktualizowany rekord + ewentualne zmiany zależne

### `POST /calendar/move-workout`

- body: `planned_workout_id`, `from_date`, `to_date`
- response: zaktualizowany trening + lista przesuniętych jednostek

### `POST /adaptive/recalculate-week`

- body: `week_start`, `strategy`
- response: nowy układ tygodnia po auto-adjust

### `GET /metrics/load`

- query: zakres dat
- response: serie `TSS`, `ATL`, `CTL`, `TSB`

### `GET /insights`

- query: zakres dat, poziom severity
- response: lista komentarzy trenerskich

---

## 7. Walidacje i reguły domenowe

- FTP > 0
- Waga > 0
- HR max > HR progowy
- Trening nie może mieć ujemnego czasu/dystansu
- Jeden trening importowany raz (hash pliku lub identyfikator sesji)
- Status treningu musi należeć do: `planned`, `completed`, `skipped`, `moved`
- Przy statusie `moved` pole `moved_from_date` jest wymagane
- Auto-adjust nie może przekroczyć `max_ride_time_per_day_min`
- Adaptacja tygodnia musi respektować `preferred_training_days` i preferencję `indoor/outdoor`

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
2. Moduł FTP test (ramp test + 20-min)
3. Import `.FIT` z wymaganym zapisem `workout_samples`
4. Metryki: NP, IF, TSS, strefy
5. Kalendarz podstawowy
6. Manualne planowanie

## Faza 2

1. Rozszerzone statystyki i trendy (`TSS/week`, `CTL/ATL/TSB`)
2. Lepsze zarządzanie planem (statusy, drag&drop, kopiowanie tygodni)
3. Rule-based insights (np. przeciążenie, jakość Z2, progres VO2max)
4. Integracja z zewnętrznymi źródłami danych

## Faza 3 (AI)

1. Generator planu tygodniowego
2. Rekomendacje obciążenia
3. Adaptacja planu na podstawie historii i realizacji
4. Adaptive training (jak TrainerRoad / AITrainer): brak wykonania kluczowej jednostki przesuwa plan automatycznie

---

## 12. Smart Calendar i Adaptive Training (docelowy wyróżnik)

### 12.1 Smart Calendar

Zakładamy przejście z „kalendarza statycznego” do „żywego kalendarza”:

- trening ma status (`planned/completed/skipped/moved`),
- przeciąganie jednostek (drag&drop) uruchamia walidację obciążenia,
- brak realizacji treningu uruchamia auto-adjust całego tygodnia.

### 12.2 Mechanika adaptive training

Silnik adaptacyjny działa sekwencyjnie:

1. wykrycie pominiętej jednostki (np. VO2max),
2. próba przeniesienia na najbliższy możliwy dzień,
3. przesunięcie pozostałych jednostek tygodnia,
4. kontrola limitów (`max_ride_time_per_day`, preferencje dni),
5. publikacja nowej wersji mikrocyklu.

### 12.3 Przykład scenariusza

- Użytkownik nie robi treningu VO2max we wtorek.
- System przenosi VO2max na środę.
- Trening środowy jest przesuwany na czwartek.
- Reszta tygodnia zostaje przepięta tak, aby utrzymać logikę obciążenia.

---

## 13. Analityka i wykresy (obszar przewagi konkurencyjnej)

### Wykresy jednostki treningowej

- Power vs time
- HR vs power

### Wykresy długoterminowe

- `TSS / tydzień`
- `CTL / ATL / TSB`

### Killer feature: Power Curve

Wymagane punkty odniesienia:

- 5s
- 1min
- 5min
- 20min

Interpretacja dla użytkownika:

- czy poprawia potencjał VO2max,
- czy FTP rośnie w czasie.

---

## 14. Real coaching feel (insights)

Na start wdrażamy hybrydę:

- **Rule-based insights (MVP+)**:
  - „Twoje Z2 jest za wysokie HR”
  - „Przetrenowanie w ostatnich 5 dniach”
  - „Dobry progres VO2max”
- **AI insights (etap późniejszy)**:
  - bardziej kontekstowe podsumowania mikro/makrocyklu.

---

## 15. Ryzyka projektowe i mitigacje

- **Jakość danych FIT** → fallback parser + walidacje.
- **Różnice źródeł (Garmin/Zwift/Wahoo)** → warstwa normalizacji danych.
- **Niewłaściwe rekomendacje AI** → ograniczenia regułowe i review użytkownika.
- **Skalowanie analizy próbek** → zapis pełnych próbek wymagany (Power Curve / FTP test); mitigacja przez partycjonowanie, kompresję i retencję.

---

## 16. Podsumowanie

Dokument definiuje kompletny plan architektury dla pierwszej wersji aplikacji oraz kierunek dalszego rozwoju. Priorytetem jest dostarczenie solidnego MVP opartego o profil sportowca, import FIT, analizę metryk i kalendarz planowania. Warstwa AI jest projektowana jako naturalne rozszerzenie, które można wdrożyć po ustabilizowaniu fundamentów danych i logiki domenowej.

---

## Changelog
- [2026-04-13] – korekty po review: ujednolicenie stacku (Flask), samples jako wymagane, kontekst SQLite, dodanie modułu FTP test.
