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
# Main page template - WITH CHARACTERS
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
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #111;
            color: white; 
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
        }
        .character-left {
            width: 300px;
            background: url('https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/7d3b6e2d-5100-4cdf-8f4c-76c56c5d6c36/dg0p9hx-8c5e0a8c-3a4d-4e5f-8e5f-9c9b9c9b9c9b.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzdkM2I2ZTJkLTUxMDAtNGNkZi04ZjRjLTc2YzU2YzVkNmMzNlwvZGcwcDloeC04YzVlMGE4Yy0zYTRkLTRlNWYtOGU1Zi05YzliOWM5YjljOWIuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.8eKQ5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q') no-repeat center center;
            background-size: cover;
        }
        .character-right {
            width: 300px;
            background: url('https://i.pinimg.com/originals/47/82/26/478226054167700539.jpg') no-repeat center center;
            background-size: cover;
        }
        .main-content {
            flex: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.8);
            min-height: 100vh;
        }
        input[type=text], select { 
            padding: 8px; 
            border-radius:5px; 
            border:none; 
            margin-right:5px; 
        }
        button { 
            padding:8px 12px; 
            border-radius:5px; 
            border:none; 
            background-color:#4CAF50; 
            color:white; 
            cursor:pointer; 
        }
        button:hover { background-color:#45a049; }
        .cards-container { 
            display:flex; 
            flex-wrap:wrap; 
            justify-content:center; 
            gap:20px; 
            margin-top:20px; 
        }
        .card { 
            background:#1a1a1a; 
            border-radius:10px; 
            padding:10px; 
            width:200px; 
            text-align:center; 
            box-shadow:0 0 10px rgba(255,255,255,0.1); 
            transition:transform 0.2s; 
        }
        .card:hover { transform:scale(1.05); }
        .card img { width:100%; border-radius:8px; }
        .stats { display:flex; justify-content:space-around; margin-top:8px; }
        a.button { 
            display:inline-block;
            padding:10px 20px; 
            margin-top:10px; 
            background-color:#4CAF50; 
            color:white; 
            border-radius:5px; 
            text-decoration:none; 
            margin:5px; 
        }
        a.button:hover { background-color:#45a049; }
        .godly-tier { border: 3px solid gold; box-shadow: 0 0 15px gold; }
        h1 { text-align: center; color: #ffcc00; }
        .search-form { text-align: center; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="character-left"></div>
    
    <div class="main-content">
        <h1>Yu-Gi-Oh! Card Search</h1>
        <div style="text-align:center;">
            <a href="/" class="button">Main Page</a>
            <a href="/second" class="button">Clicker & Shop</a>
            <a href="/third" class="button">Deck Builder</a>
        </div>

        <form id="searchForm" class="search-form">
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
        <p id="loadingText" style="display:none; text-align:center;">Loading more cards...</p>

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
    </div>

    <div class="character-right"></div>
</body>
</html>
"""

# ------------------------
# Clicker page template - WITH EGYPTIAN GODS
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
        body { 
            font-family:'Segoe UI',sans-serif;
            background: 
                linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)),
                url('https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/a30a9a27-8dcd-4b26-8f75-4c246b3635e5/dfym0pr-6e9c1a9c-8d0a-4b5e-9e5e-5e5e5e5e5e5e.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2EzMGE5YTI3LThkY2QtNGIyNi04Zjc1LTRjMjQ2YjM2MzVlNVwvZGZ5bTBwci02ZTljMWE5Yy04ZDBhLTRiNWUtOWU1ZS01ZTVlNWU1ZTVlNWUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.8eKQ5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q') no-repeat center center fixed;
            background-size: cover;
            color:white;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        .clicker-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: rgba(0, 0, 0, 0.8);
            min-height: 100vh;
        }
        h1{color:#ffcc00; text-align: center;}
        .cards-container,.collection-container{
            display:flex;
            flex-wrap:wrap;
            justify-content:center;
            gap:15px;
            margin-top:20px;
        }
        .card{
            background:#1a1a1a;
            border-radius:10px;
            padding:10px;
            width:180px;
            text-align:center;
            box-shadow:0 0 10px rgba(255,255,255,0.1);
            transition:transform 0.2s;
        }
        .card:hover{transform:scale(1.05);}
        .card img{width:100%; border-radius:8px;}
        a.button{
            display:inline-block;
            padding:10px 20px;
            margin-top:10px;
            background-color:#4CAF50;
            color:white;
            border-radius:5px;
            text-decoration:none;
            margin:5px;
        }
        a.button:hover{background-color:#45a049;}
        #clickButton { 
            width:257px; 
            cursor:pointer; 
            touch-action: manipulation; 
            display: block;
            margin: 20px auto;
        }
        #clickButton:active { opacity:0.8; }
        form { 
            margin-bottom: 20px; 
            text-align: center;
        }
        input[type=text], select { 
            padding: 6px; 
            border-radius:5px; 
            border:none; 
            margin-right:5px; 
        }
        button { 
            padding:6px 10px; 
            border-radius:5px; 
            border:none; 
            background-color:#4CAF50; 
            color:white; 
            cursor:pointer; 
        }
        button:hover { background-color:#45a049; }
        .godly-tier { border: 3px solid gold; box-shadow: 0 0 15px gold; }
        .stats-display {
            text-align: center;
            margin: 20px 0;
            background: rgba(42, 42, 42, 0.9);
            padding: 15px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="clicker-content">
        <h1>Yu-Gi-Oh! Clicker</h1>
        <div style="text-align:center;">
            <a href="/" class="button">Main Page</a>
            <a href="/second" class="button">Clicker & Shop</a>
            <a href="/third" class="button">Deck Builder</a>
        </div>

        <div class="stats-display">
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
        <p id="loadingShop" style="display:none; text-align:center;">Loading more cards...</p>

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
    </div>
</body>
</html>
"""

# ------------------------
# Deck Builder page template - CLICK TO ADD SYSTEM
# ------------------------
DECK_BUILDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yu-Gi-Oh! Deck Builder</title>
    
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
            margin: 0;
            min-height: 100vh;
        }
        h1{color:#ffcc00;text-align:center;}
        .deck-container { 
            display: grid; 
            grid-template-columns: repeat(8, 1fr); 
            gap: 10px; 
            margin: 20px 0; 
            padding: 20px; 
            background: #1a1a1a; 
            border-radius: 10px; 
            min-height: 300px;
        }
        .deck-slot { 
            width: 80px; 
            height: 120px; 
            border: 2px dashed #444; 
            border-radius: 8px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            background: #2a2a2a; 
            transition: all 0.2s; 
            flex-direction: column;
        }
        .deck-slot:hover { border-color: #666; background: #333; }
        .deck-slot.occupied { border: 2px solid #4CAF50; }
        .card { 
            background:#1a1a1a; 
            border-radius:10px; 
            padding:5px; 
            width:70px; 
            text-align:center; 
            box-shadow:0 0 10px rgba(255,255,255,0.1); 
            transition: all 0.2s; 
            cursor: pointer;
            user-select: none;
        }
        .card:hover { transform:scale(1.05); }
        .card.selected { 
            border: 2px solid #ffcc00;
            box-shadow: 0 0 15px #ffcc00;
        }
        .card img { width:100%; border-radius:6px; }
        .collection-container { 
            display:flex; 
            flex-wrap:wrap; 
            justify-content:center; 
            gap:10px; 
            margin-top:20px; 
            max-height: 500px; 
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
        .godly-tier { border: 3px solid gold; box-shadow: 0 0 15px gold; }
        .deck-count { 
            text-align: center; 
            margin: 10px 0; 
            font-size: 18px; 
            background: #2a2a2a;
            padding: 10px;
            border-radius: 5px;
        }
        .card-name { 
            font-size: 10px; 
            margin-top: 5px; 
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 70px;
        }
        .clear-deck { 
            background: #ff4444; 
            margin-left: 10px; 
        }
        .clear-deck:hover { 
            background: #cc0000; 
        }
        .add-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 5px;
            font-size: 12px;
        }
        .add-button:hover {
            background: #45a049;
        }
        .remove-button {
            background: #ff4444;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 5px;
            font-size: 12px;
        }
        .remove-button:hover {
            background: #cc0000;
        }
        .instructions {
            text-align: center;
            margin: 10px 0;
            color: #ffcc00;
            font-size: 14px;
        }
        .deck-builder-content {
            max-width: 1400px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="deck-builder-content">
        <h1>Yu-Gi-Oh! Deck Builder</h1>
        <div style="text-align:center;">
            <a href="/" class="button">Main Page</a>
            <a href="/second" class="button">Clicker & Shop</a>
            <a href="/third" class="button">Deck Builder</a>
        </div>

        <div class="deck-count">
            Deck: <span id="deckCount">0</span>/40
            <button class="button clear-deck" onclick="clearDeck()">Clear Deck</button>
        </div>

        <div class="instructions">
            Click a card from your collection, then click "Add" on any empty deck slot to place it
        </div>
        
        <h2>Your Deck</h2>
        <div class="deck-container" id="deckContainer"></div>

        <h2>Your Collection (Click a card to select it)</h2>
        <div class="collection-container" id="collectionContainer"></div>

        <script>
            const allCards = {{ all_cards|tojson }};
            const godlyTierCards = ["Obelisk the Tormentor", "The Winged Dragon of Ra", "Slifer the Sky Dragon", "Pot of Greed"];
            let purchasedCards = [];
            let currentDeck = Array(40).fill(null);
            let selectedCard = null;

            function loadDeckState() {
                const savedDeck = JSON.parse(localStorage.getItem('currentDeck') || '[]');
                const savedCards = JSON.parse(localStorage.getItem('purchasedCards') || '[]');
                purchasedCards = allCards.filter(c => savedCards.includes(c.name));
                
                // Load deck, ensuring it's exactly 40 slots
                currentDeck = Array(40).fill(null);
                savedDeck.forEach((cardName, index) => {
                    if (index < 40 && cardName) {
                        currentDeck[index] = purchasedCards.find(c => c.name === cardName) || null;
                    }
                });
                
                renderDeck();
                renderCollection();
                updateDeckCount();
            }

            function saveDeckState() {
                localStorage.setItem('currentDeck', JSON.stringify(currentDeck.map(c => c ? c.name : null)));
            }

            function renderDeck() {
                const deckContainer = document.getElementById('deckContainer');
                deckContainer.innerHTML = '';
                
                for (let i = 0; i < 40; i++) {
                    const slot = document.createElement('div');
                    slot.className = currentDeck[i] ? 'deck-slot occupied' : 'deck-slot';
                    slot.id = `slot-${i}`;
                    
                    if (currentDeck[i]) {
                        const card = currentDeck[i];
                        const isGodly = godlyTierCards.includes(card.name);
                        const cardDiv = document.createElement('div');
                        cardDiv.className = `card ${isGodly ? 'godly-tier' : ''}`;
                        cardDiv.innerHTML = `
                            <img src="${card.img}" alt="${card.name}" loading="lazy">
                            <div class="card-name">${card.name}</div>
                            <button class="remove-button" onclick="removeCard(${i})">Remove</button>
                        `;
                        slot.appendChild(cardDiv);
                    } else {
                        // Empty slot - show add button if a card is selected
                        if (selectedCard) {
                            const addButton = document.createElement('button');
                            addButton.className = 'add-button';
                            addButton.textContent = 'Add Card';
                            addButton.onclick = () => addCardToSlot(i);
                            slot.appendChild(addButton);
                        } else {
                            slot.innerHTML = '<span style="color:#666; font-size:12px;">Empty</span>';
                        }
                    }
                    
                    deckContainer.appendChild(slot);
                }
            }

            function renderCollection() {
                const collectionContainer = document.getElementById('collectionContainer');
                collectionContainer.innerHTML = '';
                
                if (purchasedCards.length === 0) {
                    collectionContainer.innerHTML = '<p>No cards purchased yet! Go to the Clicker page to buy cards.</p>';
                    return;
                }
                
                purchasedCards.forEach((card) => {
                    const isGodly = godlyTierCards.includes(card.name);
                    const isSelected = selectedCard && selectedCard.name === card.name;
                    const cardDiv = document.createElement('div');
                    cardDiv.className = `card ${isGodly ? 'godly-tier' : ''} ${isSelected ? 'selected' : ''}`;
                    cardDiv.setAttribute('data-card-name', card.name);
                    cardDiv.innerHTML = `
                        <img src="${card.img}" alt="${card.name}" loading="lazy">
                        <div class="card-name">${card.name}</div>
                    `;
                    
                    cardDiv.addEventListener('click', () => selectCard(card));
                    collectionContainer.appendChild(cardDiv);
                });
            }

            function selectCard(card) {
                selectedCard = card;
                renderCollection();
                renderDeck();
            }

            function addCardToSlot(slotIndex) {
                if (selectedCard) {
                    currentDeck[slotIndex] = selectedCard;
                    saveDeckState();
                    renderDeck();
                    updateDeckCount();
                }
            }

            function removeCard(slotIndex) {
                currentDeck[slotIndex] = null;
                saveDeckState();
                renderDeck();
                updateDeckCount();
            }

            function clearDeck() {
                if (confirm('Are you sure you want to clear your entire deck?')) {
                    currentDeck = Array(40).fill(null);
                    saveDeckState();
                    renderDeck();
                    updateDeckCount();
                }
            }

            function updateDeckCount() {
                const count = currentDeck.filter(card => card !== null).length;
                document.getElementById('deckCount').textContent = count;
            }

            // Initialize
            loadDeckState();
        </script>
    </div>
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