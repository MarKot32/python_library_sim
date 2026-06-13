"""
Symulator Biblioteki - TUI (curses)
Nawigacja: strzałki, Enter = wybór, Q/Esc = wstecz/wyjście
"""

import curses
import pandas as pd
import os
from datetime import date, timedelta
import time
BOOKS_CSV   = "books.csv"
READERS_CSV = "readers.csv"
LOANS_CSV   = "loans.csv"

C_NORMAL    = 1
C_HIGHLIGHT = 2
C_HEADER    = 3
C_SUCCESS   = 4
C_ERROR     = 5
C_BORDER    = 6
C_DIM       = 7


# Dane 

def mierz_czas(funkcja):
    def wrapper(*args, **kwargs):
        start = time.time()
        wynik = funkcja(*args, **kwargs)
        koniec = time.time()
        text = open("log.txt", "a")
        text.write(f"Funkcja '{funkcja.__name__}' wykonala sie w {koniec - start:.4f} s.")
        return wynik
    return wrapper

def init_data():
    if not os.path.exists(BOOKS_CSV):
        pd.DataFrame([
            {"id":1,"tytul":"Wiedźmin: Ostatnie życzenie","autor":"Andrzej Sapkowski","rok":1993,"gatunek":"Fantasy","dostepna":True},
            {"id":2,"tytul":"Pan Tadeusz",                "autor":"Adam Mickiewicz",  "rok":1834,"gatunek":"Epika",   "dostepna":True},
            {"id":3,"tytul":"Solaris",                    "autor":"Stanisław Lem",    "rok":1961,"gatunek":"SF",      "dostepna":False},
            {"id":4,"tytul":"Lalka",                      "autor":"Bolesław Prus",    "rok":1890,"gatunek":"Realizm", "dostepna":True},
            {"id":5,"tytul":"Harry Potter i Kamień Filozoficzny","autor":"J.K. Rowling","rok":1997,"gatunek":"Fantasy","dostepna":True},
            {"id":6,"tytul":"1984",                       "autor":"George Orwell",    "rok":1949,"gatunek":"Dystopia","dostepna":False},
            {"id":7,"tytul":"Mały Książę",               "autor":"Antoine de Saint-Exupéry","rok":1943,"gatunek":"Bajka","dostepna":True},
        ]).to_csv(BOOKS_CSV, index=False)

    if not os.path.exists(READERS_CSV):
        pd.DataFrame([
            {"id":1,"imie":"Anna",    "nazwisko":"Kowalska",  "email":"anna@mail.com",  "rejestracja":"2023-01-15"},
            {"id":2,"imie":"Piotr",   "nazwisko":"Nowak",     "email":"piotr@mail.com", "rejestracja":"2023-03-22"},
            {"id":3,"imie":"Marcin",  "nazwisko":"Wiśniewski","email":"marcin@mail.com","rejestracja":"2024-06-01"},
            {"id":4,"imie":"Katarzyna","nazwisko":"Zielińska","email":"kasia@mail.com", "rejestracja":"2024-09-10"},
        ]).to_csv(READERS_CSV, index=False)

    if not os.path.exists(LOANS_CSV):
        pd.DataFrame([
            {"id":1,"ksiazka_id":3,"czytelnik_id":2,"data_wyp":"2025-05-20","termin":"2025-06-03","zwrot":None,        "zwrocona":False},
            {"id":2,"ksiazka_id":6,"czytelnik_id":1,"data_wyp":"2025-04-01","termin":"2025-04-15","zwrot":None,        "zwrocona":False},
            {"id":3,"ksiazka_id":1,"czytelnik_id":3,"data_wyp":"2025-05-01","termin":"2025-05-15","zwrot":"2025-05-14","zwrocona":True},
        ]).to_csv(LOANS_CSV, index=False)

@mierz_czas
def load():
    books   = pd.read_csv(BOOKS_CSV)
    readers = pd.read_csv(READERS_CSV)
    loans   = pd.read_csv(LOANS_CSV)
    books["dostepna"] = books["dostepna"].astype(bool)
    loans["zwrocona"] = loans["zwrocona"].astype(bool)
    loans["termin"]   = pd.to_datetime(loans["termin"])
    return books, readers, loans


def save(books, readers, loans):
    books.to_csv(BOOKS_CSV,   index=False)
    readers.to_csv(READERS_CSV, index=False)
    loans.to_csv(LOANS_CSV,   index=False)


#  Pomocniki TUI

