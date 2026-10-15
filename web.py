from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# --- TVOJE PÔVODNÉ DÁTA ---
produkty = ["jablko", "banan", "mrkva", "zemiak", "mlieko"]
ceny = [0.50, 0.45, 0.30, 0.25, 1.20]
druhy = ["ovocie", "ovocie", "zelenina", "zelenina", "mliečne"]
sklad = [5, 3, 4, 6, 2]

kosik = []
celkova_cena = 0
clubcard_uplatnena = False
kupon_uplatneny = False

class WebObchodBackend(BaseHTTPRequestHandler):
    def do_GET(self):
        global kosik, celkova_cena, clubcard_uplatnena, kupon_uplatneny
        
        # 1. API: Posiela dáta o obchode do webstránky
        if self.path == "/api/stav":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            # Formátovanie produktov pre web, aby sa dali jednoducho vypísať
            zoznam_produktov = []
            for i in range(len(produkty)):
                zoznam_produktov.append({
                    "id": i,
                    "nazov": produkty[i],
                    "cena": ceny[i],
                    "druh": druhy[i],
                    "sklad": sklad[i]
                })
                
            data = {
                "produkty": zoznam_produktov,
                "kosik": kosik,
                "celkova_cena": round(celkova_cena, 2)
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            
        # 2. API: Pridanie do košíka (Tvoja logika z while cyklu)
        elif self.path.startswith("/api/kupit/"):
            pozicia = int(self.path.split("/")[-1])
            
            if sklad[pozicia] > 0:
                kosik.append(produkty[pozicia])
                celkova_cena = celkova_cena + ceny[pozicia]
                sklad[pozicia] = sklad[pozicia] - 1
                self.send_response(200)
            else:
                self.send_response(400)
            self.end_headers()
            
        # 3. API: Clubcard (Zľava 10%)
        elif self.path == "/api/clubcard":
            if not clubcard_uplatnena:
                celkova_cena = celkova_cena * 0.9
                clubcard_uplatnena = True
            self.send_response(200)
            self.end_headers()
            
        # 4. API: Kupón (Zľava 20%)
        elif self.path == "/api/kupon":
            if not kupon_uplatneny:
                celkova_cena = celkova_cena * 0.8
                kupon_uplatneny = True
            self.send_response(200)
            self.end_headers()
            
        # 5. API: Zaplatenie a reset obchodu
        elif self.path == "/api/zaplatit":
            kosik = []
            celkova_cena = 0
            clubcard_uplatnena = False
            kupon_uplatneny = False
            self.send_response(200)
            self.end_headers()
            
        # 6. FRONTEND: Vykreslenie webového rozhrania
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
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
                    .btn-platba { background: #22c55e; width: 100%; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 6px; }
                </style>
            </head>
            <body>
                <h1>=== OBCHOD ===</h1>
                <div class="kontajner">
                    
                    <!-- PONUKA TOVARU -->
                    <div class="karta">
                        <h2>Ponuka produktov</h2>
                        <div id="produkty-box"></div>
                    </div>
                    
                    <!-- NÁKUPNÝ KOŠÍK -->
                    <div class="karta">
                        <h2>--- KOŠÍK ---</h2>
                        <ul id="kosik-box"></ul>
                        <hr>
                        <h3>Celková cena: <span id="cena-box">0.00</span> €</h3>
                        
                        <div class="tlacidla-zlav">
                            <button onclick="uplatnitClubcard()" style="background:#4f46e5;">💳 Skenovať Clubcard (-10%)</button>
                            <button onclick="uplatnitKupon()" style="background:#db2777;">🎟️ Použiť Kupón (-20%)</button>
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
                    async function obnovStranku() {
                        let res = await fetch('/api/stav');
                        let data = await res.json();
                        
                        // Vypísanie produktov (Tvoja podmienka na sklad)
                        let prodHtml = "";
                        data.produkty.forEach(p => {
                            let jeVypredane = p.sklad === 0;
                            let textSkladu = jeVypredane ? "VYPREDANÉ" : "sklad: " + p.sklad;
                            prodHtml += `
                                <div class="polozka">
                                    <div><strong>${p.nazov}</strong> - ${p.druh} - ${p.cena.toFixed(2)} €</div>
                                    <button onclick="kupit(${p.id})" ${jeVypredane ? 'disabled' : ''}>
                                        ${jeVypredane ? 'Vypredané' : 'Kúpiť (' + textSkladu + ')'}
                                    </button>
                                </div>`;
                        });
                        document.getElementById('produkty-box').innerHTML = prodHtml;

                        // Vypísanie košíka
                        let kosikHtml = data.kosik.length === 0 ? "<li>Košík je prázdny</li>" : "";
                        data.kosik.forEach(p => { kosikHtml += `<li>- ${p}</li>`; });
                        document.getElementById('kosik-box').innerHTML = kosikHtml;

                        // Aktualizácia celkovej ceny
                        document.getElementById('cena-box').innerText = data.celkova_cena.toFixed(2);
                    }

                    async function kupit(id) {
                        let res = await fetch('/api/kupit/' + id);
                        if(res.status === 200) {
                            alert("Produkt bol pridaný do košíka!");
                        }
                        obnovStranku();
                    }

                    async function uplatnitClubcard() {
                        await fetch('/api/clubcard');
                        alert("Clubcard bola naskenovaná! Uplatnená zľava 10 %.");
                        obnovStranku();
                    }

                    async function uplatnitKupon() {
                        await fetch('/api/kupon');
                        alert("Kupón bol použitý! Uplatnená zľava 20 %.");
                        obnovStranku();
                    }

                    async function zaplatit() {
                        let sposob = document.getElementById('platba').value;
                        let textPlatby = "";
                        
                        if(sposob === "1") {
                            textPlatby = "Platba hotovosťou bola zvolená.\\nZačnite vkladať hotovosť do pokladne.";
                        } else if(sposob === "2") {
                            textPlatby = "Platba kartou bola zvolená.\\nProsím, vložte kartu do čítačky a zadajte PIN.";
                        } else if(sposob === "3") {
                            textPlatby = "Platba kupónom bola zvolená.";
                        }
                        
                        alert(textPlatby + "\\n\\nĎakujeme za nákup!");
                        await fetch('/api/zaplatit');
                        obnovStranku();
                    }

                    // Prvé načítanie obchodu pri otvorení stránky
                    obnovStranku();
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

# Spustenie lokálneho servera
server = HTTPServer(("localhost", 8000), WebObchodBackend)
print("----------------------------------------------------------------")
print("🚀 Web server úspešne naštartoval!")
print("👉 Otvorte v prehliadači adresu: http://localhost:8000")
print("----------------------------------------------------------------")
server.serve_forever()