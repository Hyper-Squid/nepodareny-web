import json

# Globálne dáta obchodu
produkty = ["jablko", "banan", "mrkva", "zemiak", "mlieko"]
ceny = [0.50, 0.45, 0.30, 0.25, 1.20]
druhy = ["ovocie", "ovocie", "zelenina", "zelenina", "mliečne"]
sklad = [5, 3, 4, 6, 2]

kosik = []
celkova_cena = 0
clubcard_uplatnena = False
kupon_uplatneny = False

def handler(event, context):
    global kosik, celkova_cena, clubcard_uplatnena, kupon_uplatneny
    
    path = event.get("path", "")
    
    # Odstránenie predpony, aby sme vedeli porovnať cesty
    api_path = path.replace("/.netlify/functions/api", "")
    if not api_path:
        api_path = "/"

    response_body = {}
    status_code = 200

    # 1. API: Stav obchodu
    if api_path == "/stav":
        zoznam_produktov = []
        for i in range(len(produkty)):
            zoznam_produktov.append({
                "id": i,
                "nazov": produkty[i],
                "cena": ceny[i],
                "druh": druhy[i],
                "sklad": sklad[i]
            })
        response_body = {
            "produkty": zoznam_produktov,
            "kosik": kosik,
            "celkova_cena": round(celkova_cena, 2)
        }

    # 2. API: Kúpiť produkt
    elif "/kupit/" in api_path:
        try:
            pozicia = int(api_path.split("/")[-1])
            if sklad[pozicia] > 0:
                kosik.append(produkty[pozicia])
                celkova_cena += ceny[pozicia]
                sklad[pozicia] -= 1
                response_body = {"status": "success"}
            else:
                status_code = 400
                response_body = {"error": "Vypredané"}
        except:
            status_code = 400

    # 3. API: Clubcard
    elif api_path == "/clubcard":
        if not clubcard_uplatnena:
            celkova_cena = celkova_cena * 0.9
            clubcard_uplatnena = True
        response_body = {"status": "success"}

    # 4. API: Kupón
    elif api_path == "/kupon":
        if not kupon_uplatneny:
            celkova_cena = celkova_cena * 0.8
            kupon_uplatneny = True
        response_body = {"status": "success"}

    # 5. API: Zaplatiť
    elif api_path == "/zaplatit":
        kosik = []
        celkova_cena = 0
        clubcard_uplatnena = False
        kupon_uplatneny = False
        response_body = {"status": "success"}
        
    else:
        status_code = 404
        response_body = {"error": "Not Found"}

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_body)
    }