def sadd(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    try:
        win.addstr(y, x, text[:max(0, w - x - 1)], attr)
    except curses.error:
        pass


def draw_header(stdscr, title):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(C_HEADER) | curses.A_BOLD)
    stdscr.addstr(0, 0, " " * (w - 1))
    sadd(stdscr, 0, 2, f"BIBLIOTEKA  |  {title}", curses.color_pair(C_HEADER) | curses.A_BOLD)
    stdscr.attroff(curses.color_pair(C_HEADER) | curses.A_BOLD)


def draw_footer(stdscr, hint="  strzalki nawigacja  Enter wybor  Q wstecz"):
    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(C_DIM))
    stdscr.addstr(h - 1, 0, " " * (w - 1))
    sadd(stdscr, h - 1, 0, hint[:w - 1], curses.color_pair(C_DIM))
    stdscr.attroff(curses.color_pair(C_DIM))


def flash(stdscr, msg, color=C_SUCCESS):
    h, w = stdscr.getmaxyx()
    attr = curses.color_pair(color) | curses.A_BOLD
    stdscr.attron(attr)
    stdscr.addstr(h - 1, 0, " " * (w - 1))
    sadd(stdscr, h - 1, 0, msg[:w - 1], attr)
    stdscr.attroff(attr)
    stdscr.refresh()
    stdscr.getch()


def ask(stdscr, prompt, y, x, max_len=40):
    sadd(stdscr, y, x, prompt, curses.color_pair(C_NORMAL))
    px = x + len(prompt)
    h, w = stdscr.getmaxyx()
    fill = min(max_len, w - px - 1)
    sadd(stdscr, y, px, " " * fill, curses.color_pair(C_HIGHLIGHT))
    curses.echo()
    curses.curs_set(1)
    stdscr.move(y, px)
    stdscr.refresh()
    raw = stdscr.getstr(y, px, max_len)
    curses.noecho()
    curses.curs_set(0)
    return raw.decode("utf-8", errors="replace").strip()


def menu(stdscr, items, title="", oy=3, ox=6):
    idx = 0
    while True:
        stdscr.clear()
        draw_header(stdscr, title)
        draw_footer(stdscr)
        h, w = stdscr.getmaxyx()
        for i, item in enumerate(items):
            y = oy + i
            if y >= h - 1:
                break
            if i == idx:
                sadd(stdscr, y, ox, f"  >> {item}  ", curses.color_pair(C_HIGHLIGHT) | curses.A_BOLD)
            else:
                sadd(stdscr, y, ox, f"     {item}  ", curses.color_pair(C_NORMAL))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(items)
        elif key in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(items)
        elif key in (curses.KEY_ENTER, 10, 13):
            return idx
        elif key in (ord('q'), ord('Q'), 27):
            return -1


def table(stdscr, rows, cols, title=""):
    """cols = list of (key, header, width)"""
    page = curses.LINES - 6
    off  = 0
    while True:
        stdscr.clear()
        draw_header(stdscr, title)
        h, w = stdscr.getmaxyx()
        # nagłówek
        cx = 2
        for key, hdr, cw in cols:
            sadd(stdscr, 2, cx, hdr[:cw].ljust(cw), curses.color_pair(C_HEADER) | curses.A_BOLD)
            cx += cw + 2
        sadd(stdscr, 3, 2, "-" * (w - 4), curses.color_pair(C_BORDER))
        # wiersze
        for i, row in enumerate(rows[off: off + page]):
            y = 4 + i
            cx = 2
            for key, hdr, cw in cols:
                val = str(row.get(key, ""))
                sadd(stdscr, y, cx, val[:cw].ljust(cw), curses.color_pair(C_NORMAL))
                cx += cw + 2
        total = len(rows)
        draw_footer(stdscr, f"  {off+1}-{min(off+page,total)}/{total}  strzalki przewijanie  Q wróc")
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_DOWN, ord('j')) and off + page < total:
            off += 1
        elif key in (curses.KEY_UP, ord('k')) and off > 0:
            off -= 1
        elif key in (ord('q'), ord('Q'), 27):
            break


#  Ekrany 

