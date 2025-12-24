"""Xbox API client."""

from dataclasses import dataclass
from typing import Optional
import httpx

from .config import (
    API_PROFILE, API_TITLEHUB, API_USERSTATS, API_ACHIEVEMENTS,
    DEFAULT_TIMEOUT, DEFAULT_BATCH_SIZE
)


@dataclass
class XboxCredentials:
    """Xbox API credentials."""
    user_hash: str
    xsts_token: str
    xuid: str
    
    @classmethod
    def from_tokens(cls, tokens: dict) -> "XboxCredentials":
        return cls(
            user_hash=tokens["user_hash"],
            xsts_token=tokens["xsts_token"],
            xuid=tokens["xuid"]
        )
    
    def auth_header(self) -> str:
        return f"XBL3.0 x={self.user_hash};{self.xsts_token}"


class XboxAPI:
    """Xbox API client with common operations."""
    
    def __init__(self, credentials: XboxCredentials):
        self.creds = credentials
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        return self
    
    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()
    
    def _headers(self, version: str = "2") -> dict:
        return {
            "Authorization": self.creds.auth_header(),
            "x-xbl-contract-version": version,
            "Accept": "application/json",
            "Accept-Language": "pt-BR",
        }
    
    async def _get(self, url: str, version: str = "2") -> Optional[dict]:
        resp = await self.client.get(url, headers=self._headers(version))
        return resp.json() if resp.status_code == 200 else None
    
    async def _post(self, url: str, payload: dict, version: str = "2") -> Optional[dict]:
        headers = self._headers(version)
        headers["Content-Type"] = "application/json"
        resp = await self.client.post(url, json=payload, headers=headers)
        return resp.json() if resp.status_code == 200 else None
    
    async def get_profile(self, xuid: str = None) -> dict:
        """Fetch user profile."""
        xuid = xuid or self.creds.xuid
        url = f"{API_PROFILE}/users/xuid({xuid})/profile/settings?settings=GameDisplayPicRaw,Gamerscore,Gamertag,AccountTier"
        
        data = await self._get(url)
        if not data:
            return {}
        
        users = data.get("profileUsers", [])
        if not users:
            return {}
        
        settings = {s["id"]: s["value"] for s in users[0].get("settings", [])}
        return {
            "xuid": xuid,
            "gamertag": settings.get("Gamertag", ""),
            "gamerscore": settings.get("Gamerscore", "0"),
            "avatar_url": settings.get("GameDisplayPicRaw", ""),
        }
    
    async def get_xuid(self, gamertag: str) -> Optional[str]:
        """Get XUID from gamertag."""
        url = f"{API_PROFILE}/users/gt({gamertag})/profile/settings"
        data = await self._get(url)
        if data:
            users = data.get("profileUsers", [])
            if users:
                return users[0].get("id")
        return None
    
    async def get_games(self, xuid: str = None) -> list:
        """Fetch all games for user."""
        xuid = xuid or self.creds.xuid
        url = f"{API_TITLEHUB}/users/xuid({xuid})/titles/titlehistory/decoration/achievement,image,scid"
        
        data = await self._get(url)
        if not data:
            return []
        
        games = []
        for title in data.get("titles", []):
            if title.get("type") != "Game":
                continue
            
            ach = title.get("achievement", {})
            games.append({
                "id": str(title.get("titleId", "")),
                "name": title.get("name", "Unknown"),
                "last_played": title.get("titleHistory", {}).get("lastTimePlayed"),
                "current_gamerscore": ach.get("currentGamerscore", 0),
                "max_gamerscore": ach.get("totalGamerscore", 0),
                "achievements_unlocked": ach.get("currentAchievements", 0),
                "progress_percent": ach.get("progressPercentage", 0),
                "image": title.get("displayImage", ""),
            })
        
        return games
    
    async def get_playtime(self, xuid: str, title_ids: list) -> dict:
        """Fetch playtime for multiple games."""
        if not title_ids:
            return {}
        
        playtime = {}
        
        for i in range(0, len(title_ids), DEFAULT_BATCH_SIZE):
            batch = title_ids[i:i + DEFAULT_BATCH_SIZE]
            payload = {
                "arrangebyfield": "xuid",
                "stats": [{"name": "MinutesPlayed", "titleid": str(tid)} for tid in batch],
                "xuids": [str(xuid)]
            }
            
            data = await self._post(f"{API_USERSTATS}/batch", payload)
            if not data:
                continue
            
            for coll in data.get("statlistscollection", []):
                for stat in coll.get("stats", []):
                    if stat.get("name") == "MinutesPlayed":
                        tid = stat.get("titleid")
                        mins = int(stat.get("value", 0))
                        if tid:
                            playtime[str(tid)] = round(mins / 60.0, 1)
        
        return playtime
    
    async def get_achievements(self, xuid: str, title_id: str) -> list:
        """Fetch achievements for a game with rarity."""
        url = f"{API_ACHIEVEMENTS}/users/xuid({xuid})/achievements?titleId={title_id}&maxItems=1000"
        
        data = await self._get(url, version="4")
        if not data:
            return []
        
        achievements = []
        for a in data.get("achievements", []):
            unlocked = a.get("progression", {}).get("timeUnlocked")
            if not unlocked or unlocked == "0001-01-01T00:00:00Z":
                continue
            
            rarity = a.get("rarity", {})
            rewards = a.get("rewards", [{}])
            media = a.get("mediaAssets", [{}])
            
            achievements.append({
                "id": a.get("id"),
                "name": a.get("name", ""),
                "description": a.get("description", ""),
                "gamerscore": rewards[0].get("value", 0) if rewards else 0,
                "time_unlocked": unlocked,
                "rarity_percent": rarity.get("currentPercentage", 100),
                "rarity_category": rarity.get("currentCategory", "Common"),
                "title_id": title_id,
                "icon": media[0].get("url", "") if media else "",
            })
        
        return achievements

