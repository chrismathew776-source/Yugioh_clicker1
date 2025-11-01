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

# Godly tier cards - 3,500,000 coins each
godly_tier_cards = ["Obelisk the Tormentor", "The Winged Dragon of Ra", "Slifer the Sky Dragon", "Pot of Greed"]

def normalize_type(card_type):
    card_type = card_type.lower()
    if 'monster' in card_type:
        if 'xyz' in card_type:
            return 'XYZ'
        elif 'synchro' in card_type:
            return 'Synchro'
        elif 'fusion' in card_type:
            return 'Fusion'
        elif 'ritual' in card_type:
            return 'Ritual'
        else:
            return 'Normal'
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
# Main page template - WITH ZOOM
# ------------------------
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yu-Gi-Oh! Cards</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.3">
    
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3FC4FB4V8Y"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-3FC4FB4V8Y');
    </script>
    
    <style>
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #111; 
            color: white; 
            padding: 20px; 
            text-align:center; 
            transform: scale(1.3);
            transform-origin: top left;
            width: 75vw;
        }
        input[type=text], select { padding: 8px; border-radius:5px; border:none; margin-right:5px; }
        button { padding:8px 12px; border-radius:5px; border:none; background-color:#4CAF50; color:white; cursor:pointer; }
        button:hover { background-color:#45a049; }
        .cards-container { display:flex; flex-wrap:wrap; justify-content:center; gap:20px; margin-top:20px; }
        .card { background:#1a1a1a; border-radius:10px; padding:10px; width:200px; text-align:center; box-shadow:0 0 10px rgba(255,255,255,0.1); transition:transform 0.2s; }
        .card:hover { transform:scale(1.05); }
        .card img { width:100%; border-radius:8px; }
        .stats { display:flex; justify-content:space-around; margin-top:8px; }
        a.button { display:inline-block; padding:10px 20px; margin-top:10px; background-color:#4CAF50; color:white; border-radius:5px; text-decoration:none; margin:5px; }
        a.button:hover { background-color:#45a049; }
        .godly-tier { border: 3px solid gold; box-shadow: 0 0 15px gold; }
    </style>
</head>
<body>
    <h1>Yu-Gi-Oh! Card Search</h1>
    <div>
        <a href="/" class="button">Main Page</a>
        <a href="/second" class="button">Clicker & Shop</a>
        <a href="/third" class="button">Deck Builder</a>
    </div>
    <form id="searchForm">
        <input type="text" id="searchInput" placeholder="Search card name...">
        <select id="typeFilter">
            <option value="">All Types</option>
            <option value="Normal">Normal</option>
            <option value="XYZ">XYZ</option>
            <option value="Synchro">Synchro</option>
            <option value="Fusion">Fusion</option>
            <option value="Ritual">Ritual</option>
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
# Clicker page template - WITH ZOOM
# ------------------------
CLICKER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yu-Gi-Oh! Clicker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.3">
    
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3FC4FB4V8Y"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-3FC4FB4V8Y');
    </script>
    
    <style>
        body { 
            font-family:'Segoe UI',sans-serif;
            background:#0d0d0d;
            color:white;
            text-align:center;
            padding:20px;
            position:relative;
            transform: scale(1.3);
            transform-origin: top left;
            width: 75vw;
        }
        h1{color:#ffcc00;}
        .cards-container,.collection-container{display:flex;flex-wrap:wrap;justify-content:center;gap:15px;margin-top:20px;}
        .card{background:#1a1a1a;border-radius:10px;padding:10px;width:180px;text-align:center;box-shadow:0 0 10px rgba(255,255,255,0.1);transition:transform 0.2s;}
        .card:hover{transform:scale(1.05);}
        .card img{width:100%;border-radius:8px;}
        a.button{display:inline-block;padding:10px 20px;margin-top:10px;background-color:#4CAF50;color:white;border-radius:5px;text-decoration:none; margin:5px;}
        a.button:hover{background-color:#45a049;}
        #clickButton { width:257px; cursor:pointer; touch-action: manipulation; }
        #clickButton:active { opacity:0.8; }
        form { margin-bottom: 20px; }
        input[type=text], select { padding: 6px; border-radius:5px; border:none; margin-right:5px; }
        button { padding:6px 10px; border-radius:5px; border:none; background-color:#4CAF50; color:white; cursor:pointer; }
        button:hover { background-color:#45a049; }
        .godly-tier { border: 3px solid gold; box-shadow: 0 0 15px gold; }
    </style>
</head>
<body>
    <h1>Yu-Gi-Oh! Clicker</h1>
    <div>
        <a href="/" class="button">Main Page</a>
        <a href="/second" class="button">Clicker & Shop</a>
        <a href="/third" class="button">Deck Builder</a>
    </div>
    <div>
        <h2>Yugi Coins: <span id="coins">0</span></h2>
        <h3>Click Value: <span id="clickValue">1</span></h3>
        <img id="clickButton" src="https://ms.yugipedia.com//thumb/e/e5/Back-EN.png/257px-Back-EN.png" alt="Click Me!">
    </div>
    <form id="shopSearchForm">
        <input type="text" id="shopSearchInput" placeholder="Search card name...">
        <select id="shopTypeFilter">
            <option value="">All Types</option>
            <option value="Normal">Normal</option>
            <option value="XYZ">XYZ</option>
            <option value="Synchro">Synchro</option>
            <option value="Fusion">Fusion</option>
            <option value="Ritual">Ritual</option>
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
        const godlyTierCards = ["Obelisk the Tormentor", "The Winged Dragon of Ra", "Slifer the Sky Dragon", "Pot of Greed"];
        let shopLoading=false;
        let shopFilteredCards = allCards.slice();
        let searchTerm='';
        let typeTerm='';
        let atkTerm='';
        
        function getCardPrice(card){
            // Godly tier cards cost 3,500,000 coins
            if(godlyTierCards.includes(card.name)) return 3500000;
            
            const atk=card.atk||0;
            if(atk<=999) return 500;
            if(atk<=1999) return 2000;
            if(atk<=2999) return 10000;
            if(atk<=3999) return 25000;
            if(atk<=4999) return 50000;
            return 100000;
        }
        
        function getCardBoost(card){
            // Godly tier cards give massive boost
            if(godlyTierCards.includes(card.name)) return 10000;
            
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
                const isGodly = godlyTierCards.includes(card.name);
                cardDiv.className = isGodly ? 'card godly-tier' : 'card';
                cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>ATK: ${card.atk} | Boost: ${boost}X</p><p>Price: ${price.toLocaleString()} Yugi Coins</p><button onclick="buyCard(${allCards.indexOf(card)})">Buy</button>`;
                shopContainer.appendChild(cardDiv);
            });
            if(chunk.length>0) shopPage++;
            shopLoading=false;
            loadingShop.style.display='none';
        }
        
        window.addEventListener('scroll', ()=>{
            if(viewingPurchased) return;
            if(window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) loadShop();
        });
        
        function buyCard(index){
            const card = allCards[index];
            const price = getCardPrice(card);
            const boost = getCardBoost(card);
            if(coins >= price && !purchasedCards.includes(card)){
                coins -= price;
                purchasedCards.push(card);
                updateClickValue();
                updateCollection();
                updateDisplay();
                saveState();
            } else {
                alert('Not enough coins or already purchased!');
            }
        }
        
        function updateCollection(){
            collectionContainer.innerHTML='';
            purchasedCards.forEach(card=>{
                const cardDiv=document.createElement('div');
                const isGodly = godlyTierCards.includes(card.name);
                cardDiv.className = isGodly ? 'card godly-tier' : 'card';
                cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>Boost: ${getCardBoost(card)}X</p>`;
                collectionContainer.appendChild(cardDiv);
            });
        }
        
        function updateClickValue(){
            clickValue = purchasedCards.reduce((acc, c) => acc + getCardBoost(c), 0);
            if(clickValue===0) clickValue=1;
            clickValueDisplay.textContent = clickValue;
        }
        
        function updateDisplay(){coinsDisplay.textContent=coins.toLocaleString();}
        
        function addCoins(e){
            e.preventDefault();
            coins += clickValue;
            updateDisplay();
            saveState();
        }
        
        clickButton.addEventListener('click', addCoins);
        clickButton.addEventListener('touchstart', addCoins);
        
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
                const isGodly = godlyTierCards.includes(card.name);
                const cardDiv=document.createElement('div');
                cardDiv.className = isGodly ? 'card godly-tier' : 'card';
                cardDiv.innerHTML=`<img src="${card.img}" alt="${card.name}" loading="lazy"><h4>${card.name}</h4><p>ATK: ${card.atk} | Boost: ${boost}X</p>`;
                shopContainer.appendChild(cardDiv);
            });
        });
        
        loadState();
        loadShop();
        updateDisplay();
    </script>
</body>
</html>
"""

# ------------------------
# Deck Builder page template - WITH 30 MAIN + 15 EXTRA SLOTS AND RESTRICTIONS
# ------------------------
DECK_BUILDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yu-Gi-Oh! Deck Builder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.3">
    
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3FC4FB4V8Y"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-3FC4FB4V8Y');
    </script>
    
    <style>
        body { 
            font-family:'Segoe UI',sans-serif;
            background:#0d0d0d;
            color:white;
            padding:20px;
            transform: scale(1.3);
            transform-origin: top left;
            width: 75vw;
        }
        h1{color:#ffcc00;text-align:center;}
        .deck-section { 
            margin: 20px 0; 
            padding: 20px; 
            background: #1a1a1a; 
            border-radius: 10px;
        }
        .deck-container { 
            display: grid; 
            grid-template-columns: repeat(10, 1fr); 
            gap: 8px; 
            margin: 15px 0;
        }
        .extra-deck-container { 
            display: grid; 
            grid-template-columns: repeat(5, 1fr); 
            gap: 8px; 
            margin: 15px 0;
        }
        .deck-slot { 
            width: 70px; 
            height: 100px; 
            border: 2px dashed #444; 
            border-radius: 8px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            background: #2a2a2a; 
            transition: all 0.2s; 
            font-size: 10px;
            text-align: center;
        }
        .deck-slot:hover { border-color: #666; background: #333; }
        .deck-slot.drag-over { border-color: #4CAF50; background: #1e3a1e; }
        .deck-slot.occupied { border: 2px solid #4CAF50; }
        .deck-slot.invalid { border: 2px solid #ff4444; background: #3a1e1e; }
        .card { 
            background:#1a1a1a; 
            border-radius:8px; 
            padding:4px; 
            width:65px; 
            text-align:center; 
            box-shadow:0 0 10px rgba(255,255,255,0.1); 
            transition: all 0.2s; 
            cursor: grab;
            user-select: none;
        }
        .card:hover { transform:scale(1.05); }
        .card.dragging { 
            opacity: 0.7; 
            transform: rotate(5deg) scale(1.1);
            z-index: 1000;
            position: relative;
        }
        .card img { width:100%; border-radius:5px; }
        .collection-container { 
            display:flex; 
            flex-wrap:wrap; 
            justify-content:center; 
            gap:8px; 
            margin-top:15px; 
            max-height: 400px; 
            overflow-y: auto; 
            padding: 15px;
            background: #1a1a1a;
            border-radius: 10px;
        }
        a.button { 
            display:inline-block;
            padding:10px 20px; 
            margin:10px; 
            background-color:#4CAF50; 
            color:white; 
            border-radius:5px; 
            text-decoration:none; 
        }
        a.button:hover { background-color:#45a049; }
        .godly-tier { border: 2px solid gold; box-shadow: 0 0 10px gold; }
        .xyz-tier { border: 2px solid #9c27b0; box-shadow: 0 0 10px #9c27b0; }
        .fusion-tier { border: 2px solid #ff9800; box-shadow: 0 0 10px #ff9800; }
        .deck-count { 
            text-align: center; 
            margin: 10px 0; 
            font-size: 16px; 
            background: #2a2a2a;
            padding: 8px;
            border-radius: 5px;
        }
        .card-name { 
            font-size: 8px; 
            margin-top: 3px; 
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 60px;
        }
        .clear-deck { 
            background: #ff4444; 
            margin-left: 10px; 
        }
        .clear-deck:hover { 
            background: #cc0000; 
        }
        .rules-info {
            background: #2a2a2a;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>Yu-Gi-Oh! Deck Builder</h1>
    <div style="text-align:center;">
        <a href="/" class="button">Main Page</a>
        <a href="/second" class="button">Clicker & Shop</a>
        <a href="/third" class="button">Deck Builder</a>
    </div>
    
    <div class="rules-info">
        <strong>Deck Rules:</strong> Main Deck: 30 cards max (Normal/Spell/Trap only, max 3 copies each) | Extra Deck: 15 cards max (XYZ/Fusion only) | Godly Cards: 1 copy max
    </div>
    
    <div class="deck-count">
        Main Deck: <span id="mainDeckCount">0</span>/30 | Extra Deck: <span id="extraDeckCount">0</span>/15
        <button class="button clear-deck" onclick="clearDeck()">Clear Deck</button>
    </div>
    
    <div class="deck-section">
        <h2>Main Deck (Normal/Spell/Trap only)</h2>
        <div class="deck-container" id="mainDeckContainer"></div>
    </div>
    
    <div class="deck-section">
        <h2>Extra Deck (XYZ/Fusion only)</h2>
        <div class="extra-deck-container" id="extraDeckContainer"></div>
    </div>
    
    <h2>Your Collection (Drag cards to deck slots)</h2>
    <div class="collection-container" id="collectionContainer"></div>
    
    <script>
        const allCards = {{ all_cards|tojson }};
        const godlyTierCards = ["Obelisk the Tormentor", "The Winged Dragon of Ra", "Slifer the Sky Dragon", "Pot of Greed"];
        let purchasedCards = [];
        let currentMainDeck = Array(30).fill(null);
        let currentExtraDeck = Array(15).fill(null);
        let draggedCard = null;

        function loadDeckState() {
            const savedDeck = JSON.parse(localStorage.getItem('currentDeck') || '{"main":[],"extra":[]}');
            const savedCards = JSON.parse(localStorage.getItem('purchasedCards') || '[]');
            purchasedCards = allCards.filter(c => savedCards.includes(c.name));
            
            // Load main deck
            currentMainDeck = Array(30).fill(null);
            if (savedDeck.main) {
                savedDeck.main.forEach((cardName, index) => {
                    if (index < 30 && cardName) {
                        currentMainDeck[index] = purchasedCards.find(c => c.name === cardName) || null;
                    }
                });
            }
            
            // Load extra deck
            currentExtraDeck = Array(15).fill(null);
            if (savedDeck.extra) {
                savedDeck.extra.forEach((cardName, index) => {
                    if (index < 15 && cardName) {
                        currentExtraDeck[index] = purchasedCards.find(c => c.name === cardName) || null;
                    }
                });
            }
            
            renderDecks();
            renderCollection();
            updateDeckCounts();
        }

        function saveDeckState() {
            const deckData = {
                main: currentMainDeck.map(c => c ? c.name : null),
                extra: currentExtraDeck.map(c => c ? c.name : null)
            };
            localStorage.setItem('currentDeck', JSON.stringify(deckData));
        }

        function renderDecks() {
            renderMainDeck();
            renderExtraDeck();
        }

        function renderMainDeck() {
            const container = document.getElementById('mainDeckContainer');
            container.innerHTML = '';
            
            for (let i = 0; i < 30; i++) {
                const slot = document.createElement('div');
                slot.className = currentMainDeck[i] ? 'deck-slot occupied' : 'deck-slot';
                slot.id = `main-slot-${i}`;
                slot.setAttribute('data-slot-type', 'main');
                slot.setAttribute('data-slot-index', i);
                
                if (currentMainDeck[i]) {
                    const card = currentMainDeck[i];
                    const cardClass = getCardClass(card);
                    const cardDiv = createCardElement(card, 'main', i);
                    slot.appendChild(cardDiv);
                }
                
                setupSlotEvents(slot);
                container.appendChild(slot);
            }
        }

        function renderExtraDeck() {
            const container = document.getElementById('extraDeckContainer');
            container.innerHTML = '';
            
            for (let i = 0; i < 15; i++) {
                const slot = document.createElement('div');
                slot.className = currentExtraDeck[i] ? 'deck-slot occupied' : 'deck-slot';
                slot.id = `extra-slot-${i}`;
                slot.setAttribute('data-slot-type', 'extra');
                slot.setAttribute('data-slot-index', i);
                
                if (currentExtraDeck[i]) {
                    const card = currentExtraDeck[i];
                    const cardDiv = createCardElement(card, 'extra', i);
                    slot.appendChild(cardDiv);
                }
                
                setupSlotEvents(slot);
                container.appendChild(slot);
            }
        }

        function createCardElement(card, deckType, index) {
            const cardDiv = document.createElement('div');
            cardDiv.className = `card ${getCardClass(card)}`;
            cardDiv.draggable = true;
            cardDiv.setAttribute('data-deck-type', deckType);
            cardDiv.setAttribute('data-slot-index', index);
            cardDiv.innerHTML = `
                <img src="${card.img}" alt="${card.name}" loading="lazy">
                <div class="card-name">${card.name}</div>
            `;
            
            cardDiv.addEventListener('dragstart', handleDeckCardDragStart);
            cardDiv.addEventListener('dragend', handleDragEnd);
            return cardDiv;
        }

        function getCardClass(card) {
            if (godlyTierCards.includes(card.name)) return 'godly-tier';
            if (card.type === 'XYZ') return 'xyz-tier';
            if (card.type === 'Fusion') return 'fusion-tier';
            return '';
        }

        function setupSlotEvents(slot) {
            slot.addEventListener('dragover', handleDragOver);
            slot.addEventListener('dragenter', handleDragEnter);
            slot.addEventListener('dragleave', handleDragLeave);
            slot.addEventListener('drop', handleDrop);
        }

        function renderCollection() {
            const collectionContainer = document.getElementById('collectionContainer');
            collectionContainer.innerHTML = '';
            
            if (purchasedCards.length === 0) {
                collectionContainer.innerHTML = '<p>No cards purchased yet! Go to the Clicker page to buy cards.</p>';
                return;
            }
            
            purchasedCards.forEach((card) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = `card ${getCardClass(card)}`;
                cardDiv.draggable = true;
                cardDiv.setAttribute('data-card-name', card.name);
                cardDiv.setAttribute('data-card-type', card.type);
                cardDiv.innerHTML = `
                    <img src="${card.img}" alt="${card.name}" loading="lazy">
                    <div class="card-name">${card.name}</div>
                `;
                
                cardDiv.addEventListener('dragstart', handleCollectionCardDragStart);
                cardDiv.addEventListener('dragend', handleDragEnd);
                collectionContainer.appendChild(cardDiv);
            });
        }

        function handleCollectionCardDragStart(e) {
            draggedCard = {
                type: 'collection',
                name: e.target.getAttribute('data-card-name'),
                cardType: e.target.getAttribute('data-card-type')
            };
            e.target.classList.add('dragging');
            e.dataTransfer.setData('text/plain', JSON.stringify(draggedCard));
            e.dataTransfer.effectAllowed = 'copy';
        }

        function handleDeckCardDragStart(e) {
            const deckType = e.target.getAttribute('data-deck-type');
            const slotIndex = parseInt(e.target.getAttribute('data-slot-index'));
            draggedCard = {
                type: 'deck',
                deckType: deckType,
                slotIndex: slotIndex
            };
            e.target.classList.add('dragging');
            e.dataTransfer.setData('text/plain', JSON.stringify(draggedCard));
            e.dataTransfer.effectAllowed = 'move';
        }

        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        }

        function handleDragEnter(e) {
            e.preventDefault();
            if (e.target.classList.contains('deck-slot')) {
                e.target.classList.add('drag-over');
            }
        }

        function handleDragLeave(e) {
            if (e.target.classList.contains('deck-slot')) {
                e.target.classList.remove('drag-over');
            }
        }

        function handleDrop(e) {
            e.preventDefault();
            e.stopPropagation();
            
            document.querySelectorAll('.deck-slot.drag-over').forEach(slot => {
                slot.classList.remove('drag-over');
            });
            
            const slot = e.target.closest('.deck-slot');
            if (!slot) return;
            
            const slotType = slot.getAttribute('data-slot-type');
            const slotIndex = parseInt(slot.getAttribute('data-slot-index'));
            const data = e.dataTransfer.getData('text/plain');
            
            try {
                const dragData = JSON.parse(data);
                
                if (dragData.type === 'collection') {
                    // Validate card placement
                    if (!validateCardPlacement(dragData, slotType)) {
                        slot.classList.add('invalid');
                        setTimeout(() => slot.classList.remove('invalid'), 1000);
                        return;
                    }
                    
                    // Adding card from collection to deck
                    const card = purchasedCards.find(c => c.name === dragData.name);
                    if (card) {
                        if (slotType === 'main') {
                            currentMainDeck[slotIndex] = card;
                        } else {
                            currentExtraDeck[slotIndex] = card;
                        }
                        saveDeckState();
                        renderDecks();
                        updateDeckCounts();
                    }
                } else if (dragData.type === 'deck') {
                    // Moving card within deck
                    if (slotType !== dragData.deckType || slotIndex !== dragData.slotIndex) {
                        // Validate move between decks
                        const sourceDeck = dragData.deckType === 'main' ? currentMainDeck : currentExtraDeck;
                        const targetDeck = slotType === 'main' ? currentMainDeck : currentExtraDeck;
                        const card = sourceDeck[dragData.slotIndex];
                        
                        if (card && !validateCardTypeForDeck(card, slotType)) {
                            slot.classList.add('invalid');
                            setTimeout(() => slot.classList.remove('invalid'), 1000);
                            return;
                        }
                        
                        // Perform the move
                        sourceDeck[dragData.slotIndex] = null;
                        targetDeck[slotIndex] = card;
                        saveDeckState();
                        renderDecks();
                        updateDeckCounts();
                    }
                }
            } catch (error) {
                console.error('Drop error:', error);
            }
        }

        function validateCardPlacement(dragData, slotType) {
            const card = purchasedCards.find(c => c.name === dragData.name);
            if (!card) return false;
            
            return validateCardTypeForDeck(card, slotType) && 
                   validateCardLimits(card, slotType);
        }

        function validateCardTypeForDeck(card, slotType) {
            // Main deck can only have Normal, Spell, Trap
            if (slotType === 'main') {
                return ['Normal', 'Spell', 'Trap', 'Ritual', 'Synchro'].includes(card.type);
            }
            // Extra deck can only have XYZ, Fusion
            if (slotType === 'extra') {
                return ['XYZ', 'Fusion'].includes(card.type);
            }
            return false;
        }

        function validateCardLimits(card, slotType) {
            if (slotType === 'main') {
                // Check godly card limit
                if (godlyTierCards.includes(card.name)) {
                    const godlyCount = currentMainDeck.filter(c => c && godlyTierCards.includes(c.name)).length;
                    if (godlyCount >= 1) return false;
                }
                
                // Check general card limit (max 3 copies)
                const cardCount = currentMainDeck.filter(c => c && c.name === card.name).length;
                if (cardCount >= 3) return false;
            }
            return true;
        }

        function handleDragEnd(e) {
            document.querySelectorAll('.card.dragging').forEach(card => {
                card.classList.remove('dragging');
            });
            draggedCard = null;
            document.querySelectorAll('.deck-slot.drag-over').forEach(slot => {
                slot.classList.remove('drag-over');
            });
        }

        function clearDeck() {
            if (confirm('Are you sure you want to clear your entire deck?')) {
                currentMainDeck = Array(30).fill(null);
                currentExtraDeck = Array(15).fill(null);
                saveDeckState();
                renderDecks();
                updateDeckCounts();
            }
        }

        function updateDeckCounts() {
            const mainCount = currentMainDeck.filter(card => card !== null).length;
            const extraCount = currentExtraDeck.filter(card => card !== null).length;
            document.getElementById('mainDeckCount').textContent = mainCount;
            document.getElementById('extraDeckCount').textContent = extraCount;
        }

        // Allow dropping anywhere on the page (for removing cards)
        document.addEventListener('dragover', function(e) {
            e.preventDefault();
        });

        document.addEventListener('drop', function(e) {
            if (!e.target.closest('.deck-slot')) {
                e.preventDefault();
                const data = e.dataTransfer.getData('text/plain');
                try {
                    const dragData = JSON.parse(data);
                    if (dragData.type === 'deck') {
                        // Remove card from deck by dropping outside
                        if (dragData.deckType === 'main') {
                            currentMainDeck[dragData.slotIndex] = null;
                        } else {
                            currentExtraDeck[dragData.slotIndex] = null;
                        }
                        saveDeckState();
                        renderDecks();
                        updateDeckCounts();
                    }
                } catch (error) {
                    // Ignore non-JSON data
                }
            }
        });

        // Initialize
        loadDeckState();
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

@app.route("/third")
def third_page():
    return render_template_string(DECK_BUILDER_TEMPLATE, all_cards=all_cards)

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