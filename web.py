import json

# Základné informácie o produktoch
ZAKLADNE_PRODUKTY = [
    {"id": 0, "nazov": "jablko", "cena": 0.50, "druh": "ovocie"},
    {"id": 1, "nazov": "banan", "cena": 0.45, "druh": "ovocie"},
    {"id": 2, "nazov": "mrkva", "cena": 0.30, "druh": "zelenina"},
    {"id": 3, "nazov": "zemiak", "cena": 0.25, "druh": "zelenina"},
    {"id": 4, "nazov": "mlieko", "cena": 1.20, "druh": "mliečne"}
]

def handler(event, context):
    path = event.get("path", "")
    api_path = path.replace("/.netlify/functions/api", "")
    if not api_path:
        api_path = "/"

    # Načítanie aktuálneho stavu, ktorý poslal frontend
    try:
        req_data = json.loads(event.get("body", "{}")) if event.get("body") else {}
    except:
        req_data = {}

    # Ak frontend neposlal stav skladu, použijeme predvolený z vašej úlohy: [5, 3, 4, 6, 2]
    sklad = req_data.get("sklad", [5, 3, 4, 6, 2])
    kosik = req_data.get("kosik", [])
    celkova_cena = req_data.get("celkova_cena", 0.0)
    clubcard_uplatnena = req_data.get("clubcard_uplatnena", False)
    kupon_uplatneny = req_data.get("kupon_uplatneny", False)

    response_body = {}
    status_code = 200

    # 1. Stav obchodu
    if api_path == "/stav":
        produkty_so_skladom = []
        for p in ZAKLADNE_PRODUKTY:
            produkty_so_skladom.append({
                **p,
                "sklad": sklad[p["id"]]
            })
        response_body = {
            "produkty": produkty_so_skladom,
            "kosik": kosik,
            "celkova_cena": round(celkova_cena, 2),
            "sklad": sklad,
            "clubcard_uplatnena": clubcard_uplatnena,
            "kupon_uplatneny": kupon_uplatneny
        }

    # 2. Pridanie do košíka
    elif "/kupit/" in api_path:
        try:
            pozicia = int(api_path.split("/")[-1])
            if sklad[pozicia] > 0:
                kosik.append(ZAKLADNE_PRODUKTY[pozicia]["nazov"])
                celkova_cena += ZAKLADNE_PRODUKTY[pozicia]["cena"]
                sklad[pozicia] -= 1
                response_body = {
                    "sklad": sklad, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
                    "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
                }
            else:
                status_code = 400
                response_body = {"error": "Vypredané"}
        except:
            status_code = 400

    # 3. Clubcard zľava
    elif api_path == "/clubcard":
        if not clubcard_uplatnena:
            celkova_cena = celkova_cena * 0.9
            clubcard_uplatnena = True
        response_body = {
            "sklad": sklad, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }

    # 4. Kupón zľava
    elif api_path == "/kupon":
        if not kupon_uplatneny:
            celkova_cena = celkova_cena * 0.8
            kupon_uplatneny = True
        response_body = {
            "sklad": sklad, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }

    # 5. Zaplatenie a reset
    elif api_path == "/zaplatit":
        response_body = {
            "sklad": [5, 3, 4, 6, 2],
            "kosik": [],
            "celkova_cena": 0.0,
            "clubcard_uplatnena": False,
            "kupon_uplatneny": False
        }
    else:
        status_code = 404
        response_body = {"error": "Nenájdené"}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_body)
    }
