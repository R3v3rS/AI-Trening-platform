# Specyfikacja techniczna i playbook rozwoju (pod AI Agenta)

## 1. Cel dokumentu

Ten dokument jest **bazową specyfikacją wykonawczą** dla:

1. uruchomienia pierwszej działającej wersji aplikacji,
2. utrzymania spójności technologicznej przy kolejnych iteracjach,
3. prowadzenia rozwoju przez AI Agenta bez pomijania kluczowych elementów.

Dokument łączy trzy perspektywy: **architekturę**, **proces wytwórczy** i **reguły jakości**.

---

## Założenie bazowe: aplikacja jednoosobowa (single-athlete)

Na tym etapie aplikacja jest tworzona **dla jednej osoby**. Oznacza to:

- brak modułu rejestracji i logowania,
- brak wielodostępności i ról użytkowników,
- jedna konfiguracja profilu sportowca w aplikacji.

W przypadku przyszłego przejścia na multi-user należy to traktować jako osobny etap migracyjny.

---

## 2. Audyt obecnej dokumentacji (stan i korekty)

Dokument `plan-architektury-treningowy-asystent-kolarza.md` ma poprawnie opisany kierunek produktu (profil, import FIT, metryki, kalendarz, AI), ale wymaga doprecyzowania technicznego w obszarach:

- standardów API (wersjonowanie, format błędów, idempotencja),
- struktury repozytorium i kontraktów między modułami,
- wymagań środowiskowych (lokalnie/CI/prod),
- kryteriów „Definition of Done” dla funkcji,
- checklisty dla AI Agenta (co zawsze sprawdzać przed zmianą i po zmianie).

Wnioski: kierunek jest właściwy, ale do efektywnego developmentu potrzebny jest **operacyjny playbook** (poniżej).

---

## 3. Docelowy stos technologiczny (zalecenie)

> Celem jest szybki start MVP i bezpieczna ścieżka skalowania.

### 3.1 Backend

- **Python 3.12**
- **Flask** (jedyny i docelowy framework backendowy)
- **Pydantic v2** do walidacji kontraktów
- **SQLAlchemy 2.x** + **Alembic** do migracji
- **Celery/RQ** (opcjonalnie od fazy 2) do zadań asynchronicznych (np. cięższe przetwarzanie FIT)

Dlaczego:

- silna walidacja schematów,
- automatyczne OpenAPI,
- dobra ergonomia przy integracji z modułami AI.

### 3.2 Frontend

- **React + TypeScript**
- **Vite**
- **TanStack Query** (cache i synchronizacja danych API)
- **FullCalendar** (kalendarz treningowy)
- **Zod** do walidacji runtime po stronie UI

Dlaczego:

- przewidywalny przepływ danych,
- szybkie iteracje,
- łatwiejsze utrzymanie kontraktów z backendem.

### 3.3 Baza danych

- **MVP:** PostgreSQL 16 lub SQLite (w zależności od środowiska wdrożenia)
- **Produkcyjnie:** dla single-athlete deployment na home server dopuszczalne i rekomendowane jest SQLite; PostgreSQL zalecany przy przejściu na multi-user
- **Redis** (opcjonalnie) do kolejek/cache

Dlaczego:

- stabilność migracji,
- lepsza obsługa zapytań analitycznych,
- gotowość do skalowania bez przepisywania warstwy danych.

### 3.4 Import FIT i metryki

- Parser FIT: `fitdecode` (preferowany), `fitparse` jako fallback
- Obliczenia metryk: moduł domenowy backendu (deterministyczny, bez AI)
- Testy referencyjne dla NP/IF/TSS/CTL/ATL/TSB na stałych datasetach

### 3.5 Moduł AI

- Provider abstrakcyjny: `LLMProvider` (interfejs), implementacje np. OpenRouter / Gemini / OpenAI
- Wymuszony output JSON zgodny ze schematem
- Blokada publikacji planu, jeśli walidacja odpowiedzi modelu nie przejdzie

---

## 4. Struktura aplikacji (wersja początkowa, działająca)

Poniżej minimalna struktura repozytorium dla startu prac:

```text
.
├─ apps/
│  ├─ api/
│  │  ├─ src/
│  │  │  ├─ main.py
│  │  │  ├─ api/
│  │  │  │  ├─ v1/
│  │  │  │  │  ├─ health.py
│  │  │  │  │  ├─ profile.py
│  │  │  │  │  ├─ workouts.py
│  │  │  │  │  ├─ calendar.py
│  │  │  │  │  └─ import_fit.py
│  │  │  ├─ core/
│  │  │  │  ├─ config.py
│  │  │  │  └─ logging.py
│  │  │  ├─ domain/
│  │  │  │  ├─ metrics/
│  │  │  │  ├─ planning/
│  │  │  │  └─ insights/
│  │  │  ├─ infrastructure/
│  │  │  │  ├─ db/
│  │  │  │  ├─ repositories/
│  │  │  │  └─ fit/
│  │  │  └─ schemas/
│  │  ├─ tests/
│  │  └─ alembic/
│  └─ web/
│     ├─ src/
│     │  ├─ pages/
│     │  ├─ features/
│     │  ├─ components/
│     │  ├─ lib/api/
│     │  └─ types/
│     └─ tests/
├─ packages/
│  └─ shared-contracts/
├─ docs/
│  ├─ plan-architektury-treningowy-asystent-kolarza.md
│  ├─ specyfikacja-techniczna-i-playbook-agenta-ai.md
│  ├─ adr/
│  └─ runbooks/
├─ scripts/
├─ docker-compose.yml
└─ README.md
```

---

