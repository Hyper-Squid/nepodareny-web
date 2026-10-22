
import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Neskôr nahraď svojou Netlify doménou
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

def pripojenie():
    url = os.environ["DATABASE_URL"]
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode="require")


def vytvor_tabulky():
    with pripojenie() as db:
        with db.cursor() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS produkty (
                    id SERIAL PRIMARY KEY,
                    nazov TEXT UNIQUE NOT NULL,
                    cena NUMERIC(10, 2) NOT NULL CHECK (cena >= 0),
                    sklad INTEGER NOT NULL DEFAULT 0 CHECK (sklad >= 0)
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS nakupy (
                    id SERIAL PRIMARY KEY,
                    produkt_id INTEGER REFERENCES produkty(id),
                    nazov TEXT NOT NULL,
                    pocet INTEGER NOT NULL,
                    cena NUMERIC(10, 2) NOT NULL,
                    datum TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            # Vloží vzorové produkty iba vtedy, keď databáza
            # ešte nemá žiadne produkty.
            c.execute("SELECT COUNT(*) FROM produkty")
            if c.fetchone()[0] == 0:
                c.executemany("""
                    INSERT INTO produkty (nazov, cena, sklad)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (nazov) DO NOTHING
                """, [
                    ("jablko", 0.50, 5),
                    ("banan", 0.45, 3),
                    ("mrkva", 0.30, 4),
                    ("zemiak", 0.25, 6),
                    ("mlieko", 1.20, 2)
                ])


@app.on_event("startup")
def start():
    vytvor_tabulky()


class Nakup(BaseModel):
    produkt_id: int
    pocet: int = Field(gt=0, le=100)


@app.get("/")
def domov():
    return {"sprava": "Obchod API funguje"}


@app.get("/produkty")
def produkty():
    with pripojenie() as db:
        with db.cursor() as c:
            c.execute("""
                SELECT id, nazov, cena, sklad
                FROM produkty ORDER BY id
            """)
            riadky = c.fetchall()

    return [
        {
            "id": r[0],
            "nazov": r[1],
            "cena": float(r[2]),
            "sklad": r[3],
            "vypredane": r[3] == 0
        }
        for r in riadky
    ]


@app.post("/nakup")
def nakup(data: Nakup):
    with pripojenie() as db:
        with db.cursor() as c:
            c.execute("""
                SELECT nazov, cena, sklad
                FROM produkty
                WHERE id = %s
                FOR UPDATE
            """, (data.produkt_id,))

            produkt = c.fetchone()

            if produkt is None:
                raise HTTPException(404, "Produkt neexistuje")

            nazov, cena, sklad = produkt

            if sklad < data.pocet:
                raise HTTPException(
                    400, f"Nedostatok na sklade. Zostáva: {sklad}"
                )

            c.execute("""
                UPDATE produkty
                SET sklad = sklad - %s
                WHERE id = %s
            """, (data.pocet, data.produkt_id))

            c.execute("""
                INSERT INTO nakupy (produkt_id, nazov, pocet, cena)
                VALUES (%s, %s, %s, %s)
            """, (data.produkt_id, nazov, data.pocet, cena))

            zostava = sklad - data.pocet

    return {
        "sprava": "Nákup uložený",
        "produkt": nazov,
        "pocet": data.pocet,
        "celkom": round(float(cena) * data.pocet, 2),
        "zostava_na_sklade": zostava
    }


@app.get("/nakupy")
def nakupy():
    with pripojenie() as db:
        with db.cursor() as c:
            c.execute("""
                SELECT id, nazov, pocet, cena, datum
                FROM nakupy ORDER BY id DESC
            """)
            riadky = c.fetchall()

    return [
        {
            "id": r[0],
            "produkt": r[1],
            "pocet": r[2],
            "cena_za_kus": float(r[3]),
            "datum": r[4].isoformat()
        }
        for r in riadky
    ]
