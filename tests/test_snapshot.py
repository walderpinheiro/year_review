"""Tests for snapshot builder."""

import pytest
from src.snapshot import SnapshotBuilder


class MockAPI:
    """Mock Xbox API for testing."""
    
    def __init__(self):
        self.profile_data = {
            "xuid": "123",
            "gamertag": "MockPlayer",
            "gamerscore": "10000"
        }
        self.games_data = [
            {"id": "1", "name": "Game1", "achievements_unlocked": 5, "progress_percent": 50, "image": "http://img/1"},
            {"id": "2", "name": "Game2", "achievements_unlocked": 0, "progress_percent": 0, "image": "http://img/2"},
            {"id": "3", "name": "Game3", "achievements_unlocked": 10, "progress_percent": 100, "image": "http://img/3"}
        ]
        self.playtime_data = {"1": 10.5, "2": 0, "3": 25.0}
        self.achievements_data = {
            "1": [
                {"id": "a1", "name": "Ach1", "time_unlocked": "2024-01-15T00:00:00Z", "rarity_percent": 5.0}
            ],
            "3": [
                {"id": "a2", "name": "Ach2", "time_unlocked": "2024-06-20T00:00:00Z", "rarity_percent": 15.0}
            ]
        }
    
    async def get_profile(self, xuid):
        return self.profile_data
    
    async def get_games(self, xuid):
        return self.games_data.copy()
    
    async def get_playtime(self, xuid, title_ids):
        return self.playtime_data.copy()
    
    async def get_achievements(self, xuid, title_id):
        return self.achievements_data.get(title_id, [])


class TestSnapshotBuilder:
    @pytest.fixture
    def builder(self):
        api = MockAPI()
        return SnapshotBuilder(api, "123")
    
    @pytest.mark.asyncio
    async def test_fetch_profile(self, builder):
        profile = await builder.fetch_profile()
        
        assert profile["gamertag"] == "MockPlayer"
        assert builder.profile == profile
    
    @pytest.mark.asyncio
    async def test_fetch_games_sorted(self, builder):
        games = await builder.fetch_games()
        
        # Should be sorted by hours played (descending)
        assert games[0]["id"] == "3"  # 25 hours
        assert games[1]["id"] == "1"  # 10.5 hours
    
    @pytest.mark.asyncio
    async def test_fetch_achievements_skips_zero(self, builder):
        await builder.fetch_games()
        await builder.fetch_achievements(max_games=10)
        
        # Should skip game2 (0 achievements)
        assert len(builder.achievements) == 2
    
    @pytest.mark.asyncio
    async def test_build_stats(self, builder):
        await builder.fetch_profile()
        await builder.fetch_games()
        
        snapshot = builder.build()
        
        assert "statistics" in snapshot
        assert snapshot["statistics"]["total_games"] == 3
        assert snapshot["statistics"]["completed_games"] == 1
    
    @pytest.mark.asyncio
    async def test_build_by_month(self, builder):
        await builder.fetch_profile()
        await builder.fetch_games()
        await builder.fetch_achievements(max_games=10)
        
        snapshot = builder.build()
        
        assert "achievements_by_month" in snapshot
        assert "2024-01" in snapshot["achievements_by_month"]
        assert "2024-06" in snapshot["achievements_by_month"]