def screen_books(stdscr, state):
    books = state[0]
    while True:
        ch = menu(stdscr, [
            "Lista wszystkich ksiazek",
            "Tylko dostepne",
            "Szukaj (tytul / autor / gatunek)",
            "Dodaj ksiazke",
            "Wróc",
        ], title="KSIAZKI")

        if ch == 0:
            rows = books.to_dict("records")
            for r in rows:
                r["dostepna"] = "TAK" if r["dostepna"] else "NIE"
            table(stdscr, rows,
                  [("id","ID",4),("tytul","Tytul",34),("autor","Autor",22),("gatunek","Gatunek",10),("dostepna","Dost.",4)],
                  "WSZYSTKIE KSIAZKI")

        elif ch == 1:
            rows = books[books["dostepna"]].to_dict("records")
            table(stdscr, rows,
                  [("id","ID",4),("tytul","Tytul",34),("autor","Autor",22),("gatunek","Gatunek",10)],
                  f"DOSTEPNE ({len(rows)})")

        elif ch == 2:
            stdscr.clear()
            draw_header(stdscr, "SZUKAJ")
            fraza = ask(stdscr, "  Fraza: ", 3, 2)
            if fraza:
                mask = (
                    books["tytul"].str.contains(fraza, case=False, na=False) |
                    books["autor"].str.contains(fraza, case=False, na=False) |
                    books["gatunek"].str.contains(fraza, case=False, na=False)
                )
                rows = books[mask].to_dict("records")
                for r in rows:
                    r["dostepna"] = "TAK" if r["dostepna"] else "NIE"
                table(stdscr, rows,
                      [("id","ID",4),("tytul","Tytul",34),("autor","Autor",22),("dostepna","Dost.",4)],
                      f"WYNIKI: '{fraza}' ({len(rows)})")

        elif ch == 3:
            stdscr.clear()
            draw_header(stdscr, "DODAJ KSIAZKE")
            tytul   = ask(stdscr, "  Tytul:   ", 3, 2)
            autor   = ask(stdscr, "  Autor:   ", 4, 2)
            rok_s   = ask(stdscr, "  Rok:     ", 5, 2, 6)
            gatunek = ask(stdscr, "  Gatunek: ", 6, 2)
            if tytul and autor:
                try:    rok = int(rok_s)
                except: rok = 0
                nid  = int(books["id"].max()) + 1
                books = pd.concat([books,
                    pd.DataFrame([{"id":nid,"tytul":tytul,"autor":autor,
                                   "rok":rok,"gatunek":gatunek,"dostepna":True}])],
                    ignore_index=True)
                state[0] = books
                save(*state)
                flash(stdscr, f"OK  Dodano: '{tytul}' (ID={nid})", C_SUCCESS)
            else:
                flash(stdscr, "BLAD  Tytul i autor sa wymagane.", C_ERROR)

        elif ch in (-1, 4):
            break
    state[0] = books


def screen_readers(stdscr, state):
    readers = state[1]
    while True:
        ch = menu(stdscr, ["Lista czytelnikow", "Zarejestruj czytelnika", "Wróc"], title="CZYTELNICY")

        if ch == 0:
            table(stdscr, readers.to_dict("records"),
                  [("id","ID",4),("imie","Imie",14),("nazwisko","Nazwisko",18),
                   ("email","E-mail",26),("rejestracja","Rejestracja",12)],
                  "CZYTELNICY")

        elif ch == 1:
            stdscr.clear()
            draw_header(stdscr, "NOWY CZYTELNIK")
            imie     = ask(stdscr, "  Imie:     ", 3, 2)
            nazwisko = ask(stdscr, "  Nazwisko: ", 4, 2)
            email    = ask(stdscr, "  E-mail:   ", 5, 2)
            if imie and nazwisko:
                nid = int(readers["id"].max()) + 1
                readers = pd.concat([readers,
                    pd.DataFrame([{"id":nid,"imie":imie,"nazwisko":nazwisko,
                                   "email":email,"rejestracja":str(date.today())}])],
                    ignore_index=True)
                state[1] = readers
                save(*state)
                flash(stdscr, f"OK  Zarejestrowano: {imie} {nazwisko} (ID={nid})", C_SUCCESS)
            else:
                flash(stdscr, "BLAD  Imie i nazwisko sa wymagane.", C_ERROR)

        elif ch in (-1, 2):
            break
    state[1] = readers


