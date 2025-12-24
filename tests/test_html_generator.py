"""Tests for HTML generator."""

import pytest
from src.html_generator import HTMLGenerator


@pytest.fixture
def sample_data():
    return {
        "profile": {
            "gamertag": "TestPlayer",
            "gamerscore": "50000",
            "avatar_url": "http://example.com/avatar.png"
        },
        "statistics": {
            "total_games": 100,
            "total_hours": 1234.5,
            "total_achievements": 500,
            "completed_games": 10
        },
        "games": [
            {
                "id": "1",
                "name": "Game One",
                "hours_played": 100.5,
                "achievements_unlocked": 20,
                "progress_percent": 80,
                "image": "http://example.com/game1.png",
                "current_gamerscore": 500
            },
            {
                "id": "2",
                "name": "Game Two",
                "hours_played": 50.0,
                "achievements_unlocked": 10,
                "progress_percent": 100,
                "image": "http://example.com/game2.png",
                "current_gamerscore": 1000
            }
        ],
        "achievements_detailed": [
            {
                "id": "a1",
                "name": "Rare Achievement",
                "description": "Very rare",
                "gamerscore": 50,
                "time_unlocked": "2024-06-15T10:30:00Z",
                "rarity_percent": 2.5,
                "game_name": "Game One",
                "icon": "http://example.com/ach1.png"
            },
            {
                "id": "a2",
                "name": "Common Achievement",
                "description": "Easy one",
                "gamerscore": 10,
                "time_unlocked": "2024-01-01T00:00:00Z",
                "rarity_percent": 75.0,
                "game_name": "Game Two",
                "icon": ""
            }
        ],
        "by_year": {
            "2023": {"games": 10, "hours": 100},
            "2024": {"games": 50, "hours": 500}
        },
        "achievements_by_month": {
            "2024-01": 15,
            "2024-06": 25
        }
    }


class TestHTMLGenerator:
    def test_gamertag(self, sample_data):
        gen = HTMLGenerator(sample_data)
        assert gen.gamertag == "TestPlayer"
    
    def test_top_game(self, sample_data):
        gen = HTMLGenerator(sample_data)
        assert gen.top_game["name"] == "Game One"
    
    def test_top10_games_sorted(self, sample_data):
        gen = HTMLGenerator(sample_data)
        games = gen.top10_games
        
        assert len(games) == 2
        assert games[0]["hours_played"] >= games[1]["hours_played"]
    
    def test_rarest_achievements_filtered(self, sample_data):
        gen = HTMLGenerator(sample_data)
        rarest = gen.rarest_achievements
        
        # Should only include achievements with rarity < 50%
        assert len(rarest) == 1
        assert rarest[0]["name"] == "Rare Achievement"
    
    def test_completed_games(self, sample_data):
        gen = HTMLGenerator(sample_data)
        completed = gen.completed_games
        
        assert len(completed) == 1
        assert completed[0]["name"] == "Game Two"
    
    def test_chart_data(self, sample_data):
        gen = HTMLGenerator(sample_data)
        labels, values = gen.chart_data
        
        assert len(labels) == 2
        assert len(values) == 2
        assert "Jan/24" in labels
        assert 15 in values
    
    def test_generate_html(self, sample_data):
        gen = HTMLGenerator(sample_data)
        html = gen.generate()
        
        assert "<!DOCTYPE html>" in html
        assert "TestPlayer" in html
        assert "Game One" in html
        assert "Rare Achievement" in html
        assert "1.234,5h" in html  # formatted hours


class TestHTMLGeneratorEmptyData:
    def test_empty_games(self):
        data = {
            "profile": {"gamertag": "Empty"},
            "statistics": {},
            "games": [],
            "achievements_detailed": [],
            "by_year": {},
            "achievements_by_month": {}
        }
        gen = HTMLGenerator(data)
        
        assert gen.top_game == {}
        assert gen.top10_games == []
        assert gen.rarest_achievements == []
    
    def test_generates_without_error(self):
        data = {
            "profile": {"gamertag": "Empty", "gamerscore": "0"},
            "statistics": {"total_games": 0, "total_hours": 0, "total_achievements": 0, "completed_games": 0},
            "games": [],
            "achievements_detailed": [],
            "by_year": {},
            "achievements_by_month": {}
        }
        gen = HTMLGenerator(data)
        html = gen.generate()
        
        assert "Empty" in html