## 5. MVP techniczne – co musi działać

### 5.1 Zakres „działającej wersji początkowej”

1. Uzupełnienie i edycja profilu sportowca (jedna osoba).
2. Import pliku FIT i zapis treningu do DB.
3. Wyliczenie i prezentacja: `NP`, `IF`, `TSS`.
4. Widok kalendarza z treningami wykonanymi i planowanymi.
5. Dodanie planowanego treningu i zmiana statusu (`planned/completed/skipped/moved`).
6. Endpoint healthcheck + podstawowe logowanie błędów.

### 5.2 Minimalne API (v1)

- `GET /api/v1/health`
- `GET /api/v1/profile`
- `PUT /api/v1/profile`
- `POST /api/v1/workouts/import-fit`
- `GET /api/v1/workouts`
- `GET /api/v1/calendar?from=...&to=...`
- `POST /api/v1/planned-workouts`
- `PATCH /api/v1/planned-workouts/{id}/status`

### 5.3 Minimalny model danych (MVP)

- `athlete_profiles`
- `workouts`
- `planned_workouts`
- `daily_load_metrics`

`workout_samples` są wymagane od Fazy 1 (pod Power Curve), natomiast `workout_insights` mogą wejść w kolejnym kroku.

---

## 6. Zasady architektoniczne (niełamalne)

1. **Deterministyczna domena treningowa:** metryki obciążenia liczy backend, nie model AI.
2. **AI nie zapisuje bez walidacji:** każda odpowiedź AI musi przejść walidator schematu.
3. **Wersjonowanie API:** wszystkie endpointy w `/api/v1/...`.
4. **Idempotencja importu FIT:** ten sam plik nie może tworzyć duplikatu treningu.
5. **Jawne kontrakty:** request/response wyłącznie przez schematy.
6. **Migracje obowiązkowe:** żadnych ręcznych zmian w produkcyjnej bazie danych.
7. **Testy dla logiki domenowej:** każda zmiana w metrykach wymaga testu regresji.

---

## 7. Workflow rozwoju prowadzony przez AI Agenta

## 7.1 Pętla pracy (obowiązkowa)

1. Odczytaj wymaganie i przypisz je do modułu (`profile/import/metrics/calendar/ai`).
2. Sprawdź wpływ na kontrakty API i DB.
3. Wprowadź zmianę minimalnym zakresem.
4. Uzupełnij testy (jednostkowe i/lub integracyjne).
5. Uruchom checklistę jakości.
6. Zaktualizuj dokumentację (`docs/` + changelog/ADR jeśli decyzja architektoniczna).

## 7.2 Checklist przed merge

- [ ] Kod przechodzi lint/format.
- [ ] Testy przechodzą lokalnie i w CI.
- [ ] Zmiany API mają zaktualizowany kontrakt OpenAPI.
- [ ] Zmiany DB mają migrację i opis rollback.
- [ ] Uzupełniono dokumentację funkcjonalną/techniczną.
- [ ] Brak naruszeń zasad z sekcji 6.

## 7.3 Definition of Done dla każdej funkcji

Funkcja jest ukończona, gdy:

- działa end-to-end,
- ma walidacje wejścia i sensowne błędy,
- ma testy dla scenariuszy pozytywnych i krytycznych negatywnych,
- jest opisana w dokumentacji użytkowej i technicznej,
- nie obniża jakości istniejących modułów.

---

## 8. Plan rozwoju kompatybilny wstecz

### Faza 1 (MVP)

- Profil + import FIT + podstawowe metryki + kalendarz + statusy + moduł FTP test (ramp test + 20-min) + wymagane `workout_samples`.

### Faza 2 (stabilizacja i jakość)

- CTL/ATL/TSB i wykresy trendów,
- auto-adjust tygodnia po `skipped/moved`,
- rule-based insights,
- lepsza obsługa błędów parserów FIT.

### Faza 3 (AI planowanie)

- generator planu tygodniowego,
- adaptacja planu po realizacji,
- komentarze trenerskie AI,
- monitoring jakości rekomendacji.

Każda faza rozszerza poprzednią i nie łamie kontraktów API v1 (nowe pola tylko jako opcjonalne, lub nowe endpointy).

---

## 9. Rejestr decyzji (ADR) – co utrzymywać

Każda istotna decyzja techniczna powinna trafić do `docs/adr/` z datą i skutkami.

Minimalny szablon ADR:

1. Kontekst
2. Decyzja
3. Alternatywy
4. Konsekwencje
5. Plan migracji (jeśli dotyczy)

---

## 10. Minimalny plan uruchomienia projektu (bootstrap)

1. Inicjalizacja backendu i frontendu.
2. Konfiguracja `docker-compose` (api, web, db).
3. Pierwsza migracja DB.
4. Endpoint `health` i podstawowe logowanie aplikacyjne.
5. Pierwszy import FIT + zapis treningu.
6. Widok listy treningów i kalendarza.
7. Pipeline CI: lint + test + build.

---

## 11. Konkluzja

Ta specyfikacja stanowi **bazę operacyjną** dla rozwoju aplikacji przez zespół i AI Agenta.
Najważniejsze zasady to:

- spójne kontrakty,
- deterministyczna logika metryk,
- kontrolowane wprowadzanie AI,
- obowiązkowa dokumentacja i testy przy każdej iteracji.

Dzięki temu kolejne funkcje będą dodawane bez łamania wcześniejszych założeń i bez utraty jakości architektury.

---

## Changelog
- [2026-04-13] – korekty po review: ujednolicenie stacku (Flask), samples jako wymagane, kontekst SQLite, dodanie modułu FTP test.