def screen_loans(stdscr, state):
    while True:
        ch = menu(stdscr, [
            "Aktywne wypozyczenia",
            "Historia (wszystkie)",
            "Nowe wypozyczenie",
            "Zwróc ksiazke",
            "Wróc",
        ], title="WYPOZYCZENIA")

        books, readers, loans = state[0], state[1], state[2]

        if ch in (0, 1):
            df = loans.copy()
            if ch == 0:
                df = df[df["zwrocona"] == False]
            df = df.merge(books[["id","tytul"]], left_on="ksiazka_id", right_on="id", suffixes=("","_b"))
            df = df.merge(readers[["id","imie","nazwisko"]], left_on="czytelnik_id", right_on="id", suffixes=("","_r"))
            df["czytelnik"] = df["imie"] + " " + df["nazwisko"]
            today = pd.Timestamp(date.today())
            df["termin_s"] = df["termin"].dt.strftime("%Y-%m-%d")
            df["status"]   = df.apply(lambda r:
                "zwrocona" if r["zwrocona"] else
                ("PRZETERMIN" if r["termin"] < today else "aktywna"), axis=1)
            rows = df[["id","tytul","czytelnik","termin_s","status"]].rename(
                columns={"termin_s":"termin"}).to_dict("records")
            title = f"AKTYWNE ({len(rows)})" if ch == 0 else f"HISTORIA ({len(rows)})"
            table(stdscr, rows,
                  [("id","ID",4),("tytul","Tytul",28),("czytelnik","Czytelnik",22),
                   ("termin","Termin",12),("status","Status",12)], title)

        elif ch == 2:
            stdscr.clear()
            draw_header(stdscr, "NOWE WYPOZYCZENIE")
            # podpowiedź
            dostepne = books[books["dostepna"]][["id","tytul"]].head(8)
            sadd(stdscr, 2, 2, "Dostepne ksiazki:", curses.color_pair(C_DIM))
            for i, (_, row) in enumerate(dostepne.iterrows()):
                sadd(stdscr, 3+i, 4, f"{row['id']:>3}  {row['tytul'][:35]}", curses.color_pair(C_DIM))
            rlist = readers[["id","imie","nazwisko"]].head(8)
            sadd(stdscr, 2, 50, "Czytelnicy:", curses.color_pair(C_DIM))
            for i, (_, row) in enumerate(rlist.iterrows()):
                sadd(stdscr, 3+i, 50, f"{row['id']:>3}  {row['imie']} {row['nazwisko']}", curses.color_pair(C_DIM))

            bid_s = ask(stdscr, "  ID ksiazki:    ", 12, 2, 6)
            rid_s = ask(stdscr, "  ID czytelnika: ", 13, 2, 6)
            dni_s = ask(stdscr, "  Dni [14]:      ", 14, 2, 4)
            try:
                bid = int(bid_s); rid = int(rid_s)
                dni = int(dni_s) if dni_s else 14
            except ValueError:
                flash(stdscr, "BLAD  Nieprawidlowe ID.", C_ERROR); continue

            if bid not in books["id"].values:
                flash(stdscr, f"BLAD  Brak ksiazki ID={bid}.", C_ERROR); continue
            if rid not in readers["id"].values:
                flash(stdscr, f"BLAD  Brak czytelnika ID={rid}.", C_ERROR); continue
            if not books.loc[books["id"] == bid, "dostepna"].values[0]:
                tyt = books.loc[books["id"] == bid, "tytul"].values[0]
                flash(stdscr, f"BLAD  '{tyt[:30]}' jest niedostepna.", C_ERROR); continue

            tyt    = books.loc[books["id"] == bid, "tytul"].values[0]
            czytel = readers.loc[readers["id"] == rid, ["imie","nazwisko"]].values[0]
            nid    = int(loans["id"].max()) + 1
            termin = date.today() + timedelta(days=dni)
            loans  = pd.concat([loans,
                pd.DataFrame([{"id":nid,"ksiazka_id":bid,"czytelnik_id":rid,
                               "data_wyp":str(date.today()),"termin":str(termin),
                               "zwrot":None,"zwrocona":False}])],
                ignore_index=True)
            loans["termin"] = pd.to_datetime(loans["termin"])
            books.loc[books["id"] == bid, "dostepna"] = False
            state[0], state[2] = books, loans
            save(*state)
            flash(stdscr, f"OK  '{tyt[:25]}' -> {czytel[0]} {czytel[1]}  termin: {termin}", C_SUCCESS)

        elif ch == 3:
            stdscr.clear()
            draw_header(stdscr, "ZWROT KSIAZKI")
            aktywne = loans[loans["zwrocona"] == False]
            aktywne = aktywne.merge(books[["id","tytul"]], left_on="ksiazka_id", right_on="id", suffixes=("","_b"))
            aktywne = aktywne.merge(readers[["id","imie","nazwisko"]], left_on="czytelnik_id", right_on="id", suffixes=("","_r"))
            sadd(stdscr, 2, 2, "Aktywne wypozyczenia:", curses.color_pair(C_DIM))
            for i, (_, row) in enumerate(aktywne.head(14).iterrows()):
                sadd(stdscr, 3+i, 4,
                     f"{row['id']:>3}  {row['tytul'][:26]:<26}  {row['imie']} {row['nazwisko']}",
                     curses.color_pair(C_DIM))
            wyp_s = ask(stdscr, "  ID wypozyczenia: ", 18, 2, 6)
            try:
                wyp_id = int(wyp_s)
            except ValueError:
                flash(stdscr, "BLAD  Nieprawidlowe ID.", C_ERROR); continue
            if wyp_id not in loans["id"].values:
                flash(stdscr, f"BLAD  Brak wypozyczenia ID={wyp_id}.", C_ERROR); continue
            if loans.loc[loans["id"] == wyp_id, "zwrocona"].values[0]:
                flash(stdscr, "BLAD  Juz zwrocona.", C_ERROR); continue
            bid = int(loans.loc[loans["id"] == wyp_id, "ksiazka_id"].values[0])
            tyt = books.loc[books["id"] == bid, "tytul"].values[0]
            loans.loc[loans["id"] == wyp_id, "zwrot"]    = str(date.today())
            loans.loc[loans["id"] == wyp_id, "zwrocona"] = True
            books.loc[books["id"] == bid, "dostepna"]    = True
            state[0], state[2] = books, loans
            save(*state)
            flash(stdscr, f"OK  Zwrócono: '{tyt[:40]}'", C_SUCCESS)

        elif ch in (-1, 4):
            break


