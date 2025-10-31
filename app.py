from flask import Flask, render_template_string, request, jsonify
import requests

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
                div.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h3>${card.name}</h3><div class="stats"><span>ATK:${card.atk}</span><span>DEF:${card.defense}</span></div>`;
                container.appendChild(div);
            });
            if(data.length>0) page++;
            loading=false;
            loadingText.style.display='none';
        });
}

window.addEventListener('scroll', ()=>{
    if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) loadCards();
});

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
<style>
body { font-family:'Segoe UI',sans-serif;background:#0d0d0d;color:white;text-align:center;padding:20px;position:relative; }
h1{color:#ffcc00;}
.cards-container,.collection-container{display:flex;flex-wrap:wrap;justify-content:center;gap:15px;margin-top:20px;}
.card{background:#1a1a1a;border-radius:10px;padding:10px;width:180px;text-align:center;box-shadow:0 0 10px rgba(255,255,255,0.1);transition:transform 0.2s;}
.card:hover{transform:scale(1.05);}
.card img{width:100%;border-radius:8px;}
a.button{display:inline-block;padding:10px 20px;margin-top:10px;background-color:#4CAF50;color:white;border-radius:5px;text-decoration:none;}
a.button:hover{background-color:#45a049;}
#clickButton { width:257px; cursor:pointer; transition: transform 0.1s; }
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

// Price & boost functions
function getCardPrice(card){
    const atk=card.atk||0;
    if(atk<=999) return 500;
    if(atk<=1999) return 2000;
    if(atk<=2999) return 10000;
    if(atk<=3999) return 25000;
    if(atk<=4999) return 50000;
    return 100000;
}
function getCardBoost(card){
    const price = getCardPrice(card);
    const atk = card.atk || 0;
    if(price >= 100000) return 25;
    if(atk <= 999) return 8;
    if(atk <= 1999) return 16;
    if(atk <= 2999) return 50;
    if(atk <= 3999) return 120;
    if(atk <= 4999) return 250;
    return 500;
}

// Save/load
function saveState(){
    localStorage.setItem('coins', coins);
    localStorage.setItem('purchasedCards', JSON.stringify(purchasedCards.map(c=>c.name)));
}
function loadState(){
    const savedCoins = localStorage.getItem('coins');
    const savedCards = JSON.parse(localStorage.getItem('purchasedCards') || '[]');
    if(savedCoins) coins = parseInt(savedCoins);
    purchasedCards = allCards.filter(c => savedCards.includes(c.name));
    updateClickValue();
    updateCollection();
    updateDisplay();
}

// Load shop
function loadShop(){
    if(shopLoading || viewingPurchased) return;
    shopLoading = true;
    loadingShop.style.display='block';
    const start = shopPage*perPage;
    const end = start+perPage;
    const chunk = shopFilteredCards.slice(start,end);
    chunk.forEach(card=>{
        const price=getCardPrice(card);
        const boost=getCardBoost(card);
        const cardDiv=document.createElement('div');
        cardDiv.className='card';
        cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>ATK: ${card.atk} | Boost: ${boost}X</p><p>Price: ${price} Yugi Coins</p><button onclick="buyCard(${allCards.indexOf(card)})">Buy</button>`;
        shopContainer.appendChild(cardDiv);
    });
    if(chunk.length>0) shopPage++;
    shopLoading=false;
    loadingShop.style.display='none';
}

// Scroll listener
window.addEventListener('scroll', ()=>{
    if(viewingPurchased) return;
    if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) loadShop();
});

// Buy card
function buyCard(index){
    const card = allCards[index];
    const price = getCardPrice(card);
    const boost = getCardBoost(card);
    if(coins >= price && !purchasedCards.includes(card)){
        if(price >= 100000) coins = 0;
        else coins -= price;
        purchasedCards.push(card);
        updateClickValue();
        updateCollection();
        updateDisplay();
        saveState();
    } else {
        alert('Not enough coins or already purchased!');
    }
}

// Update collection and click value
function updateCollection(){
    collectionContainer.innerHTML='';
    purchasedCards.forEach(card=>{
        const cardDiv=document.createElement('div');
        cardDiv.className='card';
        cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>Boost: ${getCardBoost(card)}X</p>`;
        collectionContainer.appendChild(cardDiv);
    });
}
function updateClickValue(){
    clickValue = purchasedCards.reduce((acc, c) => acc + getCardBoost(c), 0);
    if(clickValue===0) clickValue=1;
    clickValueDisplay.textContent = clickValue;
}
function updateDisplay(){coinsDisplay.textContent=coins;}

// Click giant card
clickButton.addEventListener('click', ()=>{
    coins+=clickValue;
    updateDisplay();
    saveState();
    clickButton.style.transform='scale(0.95)';
    setTimeout(()=>{clickButton.style.transform='scale(1)';},100);
});

// Shop search/filter
document.getElementById('shopSearchForm').addEventListener('submit', e=>{
    e.preventDefault();
    viewingPurchased=false;
    searchTerm = document.getElementById('shopSearchInput').value.toLowerCase();
    typeTerm = document.getElementById('shopTypeFilter').value;
    atkTerm = document.getElementById('shopAtkFilter').value;
    shopFilteredCards = allCards.filter(c=>{
        let match=true;
        if(searchTerm) match = match && c.name.toLowerCase().includes(searchTerm);
        if(typeTerm) match = match && c.type===typeTerm;
        if(atkTerm){
            const atk=c.atk||0;
            if(atkTerm==='0-999') match = match && atk<=999;
            else if(atkTerm==='1000-1999') match = match && atk>=1000 && atk<=1999;
            else if(atkTerm==='2000-2999') match = match && atk>=2000 && atk<=2999;
            else if(atkTerm==='3000-3999') match = match && atk>=3000 && atk<=3999;
            else if(atkTerm==='4000-4999') match = match && atk>=4000 && atk<=4999;
            else if(atkTerm==='5000+') match = match && atk>=5000;
        }
        return match;
    });
    shopPage=0;
    shopContainer.innerHTML='';
    loadShop();
});

// Purchased Cards button
document.getElementById('showPurchasedBtn').addEventListener('click', ()=>{
    viewingPurchased=true;
    shopContainer.innerHTML='';
    shopPage=0;
    if(purchasedCards.length===0){
        shopContainer.innerHTML='<p>No cards purchased yet!</p>';
        return;
    }
    purchasedCards.forEach(card=>{
        const boost = getCardBoost(card);
        const cardDiv=document.createElement('div');
        cardDiv.className='card';
        cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>ATK: ${card.atk} | Boost: ${boost}X</p>`;
        shopContainer.appendChild(cardDiv);
    });
});

// Initial load
loadState();
loadShop();
updateDisplay();
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
    app.run(host="0.0.0.0", port=8080, debug=True)
