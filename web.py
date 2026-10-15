import json

# Fix chýbajúcich dát – sklady sú plne doplnené
ZAKLADNE_PRODUKTY = [
    {"id": 0, "nazov": "jablko", "cena": 0.50, "druh": "ovocie"},
    {"id": 1, "nazov": "banan", "cena": 0.45, "druh": "ovocie"},
    {"id": 2, "nazov": "mrkva", "cena": 0.30, "druh": "zelenina"},
    {"id": 3, "nazov": "zemiak", "cena": 0.25, "druh": "zelenina"},
    {"id": 4, "nazov": "mlieko", "cena": 1.20, "druh": "mliečne"}
]

def handler(event, context):
    path = event.get("path", "")
    api_path = path.replace("/.netlify/functions/web", "")
    if not api_path:
        api_path = "/"

    # Načítanie stavu z prehliadača
    try:
        req_data = json.loads(event.get("body", "{}")) if event.get("body") else {}
    except:
        req_data = {}

    # Správne zadefinované predvolené hodnoty (žiadne prázdne miesta)
    sklad = req_data.get("sklad", [5, 3, 4, 6, 2])
    kosik = req_data.get("kosik", [])
    celkova_cena = req_data.get("celkova_cena", 0.0)
    clubcard_uplatnena = req_data.get("clubcard_uplatnena", False)
    kupon_uplatneny = req_data.get("kupon_uplatneny", False)

    response_body = {}
    status_code = 200

    # 1. API: Stav obchodu
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
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    # 2. API: Kúpiť produkt
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
        return {
            "statusCode": status_code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    # 3. API: Clubcard
    elif api_path == "/clubcard":
        if not clubcard_uplatnena:
            celkova_cena = celkova_cena * 0.9
            clubcard_uplatnena = True
        response_body = {
            "sklad": sklad, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    # 4. API: Kupón
    elif api_path == "/kupon":
        if not kupon_uplatneny:
            celkova_cena = celkova_cena * 0.8
            kupon_uplatneny = True
        response_body = {
            "sklad": sklad, "kosik": kosik, "celkova_cena": round(celkova_cena, 2),
            "clubcard_uplatnena": clubcard_uplatnena, "kupon_uplatneny": kupon_uplatneny
        }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    # 5. API: Zaplatiť
    elif api_path == "/zaplatit":
        response_body = {
            "sklad":,
            "kosik": [],
            "celkova_cena": 0.0,
            "clubcard_uplatnena": False,
            "kupon_uplatneny": False
        }
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body)
        }

    # 6. Zobrazenie samotného webu (Frontend integrovaný priamo vnútri)
    else:
        html = """
        <!DOCTYPE html>
        <html lang="sk">
        <head>
            <meta charset="UTF-8">
            <title>Môj Webový Obchod</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; background: #f4f6f9; color: #333; }
                .kontajner { display: flex; gap: 20px; }
                .karta { background: white; padding: 20px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .polozka { display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #eee; align-items: center; }
                button { background: #0070f3; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
                button:disabled { background: #ccc; cursor: not-allowed; }
                .tlacidla-zlav { display: flex; gap: 10px; margin: 15px 0; }
                .btn-platba { background: #22c55e; width: 100%; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 6px; color: white; border: none; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>=== OBCHOD ===</h1>
            <div class="kontajner">
                <div class="karta">
                    <h2>Ponuka produktov</h2>
                    <div id="produkty-box">Načítavam produkty...</div>
                </div>
                <div class="karta">
                    <h2>--- KOŠÍK ---</h2>
                    <ul id="kosik-box"></ul>
                    <hr>
                    <h3>Celková cena: <span id="cena-box">0.00</span> €</h3>
                    <div class="tlacidla-zlav">
                        <button id="btn-clubcard" onclick="uplatnitClubcard()" style="background:#4f46e5;">💳 Skenovať Clubcard (-10%)</button>
                        <button id="btn-kupon" onclick="uplatnitKupon()" style="background:#db2777;">🎟️ Použiť Kupón (-20%)</button>
                    </div>
                    <label for="platba">Zvoľte spôsob platby:</label>
                    <select id="platba" style="width:100%; padding:8px; margin: 10px 0 20px 0;">
                        <option value="1">1. Hotovosť</option>
                        <option value="2">2. Karta</option>
                        <option value="3">3. Kupón</option>
                    </select>
                    <button class="btn-platba" onclick="zaplatit()">Zaplatiť nákup</button>
                </div>
            </div>

            <script>
                const API_URL = '/.netlify/functions/web';
                
                let lokalnyStav = {
                    sklad:,
                    kosik: [],
                    celkova_cena: 0.0,
                    clubcard_uplatnena: false,
                    kupon_uplatneny: false
                };

                async function posliPoziadavku(urlSuffix) {
                    let res = await fetch(`${API_URL}${urlSuffix}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(lokalnyStav)
                    });
                    return await res.json();
                }

                async function inicializujObchod() {
                    let data = await posliPoziadavku('/stav');
                    vykresliData(data);
                }

                function vykresliData(data) {
                    lokalnyStav = data;

                    let prodHtml = "";
                    data.produkty.forEach(p => {
                        let jeVypredane = p.sklad === 0;
                        let textSkladu = jeVypredane ? "VYPREDANÉ" : "sklad: " + p.sklad;
                        prodHtml += `
                            <div class="polozka">
                                <div><strong>${p.nazov.toUpperCase()}</strong> - ${p.cena.toFixed(2)} €</div>
                                <button onclick="kupit(${p.id})" ${jeVypredane ? 'disabled' : ''}>
                                    ${jeVypredane ? 'Vypredané' : 'Kúpiť (' + textSkladu + ')'}
                                </button>
                            </div>`;
                    });
                    document.getElementById('produkty-box').innerHTML = prodHtml;

                    let kosikHtml = data.kosik.length === 0 ? "<li>Košík je prázdny</li>" : "";
                    data.kosik.forEach(p => { kosikHtml += `<li>- ${p}</li>`; });
                    document.getElementById('kosik-box').innerHTML = kosikHtml;

                    document.getElementById('cena-box').innerText = data.celkova_cena.toFixed(2);
                    document.getElementById('btn-clubcard').disabled = data.clubcard_uplatnena;
                    document.getElementById('btn-kupon').disabled = data.kupon_uplatneny;
                }

                async function kupit(id) {
                    let data = await posliPoziadavku(`/kupit/${id}`);
                    if(!data.error) {
                        vykresliData(data);
                    }
                }

                async function uplatnitClubcard() {
                    let data = await posliPoziadavku('/clubcard');
                    alert("Clubcard bola naskenovaná! Uplatnená zľava 10 %.");
                    vykresliData(data);
                }

                async function uplatnitKupon() {
                    let data = await posliPoziadavku('/kupon');
                    alert("Kupón bol uplatnený! Uplatnená zľava 20 %.");
                    vykresliData(data);

