"""SVG share image generator."""

import base64
import urllib.request
from pathlib import Path
from typing import Optional

from .config import OUTPUT_DIR
from .utils import format_hours, format_number


def fetch_image_base64(url: str) -> Optional[str]:
    """Fetch image and encode as base64 data URI."""
    if not url:
        return None
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
            b64 = base64.b64encode(data).decode("utf-8")
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            return f"data:{content_type};base64,{b64}"
    except Exception:
        return None


class SVGGenerator:
    """Generates SVG share image for social media."""
    
    def __init__(self, data: dict):
        self.data = data
        self.profile = data.get("profile", {})
        self.stats = data.get("statistics", {})
        self.games = data.get("games", [])
    
    @property
    def gamertag(self) -> str:
        return self.profile.get("gamertag", "Unknown")
    
    @property
    def top_game(self) -> dict:
        return self.games[0] if self.games else {}
    
    @property
    def top3_games(self) -> list:
        return sorted(self.games, key=lambda x: x.get("hours_played", 0), reverse=True)[:3]
    
    def _generate_games_svg(self, images: dict) -> str:
        """Generate SVG for top 3 games cards."""
        games_svg = '<text x="850" y="170" fill="#2ECC40" font-size="22" font-weight="700" font-family="\'Bebas Neue\', sans-serif" letter-spacing="2">TOP 3 JOGOS</text>'
        
        for i, game in enumerate(self.top3_games):
            y_offset = 200 + i * 85
            name = game.get("name", "")[:20]
            hours = format_hours(game.get("hours_played", 0))
            img_b64 = images.get(game.get("name", ""))
            
            games_svg += f'''
    <rect x="850" y="{y_offset}" width="310" height="70" rx="12" fill="rgba(45,60,45,0.65)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
    {"<image x='862' y='" + str(y_offset + 10) + "' width='50' height='50' href='" + img_b64 + "'/>" if img_b64 else ""}
    <text x="922" y="{y_offset + 32}" fill="#fff" font-size="14" font-weight="600" font-family="'Space Grotesk', sans-serif">{name}</text>
    <text x="922" y="{y_offset + 52}" fill="#2ECC40" font-size="14" font-weight="700" font-family="'Space Grotesk', sans-serif">{hours}h</text>
'''
        return games_svg
    
    def generate(self) -> str:
        """Generate SVG content."""
        # Fetch images
        print("   📥 Baixando imagens para SVG...")
        images = {}
        
        top_game_image = fetch_image_base64(self.top_game.get("image", ""))
        avatar_b64 = fetch_image_base64(self.profile.get("avatar_url", ""))
        
        for game in self.top3_games:
            img = fetch_image_base64(game.get("image", ""))
            if img:
                images[game.get("name", "")] = img
        
        # Stats
        total_hours = self.stats.get("total_hours", 0)
        total_games = self.stats.get("total_games", 0)
        gamerscore = int(self.profile.get("gamerscore", 0))
        total_ach = self.stats.get("total_achievements", 0)
        
        games_svg = self._generate_games_svg(images)
        
        # Card layout
        card_width = 155
        card_gap = 15
        cards_start_x = 40
        
        svg = f'''<svg width="1200" height="600" viewBox="0 0 1200 600" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="30"/>
    </filter>
    <linearGradient id="overlay" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:rgba(16,124,16,0.25)"/>
      <stop offset="100%" style="stop-color:rgba(5,5,8,0.8)"/>
    </linearGradient>
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff"/>
      <stop offset="100%" style="stop-color:#888888"/>
    </linearGradient>
    <clipPath id="avatarClip">
      <circle cx="100" cy="100" r="45"/>
    </clipPath>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&amp;family=Space+Grotesk:wght@400;600;700&amp;display=swap');
    </style>
  </defs>
  
  <!-- Background with game image -->
  <rect width="1200" height="600" fill="#050508"/>
  {"<image x='-100' y='-100' width='1400' height='800' href='" + top_game_image + "' preserveAspectRatio='xMidYMid slice' filter='url(#blur)'/>" if top_game_image else ""}
  <rect width="1200" height="600" fill="url(#overlay)"/>
  
  <!-- Avatar and Gamertag - Top Left -->
  <g transform="translate(40, 40)">
    <circle cx="35" cy="35" r="35" fill="#107C10"/>
    {"<image x='0' y='0' width='70' height='70' href='" + avatar_b64 + "' clip-path='url(#avatarClip)' transform='translate(-65,-65)'/>" if avatar_b64 else ""}
    <text x="90" y="45" fill="#fff" font-size="28" font-weight="700" font-family="'Bebas Neue', sans-serif" letter-spacing="3">{self.gamertag.upper()}</text>
  </g>
  
  <!-- Title - Left -->
  <text x="40" y="200" fill="url(#titleGrad)" font-size="80" font-weight="700" font-family="'Bebas Neue', sans-serif">LIFETIME</text>
  <text x="40" y="280" fill="url(#titleGrad)" font-size="80" font-weight="700" font-family="'Bebas Neue', sans-serif">REVIEW</text>
  
  <!-- Stats Cards - Bottom Left -->
  <g>
    <rect x="{cards_start_x}" y="380" width="{card_width}" height="130" rx="16" fill="rgba(45,60,45,0.65)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
    <text x="{cards_start_x + card_width//2}" y="420" fill="#fff" font-size="20" text-anchor="middle">⏱️</text>
    <text x="{cards_start_x + card_width//2}" y="460" fill="#2ECC40" font-size="32" font-weight="700" text-anchor="middle">{format_hours(total_hours)}h</text>
    <text x="{cards_start_x + card_width//2}" y="490" fill="#8a8a9a" font-size="11" text-anchor="middle">TOTAL DE HORAS</text>
    
    <rect x="{cards_start_x + card_width + card_gap}" y="380" width="{card_width}" height="130" rx="16" fill="rgba(45,60,45,0.65)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
    <text x="{cards_start_x + card_width + card_gap + card_width//2}" y="420" fill="#fff" font-size="20" text-anchor="middle">🎮</text>
    <text x="{cards_start_x + card_width + card_gap + card_width//2}" y="460" fill="#2ECC40" font-size="32" font-weight="700" text-anchor="middle">{total_games}</text>
    <text x="{cards_start_x + card_width + card_gap + card_width//2}" y="490" fill="#8a8a9a" font-size="11" text-anchor="middle">JOGOS JOGADOS</text>
    
    <rect x="{cards_start_x + (card_width + card_gap)*2}" y="380" width="{card_width}" height="130" rx="16" fill="rgba(45,60,45,0.65)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
    <text x="{cards_start_x + (card_width + card_gap)*2 + card_width//2}" y="420" fill="#fff" font-size="20" text-anchor="middle">🏆</text>
    <text x="{cards_start_x + (card_width + card_gap)*2 + card_width//2}" y="460" fill="#2ECC40" font-size="32" font-weight="700" text-anchor="middle">{format_number(gamerscore)}G</text>
    <text x="{cards_start_x + (card_width + card_gap)*2 + card_width//2}" y="490" fill="#8a8a9a" font-size="11" text-anchor="middle">GAMERSCORE</text>
    
    <rect x="{cards_start_x + (card_width + card_gap)*3}" y="380" width="{card_width}" height="130" rx="16" fill="rgba(45,60,45,0.65)" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
    <text x="{cards_start_x + (card_width + card_gap)*3 + card_width//2}" y="420" fill="#fff" font-size="20" text-anchor="middle">🏅</text>
    <text x="{cards_start_x + (card_width + card_gap)*3 + card_width//2}" y="460" fill="#2ECC40" font-size="32" font-weight="700" text-anchor="middle">{format_number(total_ach)}</text>
    <text x="{cards_start_x + (card_width + card_gap)*3 + card_width//2}" y="490" fill="#8a8a9a" font-size="11" text-anchor="middle">CONQUISTAS</text>
  </g>
  
  <!-- Top 3 Games - Right Side -->
  {games_svg}
</svg>'''
        return svg
    
    def save(self) -> Path:
        """Generate and save SVG."""
        svg = self.generate()
        path = OUTPUT_DIR / f"share_{self.gamertag}.svg"
        path.write_text(svg, encoding="utf-8")
        return path


def generate_svg(data: dict) -> Path:
    """Generate SVG from data dict."""
    generator = SVGGenerator(data)
    return generator.save()

