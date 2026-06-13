# Symulator Biblioteki

Terminalowa aplikacja do zarządzania biblioteką napisana w Pythonie z wykorzystaniem bibliotek `curses` i `pandas`. Dane przechowywane są lokalnie w plikach CSV.

---

## Spis treści

1. [Wymagania](#wymagania)
2. [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
3. [Struktura projektu](#struktura-projektu)
4. [Schemat danych](#schemat-danych)
5. [Nawigacja w aplikacji](#nawigacja-w-aplikacji)
6. [Opis modułów](#opis-modułów)
   - [Książki](#książki)
   - [Czytelnicy](#czytelnicy)
   - [Wypożyczenia](#wypożyczenia)
   - [Statystyki](#statystyki)
7. [Opis funkcji](#opis-funkcji)
   - [Warstwa danych](#warstwa-danych)
   - [Pomocniki TUI](#pomocniki-tui)
   - [Ekrany](#ekrany)
8. [Obsługa błędów](#obsługa-błędów)
9. [Możliwe rozszerzenia](#możliwe-rozszerzenia)

---

## Wymagania

| Zależność | Wersja | Uwagi |
|-----------|--------|-------|
| Python    | 3.8+   | wymagane |
| pandas    | 1.3+   | instalacja przez pip |
| curses    | -      | wbudowana w Pythona (Linux/macOS) |

> **Windows:** biblioteka `curses` nie jest domyślnie dostępna. Zaleca się używanie WSL (Windows Subsystem for Linux) lub zainstalowanie pakietu `windows-curses` przez pip.

---

## Instalacja i uruchomienie

```bash
# 1. Sklonuj repozytorium lub pobierz plik
git clone https://github.com/MarKot32/library-tui
cd library-tui

# 2. Zainstaluj zależności
pip install pandas

# 3. Uruchom aplikację
python library_tui.py
```

Przy pierwszym uruchomieniu aplikacja automatycznie tworzy pliki CSV z przykładowymi danymi (7 książek, 4 czytelników, 3 wypożyczenia).

---

## Struktura projektu

```
library-tui/
├── library_tui.py   # główny plik aplikacji
├── books.csv        # dane książek (tworzony automatycznie)
├── readers.csv      # dane czytelników (tworzony automatycznie)
├── loans.csv        # dane wypożyczeń (tworzony automatycznie)
└── README.md        # dokumentacja
```

---

## Schemat danych

### books.csv - Książki

| Kolumna    | Typ     | Opis                              |
|------------|---------|-----------------------------------|
| `id`       | int     | unikalny identyfikator            |
| `tytul`    | string  | tytuł książki                     |
| `autor`    | string  | imię i nazwisko autora            |
| `rok`      | int     | rok wydania                       |
| `gatunek`  | string  | gatunek literacki                 |
| `dostepna` | bool    | czy książka jest dostępna (`True`/`False`) |

### readers.csv — Czytelnicy

| Kolumna       | Typ    | Opis                           |
|---------------|--------|--------------------------------|
| `id`          | int    | unikalny identyfikator         |
| `imie`        | string | imię czytelnika                |
| `nazwisko`    | string | nazwisko czytelnika            |
| `email`       | string | adres e-mail                   |
| `rejestracja` | date   | data rejestracji (YYYY-MM-DD)  |

### loans.csv - Wypożyczenia

| Kolumna        | Typ    | Opis                                        |
|----------------|--------|---------------------------------------------|
| `id`           | int    | unikalny identyfikator                      |
| `ksiazka_id`   | int    | klucz obcy → `books.id`                    |
| `czytelnik_id` | int    | klucz obcy → `readers.id`                  |
| `data_wyp`     | date   | data wypożyczenia (YYYY-MM-DD)              |
| `termin`       | date   | planowany termin zwrotu (YYYY-MM-DD)        |
| `zwrot`        | date   | rzeczywista data zwrotu (puste = nie zwrócono) |
| `zwrocona`     | bool   | czy książka została zwrócona               |

---

## Nawigacja w aplikacji

| Klawisz            | Akcja                              |
|--------------------|------------------------------------|
| `↑` / `k`          | pozycja wyżej w menu / tabeli      |
| `↓` / `j`          | pozycja niżej w menu / tabeli      |
| `Enter`            | wybór zaznaczonej opcji            |
| `Q` / `q` / `Esc`  | wyjście / powrót do poprzedniego ekranu |

Zaznaczona pozycja menu oznaczona jest symbolem `>>` i wyróżniona kolorem cyjanowym.

---

## Opis modułów

### Książki

Dostęp: Menu główne >> **Książki**

| Opcja | Opis |
|-------|------|
| Lista wszystkich książek | Wyświetla pełną tabelę z kolumnami: ID, Tytuł, Autor, Gatunek, Dostępna |
| Tylko dostępne | Filtruje i pokazuje wyłącznie książki z `dostepna = True` |
| Szukaj | Wyszukiwanie po frazie w tytule, autorze **lub** gatunku (wielkość liter bez znaczenia) |
| Dodaj książkę | Formularz: Tytuł, Autor, Rok, Gatunek — po zatwierdzeniu zapisuje do CSV |

### Czytelnicy

Dostęp: Menu główne >> **Czytelnicy**

| Opcja | Opis |
|-------|------|
| Lista czytelników | Tabela: ID, Imię, Nazwisko, E-mail, Data rejestracji |
| Zarejestruj czytelnika | Formularz: Imię, Nazwisko, E-mail — data rejestracji ustawiana automatycznie |

### Wypożyczenia

Dostęp: Menu główne >> **Wypożyczenia**

| Opcja | Opis |
|-------|------|
| Aktywne wypożyczenia | Pokazuje tylko niezwrócone; kolumna Status wyróżnia pozycje przeterminowane (`PRZETERMIN`) |
| Historia (wszystkie) | Pełna lista z uwzględnieniem zwróconych |
| Nowe wypożyczenie | Formularz: ID książki, ID czytelnika, liczba dni (domyślnie 14); aplikacja waliduje dostępność |
| Zwróć książkę | Formularz: ID wypożyczenia; automatycznie ustawia datę zwrotu i przywraca dostępność książki |

### Statystyki

Dostęp: Menu główne >> **Statystyki**

Wyświetla jednoekranowe podsumowanie:
- liczba książek (ogółem / dostępnych / wypożyczonych)
- liczba zarejestrowanych czytelników
- liczba wypożyczeń (ogółem / aktywnych / przeterminowanych / zwróconych)
- zestawienie książek według gatunków

---

## Opis funkcji

### Warstwa danych

```python
init_data()
```
Tworzy pliki CSV z przykładowymi danymi, jeśli jeszcze nie istnieją. Wywoływana automatycznie przy starcie.

---

```python
load() -> (books, readers, loans)
```
Wczytuje trzy pliki CSV do obiektów `pandas.DataFrame`. Wykonuje konwersję typów: `dostepna` i `zwrocona` → `bool`, `termin` → `datetime`.

---

```python
save(books, readers, loans)
```
Zapisuje wszystkie trzy DataFrame z powrotem do plików CSV. Wywoływana po każdej operacji modyfikującej dane (dodanie, wypożyczenie, zwrot).

---

### Pomocniki TUI

```python
sadd(win, y, x, text, attr=0)
```
Bezpieczny wrapper na `curses.addstr` - nie rzuca wyjątku przy próbie zapisu poza granicą okna terminala.

---

```python
draw_header(stdscr, title)
```
Rysuje żółty pasek nagłówka na górze ekranu z aktualną nazwą widoku.

---

```python
draw_footer(stdscr, hint)
```
Rysuje szary pasek na dole ekranu z podpowiedzią klawiszową.

---

```python
flash(stdscr, msg, color)
```
Wyświetla komunikat w pasku footer (zielony = sukces, czerwony = błąd) i czeka na dowolny klawisz.

---

```python
ask(stdscr, prompt, y, x, max_len=40) -> str
```
Wyświetla etykietę i podświetlone pole tekstowe; zwraca wpisany ciąg znaków po naciśnięciu `Enter`.

---

```python
menu(stdscr, items, title, oy, ox) -> int
```
Interaktywne menu strzałkowe. Zwraca indeks wybranej pozycji lub `-1` po naciśnięciu `Q`/`Esc`.

---

```python
table(stdscr, rows, cols, title)
```
Wyświetla przewijalną tabelę danych. Parametr `cols` to lista krotek `(klucz, nagłówek, szerokość_kolumny)`. Przewijanie wiersz po wierszu strzałkami `↑`/`↓`.

---

### Ekrany

| Funkcja | Opis |
|---------|------|
| `screen_books(stdscr, state)` | Obsługuje podmenu Książki |
| `screen_readers(stdscr, state)` | Obsługuje podmenu Czytelnicy |
| `screen_loans(stdscr, state)` | Obsługuje podmenu Wypożyczenia |
| `screen_stats(stdscr, state)` | Wyświetla ekran statystyk (tylko odczyt) |
| `main_menu(stdscr, state)` | Główna pętla nawigacji; wyświetla liczbę aktywnych wypożyczeń w etykiecie opcji |
| `run(stdscr)` | Inicjalizuje kolory curses, ładuje dane i uruchamia `main_menu` |

Wszystkie ekrany współdzielą obiekt `state = [books, readers, loans]` (lista mutowalnych DataFrame). Po każdej zmianie danych wywoływane jest `save(*state)`.

---

## Obsługa błędów

Aplikacja sprawdza poprawność danych wejściowych przed każdą operacją:

| Sytuacja | Komunikat |
|----------|-----------|
| Nieprawidłowe ID (nie-liczba) | `BLAD  Nieprawidlowe ID.` |
| Książka o podanym ID nie istnieje | `BLAD  Brak ksiazki ID=X.` |
| Czytelnik o podanym ID nie istnieje | `BLAD  Brak czytelnika ID=X.` |
| Próba wypożyczenia niedostępnej książki | `BLAD  'Tytuł' jest niedostepna.` |
| Próba zwrotu już zwróconej książki | `BLAD  Juz zwrocona.` |
| Brak tytułu lub autora przy dodawaniu | `BLAD  Tytul i autor sa wymagane.` |

Wszystkie błędy wyświetlane są w czerwonym pasku na dole ekranu i wymagają naciśnięcia dowolnego klawisza.

---

## Możliwe rozszerzenia

- **Usuwanie rekordów** - możliwość usunięcia książki lub wyrejestrowania czytelnika
- **Edycja danych** - zmiana tytułu, autora, e-maila itp.
- **Powiadomienia o przeterminowaniu** - automatyczny alert przy starcie jeśli są przeterminowane wypożyczenia
- **Eksport raportów** - zapis statystyk do pliku tekstowego lub PDF
- **Wyszukiwanie czytelnika** - analogiczne do wyszukiwania książek
- **Wieloegzemplarzowość** - obsługa wielu kopii tej samej książki
- **Baza danych SQLite** - zamiana CSV na lekką bazę danych dla większych zbiorów
