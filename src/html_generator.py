"""HTML generator for lifetime review."""

import json
from datetime import datetime
from pathlib import Path

from .config import OUTPUT_DIR
from .utils import load_json, format_hours, format_number, parse_iso_date
from .svg_generator import generate_svg


class HTMLGenerator:
    """Generates lifetime review HTML."""
    
    def __init__(self, data: dict):
        self.data = data
        self.profile = data.get("profile", {})
        self.stats = data.get("statistics", {})
        self.games = data.get("games", [])
        self.achievements = data.get("achievements_detailed", [])
        self.by_year = data.get("by_year", {})
        self.by_month = data.get("achievements_by_month", {})
    
    @property
    def gamertag(self) -> str:
        return self.profile.get("gamertag", "Unknown")
    
    @property
    def top_game(self) -> dict:
        return self.games[0] if self.games else {}
    
    @property
    def top10_games(self) -> list:
        return sorted(self.games, key=lambda x: x.get("hours_played", 0), reverse=True)[:10]
    
    @property
    def rarest_achievements(self) -> list:
        unlocked = [
            a for a in self.achievements
            if a.get("time_unlocked") and not a["time_unlocked"].startswith("0001")
            and 0.01 <= a.get("rarity_percent", 100) < 50
        ]
        return sorted(unlocked, key=lambda x: x.get("rarity_percent", 100))[:10]
    
    @property
    def completed_games(self) -> list:
        done = [g for g in self.games if g.get("progress_percent", 0) >= 100]
        return sorted(done, key=lambda x: x.get("last_played", ""), reverse=True)[:20]
    
    @property
    def chart_data(self) -> tuple[list, list]:
        valid = sorted([m for m in self.by_month if len(m) == 7 and m[4] == '-'])
        labels = []
        values = []
        for m in valid:
            try:
                dt = datetime.strptime(m, "%Y-%m")
                labels.append(dt.strftime("%b/%y"))
            except:
                labels.append(m)
            values.append(self.by_month.get(m, 0))
        return labels, values
    
    def _game_card(self, rank: int, game: dict) -> str:
        cls = {1: "gold", 2: "silver", 3: "bronze"}.get(rank, "")
        return f'''<div class="game-card {cls}">
            <div class="rank">{rank}</div>
            <img src="{game.get('image','')}" class="thumb" onerror="this.src='https://via.placeholder.com/80'">
            <div class="info">
                <div class="name">{game.get('name','')}</div>
                <div class="meta"><span class="hours">{format_hours(game.get('hours_played',0))}h</span>
                <span class="tag">{game.get('achievements_unlocked',0)} ach</span></div>
                <div class="bar"><div class="fill" style="width:{game.get('progress_percent',0)}%"></div></div>
            </div>
        </div>'''
    
    def _ach_card(self, rank: int, ach: dict) -> str:
        r = ach.get("rarity_percent", 100)
        cls = "legendary" if r < 5 else "epic" if r < 15 else "rare" if r < 30 else ""
        
        dt = parse_iso_date(ach.get("time_unlocked", ""))
        date_str = dt.strftime("%d/%m/%Y") if dt else ""
        
        return f'''<div class="ach-card {cls}">
            <div class="rank">{rank}</div>
            <img src="{ach.get('icon','')}" class="icon" onerror="this.style.display='none'">
            <div class="info">
                <div class="name">{ach.get('name','')}</div>
                <div class="game">{ach.get('game_name','')}</div>
                <div class="desc">{ach.get('description','')[:60]}</div>
                {f'<div class="date">{date_str}</div>' if date_str else ''}
            </div>
            <div class="rarity">
                <div class="pct">{r:.1f}%</div>
                <div class="gs">{ach.get('gamerscore',0)}G</div>
            </div>
        </div>'''
    
    def _done_card(self, game: dict) -> str:
        return f'''<div class="done">
            <img src="{game.get('image','')}" onerror="this.style.display='none'">
            <div class="info"><div class="name">{game.get('name','')}</div>
            <div class="meta">{game.get('current_gamerscore',0)}G - {format_hours(game.get('hours_played',0))}h</div></div>
            <div class="badge">100%</div>
        </div>'''
    
    def generate(self) -> str:
        """Generate full HTML."""
        labels, values = self.chart_data
        top = self.top_game
        
        games_html = "".join(self._game_card(i, g) for i, g in enumerate(self.top10_games, 1))
        ach_html = "".join(self._ach_card(i, a) for i, a in enumerate(self.rarest_achievements, 1))
        done_html = "".join(self._done_card(g) for g in self.completed_games)
        
        description = f"{self.gamertag} - {format_hours(self.stats.get('total_hours',0))}h jogadas, {self.stats.get('total_games',0)} jogos, {format_number(self.stats.get('total_achievements',0))} conquistas"
        svg_url = f"share_{self.gamertag}.svg"
        share_url = f"https://twitter.com/intent/tweet?text={description.replace(' ', '%20')}&hashtags=Xbox,LifetimeReview"
        
        return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Xbox Lifetime Review - {self.gamertag}</title>

