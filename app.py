from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# ------------------------
# Fetch all cards at startup
# ------------------------
API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
response = requests.get(API_URL)
all_cards = []

def normalize_type(card_type):
    card_type = card_type.lower()
    if 'monster' in card_type:
        return 'Monster'
    elif 'spell' in card_type:
        return 'Spell'
    elif 'trap' in card_type:
        return 'Trap'
    return 'Unknown'

if response.status_code == 200:
    for card_data in response.json().get("data", []):
        all_cards.append({
            "name": card_data.get("name", "Unknown"),
            "type": normalize_type(card_data.get("type", "Unknown")),
            "atk": card_data.get("atk", 0) or 0,
            "defense": card_data.get("def", "N/A"),
            "img": card_data["card_images"][0]["image_url"]
        })

# ------------------------
# Main page template
# ------------------------
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Yu-Gi-Oh! Cards</title>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3FC4FB4V8Y"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-3FC4FB4V8Y');
</script>

<style>
body { font-family: 'Segoe UI', sans-serif; background: #111; color: white; padding: 20px; text-align:center; }
input[type=text], select { padding: 8px; border-radius:5px; border:none; margin-right:5px; }
button { padding:8px 12px; border-radius:5px; border:none; background-color:#4CAF50; color:white; cursor:pointer; }
button:hover { background-color:#45a049; }
.cards-container { display:flex; flex-wrap:wrap; justify-content:center; gap:20px; margin-top:20px; }
.card { background:#1a1a1a; border-radius:10px; padding:10px; width:200px; text-align:center; box-shadow:0 0 10px rgba(255,255,255,0.1); transition:transform 0.2s; }
.card:hover { transform:scale(1.05); }
.card img { width:100%; border-radius:8px; }
.stats { display:flex; justify-content:space-around; margin-top:8px; }
a.button { display:inline-block; padding:10px 20px; margin-top:10px; background-color:#4CAF50; color:white; border-radius:5px; text-decoration:none; }
a.button:hover { background-color:#45a049; }
</style>
</head>
<body>
<h1>Yu-Gi-Oh! Card Search</h1>

<a href="/second" class="button">Go to Clicker Page</a>

<form id="searchForm">
  <input type="text" id="searchInput" placeholder="Search card name...">
  <select id="typeFilter">
    <option value="">All</option>
    <option value="Monster">Monster</option>
    <option value="Spell">Spell</option>
    <option value="Trap">Trap</option>
  </select>
  <select id="atkFilter">
    <option value="">All ATK</option>
    <option value="0-999">0-999</option>
    <option value="1000-1999">1000-1999</option>
    <option value="2000-2999">2000-2999</option>
    <option value="3000-3999">3000-3999</option>
    <option value="4000-4999">4000-4999</option>
    <option value="5000+">5000+</option>
  </select>
  <button type="submit">Search</button>
</form>

<div class="cards-container" id="cardsContainer"></div>
<p id="loadingText" style="display:none;">Loading more cards...</p>

<script>
let page = 0;
const perPage = 200;
let loading = false;
let searchTerm = '';
let typeTerm = '';
let atkTerm = '';
const container = document.getElementById('cardsContainer');
const loadingText = document.getElementById('loadingText');

function loadCards() {
    if(loading) return;
    loading = true;
    loadingText.style.display = 'block';
    fetch(`/load_cards?page=${page}&search=${searchTerm}&type=${typeTerm}&atk=${atkTerm}`)
        .then(res => res.json())
        .then(data=>{
            data.forEach(card=>{
                const div = document.createElement('div');
                div.className='card';
                div.innerHTML=\`<img src="\${card.img}" alt="\${card.name}" loading="lazy"><h3>\${card.name}</h3><div class="stats"><span>ATK:\${card.atk}</span><span>DEF:\${card.defense}</span></div>\`;
                container.appendChild(div);
            });
            if(data.length>0) page++;
            loading=false;
            loadingText.style.display='none';
        });
}

window.addEventListener('scroll', ()=>{ if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) loadCards(); });

document.getElementById('searchForm').addEventListener('submit', e=>{
    e.preventDefault();
    searchTerm = document.getElementById('searchInput').value.toLowerCase();
    typeTerm = document.getElementById('typeFilter').value;
    atkTerm = document.getElementById('atkFilter').value;
    page=0;
    container.innerHTML='';
    window.scrollTo({top:0,behavior:'smooth'});
    loadCards();
});

loadCards();
</script>
</body>
</html>
"""

# ------------------------
# Clicker page template
# ------------------------
CLICKER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Yu-Gi-Oh! Clicker</title>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3FC4FB4V8Y"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-3FC4FB4V8Y');
</script>

<style>
body { font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:white;text-align:center;padding:20px;position:relative; }
h1{color:#ffcc00;}
.cards-container,.collection-container{display:flex;flex-wrap:wrap;justify-content:center;gap:15px;margin-top:20px;}
.card{background:#1a1a1a;border-radius:10px;padding:10px;width:180px;text-align:center;box-shadow:0 0 10px rgba(255,255,255,0.1);transition:transform 0.2s;}
.card:hover{transform:scale(1.05);}
.card img{width:100%;border-radius:8px;}
a.button{display:inline-block;padding:10px 20px;margin-top:10px;background-color:#4CAF50;color:white;border-radius:5px;text-decoration:none;}
a.button:hover{background-color:#45a049;}
#clickButton { width:257px; cursor:pointer; touch-action: manipulation; }
#clickButton:active { opacity:0.8; }
form { margin-bottom: 20px; }
input[type=text], select { padding: 6px; border-radius:5px; border:none; margin-right:5px; }
button { padding:6px 10px; border-radius:5px; border:none; background-color:#4CAF50; color:white; cursor:pointer; }
button:hover { background-color:#45a049; }
</style>
</head>
<body>
<h1>Yu-Gi-Oh! Clicker</h1>
<a href="/" class="button">Back to Main Page</a>

<div>
<h2>Yugi Coins: <span id="coins">0</span></h2>
<h3>Click Value: <span id="clickValue">1</span></h3>
<img id="clickButton" src="https://ms.yugipedia.com//thumb/e/e5/Back-EN.png/257px-Back-EN.png" alt="Click Me!">
</div>

<form id="shopSearchForm">
  <input type="text" id="shopSearchInput" placeholder="Search card name...">
  <select id="shopTypeFilter">
    <option value="">All</option>
    <option value="Monster">Monster</option>
    <option value="Spell">Spell</option>
    <option value="Trap">Trap</option>
  </select>
  <select id="shopAtkFilter">
    <option value="">All ATK</option>
    <option value="0-999">0-999</option>
    <option value="1000-1999">1000-1999</option>
    <option value="2000-2999">2000-2999</option>
    <option value="3000-3999">3000-3999</option>
    <option value="4000-4999">4000-4999</option>
    <option value="5000+">5000+</option>
  </select>
  <button type="submit">Search</button>
  <button type="button" id="showPurchasedBtn">Purchased Cards</button>
</form>

<h2>Shop</h2>
<div class="cards-container" id="shop"></div>
<p id="loadingShop" style="display:none;">Loading more cards...</p>

<h2>Collection</h2>
<div class="collection-container" id="collection"></div>

<script>
let coins=0;
let clickValue=1;
let purchasedCards=[];
let shopPage=0;
let viewingPurchased=false;
const perPage=50;
const shopContainer=document.getElementById('shop');
const collectionContainer=document.getElementById('collection');
const coinsDisplay=document.getElementById('coins');
const clickValueDisplay=document.getElementById('clickValue');
const clickButton=document.getElementById('clickButton');
const loadingShop=document.getElementById('loadingShop');
const allCards={{ all_cards|tojson }};
let shopLoading=false;
let shopFilteredCards = allCards.slice();
let searchTerm='';
let typeTerm='';
let atkTerm='';

// same clicker JS as before ...
</script>
</body>
</html>
"""

# ------------------------
# Routes
# ------------------------
@app.route("/")
def main_page():
    return render_template_string(MAIN_TEMPLATE)

@app.route("/second")
def second_page():
    return render_template_string(CLICKER_TEMPLATE, all_cards=all_cards)

@app.route("/load_cards")
def load_cards():
    page=int(request.args.get("page",0))
    per_page=200
    search=request.args.get("search","").strip().lower()
    type_filter=request.args.get("type","").strip()
    atk_filter=request.args.get("atk","").strip()

    filtered=all_cards
    if search: filtered=[c for c in filtered if search in c['name'].lower()]
    if type_filter: filtered=[c for c in filtered if c['type']==type_filter]
    if atk_filter:
        def atk_check(a):
            atk = a['atk'] or 0
            if atk_filter=='0-999': return atk<=999
            if atk_filter=='1000-1999': return atk>=1000 and atk<=1999
            if atk_filter=='2000-2999': return atk>=2000 and atk<=2999
            if atk_filter=='3000-3999': return atk>=3000 and atk<=3999
            if atk_filter=='4000-4999': return atk>=4000 and atk<=4999
            if atk_filter=='5000+': return atk>=5000
            return True
        filtered=[c for c in filtered if atk_check(c)]

    start=page*per_page
    end=start+per_page
    return jsonify(filtered[start:end])

# ------------------------
# Run server
# ------------------------
if __name__=="__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)


  