def screen_stats(stdscr, state):
    books, readers, loans = state
    today = pd.Timestamp(date.today())
    aktywne = loans[loans["zwrocona"] == False]
    przet   = aktywne[aktywne["termin"] < today]

    stdscr.clear()
    draw_header(stdscr, "STATYSTYKI")

    lines = [
        ("", C_NORMAL),
        ("  -- ZBIORY --", C_HEADER),
        (f"  Ksiazek ogolnie:       {len(books)}", C_NORMAL),
        (f"  Dostepnych:            {int(books['dostepna'].sum())}", C_SUCCESS),
        (f"  Wypozyczonych:         {int((~books['dostepna']).sum())}", C_NORMAL),
        ("", C_NORMAL),
        ("  -- CZYTELNICY --", C_HEADER),
        (f"  Zarejestrowanych:      {len(readers)}", C_NORMAL),
        ("", C_NORMAL),
        ("  -- WYPOZYCZENIA --", C_HEADER),
        (f"  Ogolnie:               {len(loans)}", C_NORMAL),
        (f"  Aktywnych:             {len(aktywne)}", C_NORMAL),
        (f"  Przeterminowanych:     {len(przet)}", C_ERROR if len(przet) else C_NORMAL),
        (f"  Zwróconych:            {int(loans['zwrocona'].sum())}", C_SUCCESS),
        ("", C_NORMAL),
        ("  -- GATUNKI --", C_HEADER),
    ]
    for g, n in books["gatunek"].value_counts().items():
        lines.append((f"  {g:<20} {n}", C_NORMAL))

    for i, (txt, col) in enumerate(lines):
        sadd(stdscr, 1 + i, 0, txt, curses.color_pair(col))

    draw_footer(stdscr, "  Dowolny klawisz aby wrócic...")
    stdscr.refresh()
    stdscr.getch()


#  Menu główne 

def main_menu(stdscr, state):
    while True:
        aktywne = int((~state[2]["zwrocona"]).sum())
        ch = menu(stdscr, [
            "Ksiazki",
            "Czytelnicy",
            f"Wypozyczenia  [{aktywne} aktywnych]",
            "Statystyki",
            "Wyjscie",
        ], title="MENU GLOWNE", oy=5, ox=10)

        if   ch == 0: screen_books(stdscr, state)
        elif ch == 1: screen_readers(stdscr, state)
        elif ch == 2: screen_loans(stdscr, state)
        elif ch == 3: screen_stats(stdscr, state)
        elif ch in (-1, 4): break


#  Entry point 

def run(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_NORMAL,    curses.COLOR_WHITE,  -1)
    curses.init_pair(C_HIGHLIGHT, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(C_HEADER,    curses.COLOR_YELLOW, -1)
    curses.init_pair(C_SUCCESS,   curses.COLOR_GREEN,  -1)
    curses.init_pair(C_ERROR,     curses.COLOR_RED,    -1)
    curses.init_pair(C_BORDER,    curses.COLOR_CYAN,   -1)
    curses.init_pair(C_DIM,       8,                   -1)
    curses.curs_set(0)
    curses.noecho()
    stdscr.keypad(True)

    init_data()
    books, readers, loans = load()
    state = [books, readers, loans]
    main_menu(stdscr, state)

    stdscr.clear()
    h, w = stdscr.getmaxyx()
    msg = "Do widzenia! Dane zapisane."
    sadd(stdscr, h // 2, (w - len(msg)) // 2, msg,
         curses.color_pair(C_SUCCESS) | curses.A_BOLD)
    stdscr.refresh()
    curses.napms(1000)


if __name__ == "__main__":
    curses.wrapper(run)