<!-- SEO -->
<meta name="description" content="{description}">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:title" content="Xbox Lifetime Review - {self.gamertag}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{svg_url}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Xbox Lifetime Review - {self.gamertag}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{svg_url}">

<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--g:#107C10;--gl:#2ECC40;--gold:#FFD700;--silver:#C0C0C0;--bronze:#CD7F32;--leg:#ff8000;--epic:#a335ee;--rare:#0070dd;--bg:#0a0a0f;--card:#141420;--t1:#fff;--t2:#8a8a9a}}
body{{font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--t1)}}

/* Share Button */
.share-btn{{
    position:fixed;top:20px;right:20px;z-index:1000;
    background:linear-gradient(135deg,var(--g),var(--gl));
    color:#fff;border:none;padding:12px 20px;border-radius:50px;
    font-family:'Space Grotesk',sans-serif;font-size:.9rem;font-weight:600;
    cursor:pointer;box-shadow:0 5px 20px rgba(16,124,16,.4);
    display:flex;align-items:center;gap:8px;
    transition:transform .2s,box-shadow .2s
}}
.share-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(16,124,16,.5)}}
.share-btn svg{{width:18px;height:18px}}

/* Hero */
.hero{{position:relative;min-height:100vh;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.hero-bg{{position:absolute;inset:0;background:url('{top.get("image","")}') center/cover;filter:blur(15px) brightness(.5);transform:scale(1.15);z-index:1}}
.hero-ov{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(16,124,16,.25),rgba(10,30,15,.6) 40%,rgba(10,10,15,1));z-index:2}}
.hero-c{{position:relative;z-index:10;text-align:center;padding:40px;max-width:1000px}}
.profile{{display:flex;align-items:center;justify-content:center;gap:20px;margin-bottom:30px}}
.avatar{{width:100px;height:100px;border-radius:50%;border:3px solid var(--g);box-shadow:0 0 30px rgba(16,124,16,.5)}}
.gt{{font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:2px}}
.title{{font-family:'Bebas Neue',sans-serif;font-size:7rem;line-height:.9;background:linear-gradient(180deg,#fff,#888);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:50px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:50px}}
.stat{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:25px}}
.stat-i{{font-size:2rem;margin-bottom:10px}}.stat-v{{font-size:2.5rem;font-weight:700;color:var(--gl)}}.stat-l{{font-size:.85rem;color:var(--t2);text-transform:uppercase}}
.top-badge{{display:inline-flex;align-items:center;gap:15px;background:linear-gradient(135deg,var(--g),var(--gl));padding:15px 30px;border-radius:50px}}
.top-badge img{{width:50px;height:50px;border-radius:8px}}

/* Sections */
.section{{padding:80px 40px;max-width:1200px;margin:0 auto}}
.sec-title{{font-family:'Bebas Neue',sans-serif;font-size:3rem;text-align:center;margin-bottom:50px;background:linear-gradient(90deg,var(--gl),var(--g));-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.grid{{display:flex;flex-direction:column;gap:15px}}
.game-card,.ach-card{{display:flex;align-items:center;gap:20px;background:var(--card);border-radius:12px;padding:15px 20px;border:1px solid rgba(255,255,255,.05);transition:transform .3s}}
.game-card:hover,.ach-card:hover{{transform:translateX(10px)}}
.game-card.gold{{border-left:4px solid var(--gold)}}.game-card.silver{{border-left:4px solid var(--silver)}}.game-card.bronze{{border-left:4px solid var(--bronze)}}
.rank{{font-family:'Bebas Neue',sans-serif;font-size:2.5rem;width:50px;text-align:center;color:var(--t2)}}
.game-card.gold .rank{{color:var(--gold)}}.game-card.silver .rank{{color:var(--silver)}}.game-card.bronze .rank{{color:var(--bronze)}}
.thumb{{width:80px;height:80px;object-fit:cover;border-radius:8px}}
.info{{flex:1}}.name{{font-size:1.2rem;font-weight:600;margin-bottom:5px}}
.hours{{font-size:1.5rem;font-weight:700;color:var(--gl)}}
.meta{{display:flex;align-items:center;gap:15px;margin-bottom:10px}}
.tag{{background:rgba(16,124,16,.3);color:var(--gl);padding:4px 10px;border-radius:20px;font-size:.85rem}}
.bar{{height:8px;background:rgba(255,255,255,.1);border-radius:4px;overflow:hidden}}
.fill{{height:100%;background:linear-gradient(90deg,var(--g),var(--gl));border-radius:4px}}
.ach-card.legendary{{border-left:4px solid var(--leg)}}.ach-card.epic{{border-left:4px solid var(--epic)}}.ach-card.rare{{border-left:4px solid var(--rare)}}
.ach-card.legendary .rank,.ach-card.legendary .pct{{color:var(--leg)}}
.ach-card.epic .rank,.ach-card.epic .pct{{color:var(--epic)}}
.ach-card.rare .rank,.ach-card.rare .pct{{color:var(--rare)}}
.icon{{width:60px;height:60px;border-radius:8px;object-fit:cover}}
.game{{font-size:.85rem;color:var(--gl)}}.desc{{font-size:.8rem;color:var(--t2)}}.date{{font-size:.75rem;color:var(--gl);margin-top:5px}}
.rarity{{text-align:right;min-width:80px}}.pct{{font-size:1.5rem;font-weight:700}}.gs{{font-size:.9rem;color:var(--gold);margin-top:5px}}
.chart-sec{{background:var(--card);border-radius:20px;padding:40px;margin:80px auto;max-width:1100px}}
.chart-box{{position:relative;height:350px}}
.done-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px}}
.done{{display:flex;align-items:center;gap:12px;background:var(--card);border-radius:10px;padding:12px;border:1px solid var(--g)}}
.done img{{width:50px;height:50px;border-radius:6px;object-fit:cover}}
.done .info{{flex:1}}.done .name{{font-size:.95rem;font-weight:600}}.done .meta{{font-size:.8rem;color:var(--t2)}}
.badge{{font-weight:700;color:var(--gl);background:rgba(16,124,16,.2);padding:5px 10px;border-radius:6px}}
.footer{{text-align:center;padding:40px;color:var(--t2);font-size:.85rem}}
@media(max-width:768px){{.title{{font-size:4rem}}.stats{{grid-template-columns:repeat(2,1fr)}}.section{{padding:60px 20px}}.share-btn{{bottom:20px;right:20px;padding:12px 20px}}}}
</style>
</head>
<body>

<!-- Share Button -->
<button class="share-btn" onclick="shareReview()">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13"/></svg>
    Compartilhar
</button>

<section class="hero">
<div class="hero-bg"></div><div class="hero-ov"></div>
<div class="hero-c">
<div class="profile"><img src="{self.profile.get('avatar_url','')}" class="avatar" onerror="this.style.display='none'"><h1 class="gt">{self.gamertag}</h1></div>
<h2 class="title">LIFETIME<br>REVIEW</h2>
<div class="stats">
<div class="stat"><div class="stat-i">⏱️</div><div class="stat-v">{format_hours(self.stats.get('total_hours',0))}h</div><div class="stat-l">Horas</div></div>
<div class="stat"><div class="stat-i">🎮</div><div class="stat-v">{self.stats.get('total_games',0)}</div><div class="stat-l">Jogos</div></div>
<div class="stat"><div class="stat-i">🏆</div><div class="stat-v">{format_number(int(self.profile.get('gamerscore','0')))}G</div><div class="stat-l">Gamerscore</div></div>
<div class="stat"><div class="stat-i">🏅</div><div class="stat-v">{format_number(self.stats.get('total_achievements',0))}</div><div class="stat-l">Conquistas</div></div>
</div>
<div class="top-badge"><img src="{top.get('image','')}" onerror="this.style.display='none'"><div><div style="font-size:.75rem;opacity:.8">Mais jogado</div><div style="font-weight:700">{top.get('name','N/A')} - {format_hours(top.get('hours_played',0))}h</div></div></div>
</div>
</section>
<section class="section"><h2 class="sec-title">TOP 10 JOGOS</h2><div class="grid">{games_html}</div></section>
<section class="section"><h2 class="sec-title">TOP 10 CONQUISTAS RARAS</h2><div class="grid">{ach_html}</div></section>
<div class="chart-sec"><h2 class="sec-title" style="margin-bottom:30px">CONQUISTAS POR MES</h2><div class="chart-box"><canvas id="chart"></canvas></div></div>
<section class="section"><h2 class="sec-title">JOGOS 100% ({self.stats.get('completed_games',0)})</h2><div class="done-grid">{done_html}</div></section>
<footer class="footer">{datetime.now().strftime("%d/%m/%Y")} - {self.gamertag}</footer>

<script>
const ctx=document.getElementById('chart').getContext('2d');
const grd=ctx.createLinearGradient(0,0,0,350);grd.addColorStop(0,'rgba(46,204,64,.5)');grd.addColorStop(1,'rgba(46,204,64,0)');
new Chart(ctx,{{type:'line',data:{{labels:{json.dumps(labels)},datasets:[{{data:{json.dumps(values)},borderColor:'#2ECC40',backgroundColor:grd,fill:true,tension:.4,pointRadius:4}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#8a8a9a'}}}},y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,.05)'}},ticks:{{color:'#8a8a9a'}}}}}}}}}});

function shareReview() {{
    const text = "Xbox Lifetime Review - {self.gamertag}\\n{format_hours(self.stats.get('total_hours',0))}h jogadas, {self.stats.get('total_games',0)} jogos, {format_number(self.stats.get('total_achievements',0))} conquistas";
    const url = window.location.href;
    
    if (navigator.share) {{
        navigator.share({{ title: 'Xbox Lifetime Review', text: text, url: url }}).catch(() => {{}});
    }} else {{
        window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(text) + '&hashtags=Xbox,LifetimeReview', '_blank');
    }}
}}
</script>
</body>
</html>'''
    
    def save(self) -> tuple[Path, Path]:
        """Generate and save HTML and SVG."""
        html = self.generate()
        html_path = OUTPUT_DIR / f"lifetime_review_{self.gamertag}.html"
        html_path.write_text(html, encoding="utf-8")
        
        # Generate SVG share image
        svg_path = generate_svg(self.data)
        
        return html_path, svg_path


def generate_html(snapshot_file: str) -> tuple[Path, Path]:
    """Generate HTML and SVG from snapshot file."""
    filepath = OUTPUT_DIR / snapshot_file
    if not filepath.exists():
        filepath = OUTPUT_DIR / f"{snapshot_file}.json"
    
    data = load_json(filepath)
    generator = HTMLGenerator(data)
    html_path, svg_path = generator.save()
    
    print(f"   📄 HTML: {html_path}")
    print(f"   🖼️  SVG: {svg_path}")
    return html_path, svg_path
