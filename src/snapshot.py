"""Snapshot generator."""

import asyncio
from datetime import datetime
from typing import Optional

from .api import XboxAPI, XboxCredentials
from .utils import (
    load_tokens, save_snapshot, get_year_from_date, get_month_key
)
from .config import DEFAULT_MAX_GAMES


class SnapshotBuilder:
    """Builds achievement snapshot."""
    
    def __init__(self, api: XboxAPI, xuid: str):
        self.api = api
        self.xuid = xuid
        self.profile = {}
        self.games = []
        self.achievements = []
    
    async def fetch_profile(self):
        """Fetch user profile."""
        self.profile = await self.api.get_profile(self.xuid)
        return self.profile
    
    async def fetch_games(self):
        """Fetch games and playtime."""
        self.games = await self.api.get_games(self.xuid)
        
        title_ids = [g["id"] for g in self.games]
        playtime = await self.api.get_playtime(self.xuid, title_ids)
        
        for game in self.games:
            game["hours_played"] = playtime.get(game["id"], 0)
        
        self.games.sort(key=lambda x: x.get("hours_played", 0), reverse=True)
        return self.games
    
    async def fetch_achievements(self, max_games: int = DEFAULT_MAX_GAMES, callback=None):
        """Fetch achievements for top games."""
        self.achievements = []
        
        for i, game in enumerate(self.games[:max_games]):
            if game.get("achievements_unlocked", 0) == 0:
                continue
            
            if callback:
                callback(i + 1, max_games, game["name"])
            
            achs = await self.api.get_achievements(self.xuid, game["id"])
            for a in achs:
                a["game_name"] = game.get("name", "")
                a["game_image"] = game.get("image", "")
            
            self.achievements.extend(achs)
            await asyncio.sleep(0.1)
        
        self.achievements.sort(key=lambda x: x.get("rarity_percent", 100))
        return self.achievements
    
    def _compute_stats(self) -> dict:
        """Compute statistics."""
        return {
            "total_games": len(self.games),
            "total_hours": round(sum(g.get("hours_played", 0) for g in self.games), 1),
            "total_achievements": sum(g.get("achievements_unlocked", 0) for g in self.games),
            "total_gamerscore_earned": sum(g.get("current_gamerscore", 0) for g in self.games),
            "completed_games": sum(1 for g in self.games if g.get("progress_percent", 0) >= 100),
        }
    
    def _compute_by_year(self) -> dict:
        """Compute stats grouped by year."""
        by_year = {}
        for g in self.games:
            year = get_year_from_date(g.get("last_played", ""))
            if not year:
                continue
            
            if year not in by_year:
                by_year[year] = {"games": 0, "hours": 0, "achievements": 0, "gamerscore": 0, "completed": 0}
            
            by_year[year]["games"] += 1
            by_year[year]["hours"] += g.get("hours_played", 0)
            by_year[year]["achievements"] += g.get("achievements_unlocked", 0)
            by_year[year]["gamerscore"] += g.get("current_gamerscore", 0)
            if g.get("progress_percent", 0) >= 100:
                by_year[year]["completed"] += 1
        
        return by_year
    
    def _compute_by_month(self) -> dict:
        """Compute achievements grouped by month."""
        by_month = {}
        for a in self.achievements:
            key = get_month_key(a.get("time_unlocked", ""))
            if key:
                by_month[key] = by_month.get(key, 0) + 1
        return by_month
    
    def build(self) -> dict:
        """Build final snapshot."""
        return {
            "snapshot_date": datetime.now().isoformat(),
            "profile": self.profile,
            "statistics": self._compute_stats(),
            "by_year": self._compute_by_year(),
            "achievements_by_month": self._compute_by_month(),
            "games": self.games,
            "achievements_detailed": self.achievements,
            "rarest_achievements": self.achievements[:50],
        }


async def create_snapshot(
    target_xuid: str = None,
    target_gamertag: str = None,
    max_games: int = DEFAULT_MAX_GAMES
) -> Optional[dict]:
    """Create achievement snapshot."""
    tokens = load_tokens()
    creds = XboxCredentials.from_tokens(tokens)
    
    async with XboxAPI(creds) as api:
        # Resolve XUID
        if target_xuid:
            xuid = target_xuid
        elif target_gamertag:
            print(f"Looking up {target_gamertag}...")
            xuid = await api.get_xuid(target_gamertag)
            if not xuid:
                print(f"User not found: {target_gamertag}")
                return None
        else:
            xuid = creds.xuid
        
        print(f"XUID: {xuid}")
        
        builder = SnapshotBuilder(api, xuid)
        
        # Fetch data
        profile = await builder.fetch_profile()
        gamertag = profile.get("gamertag", "Unknown")
        print(f"Gamertag: {gamertag}")
        
        print("Fetching games...")
        games = await builder.fetch_games()
        print(f"Found {len(games)} games")
        
        print(f"Fetching achievements (top {max_games} games)...")
        
        def progress(current, total, name):
            print(f"  [{current}/{total}] {name[:40]}...")
        
        await builder.fetch_achievements(max_games, progress)
        print(f"Found {len(builder.achievements)} achievements")
        
        # Build and save
        snapshot = builder.build()
        files = save_snapshot(snapshot, gamertag)
        
        print(f"\nSaved: {files[0].name}")
        
        return snapshot

