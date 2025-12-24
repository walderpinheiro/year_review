"""Tests for SVG generator."""

import pytest
from unittest.mock import patch, MagicMock

from src.svg_generator import SVGGenerator, fetch_image_base64


class TestFetchImageBase64:
    """Tests for fetch_image_base64 function."""
    
    def test_empty_url_returns_none(self):
        assert fetch_image_base64("") is None
        assert fetch_image_base64(None) is None
    
    @patch("src.svg_generator.urllib.request.urlopen")
    def test_successful_fetch(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"test_image_data"
        mock_resp.headers.get.return_value = "image/png"
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        
        result = fetch_image_base64("https://example.com/img.png")
        assert result.startswith("data:image/png;base64,")
    
    @patch("src.svg_generator.urllib.request.urlopen")
    def test_failed_fetch_returns_none(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Network error")
        
        result = fetch_image_base64("https://example.com/img.png")
        assert result is None


class TestSVGGenerator:
    """Tests for SVGGenerator class."""
    
    @pytest.fixture
    def sample_data(self):
        return {
            "profile": {
                "gamertag": "TestUser",
                "avatar_url": "https://example.com/avatar.png",
                "gamerscore": "50000"
            },
            "statistics": {
                "total_hours": 1234.5,
                "total_games": 100,
                "total_achievements": 2000
            },
            "games": [
                {"name": "Game 1", "hours_played": 500, "image": "https://example.com/g1.png"},
                {"name": "Game 2", "hours_played": 300, "image": "https://example.com/g2.png"},
                {"name": "Game 3", "hours_played": 200, "image": "https://example.com/g3.png"},
                {"name": "Game 4", "hours_played": 100, "image": "https://example.com/g4.png"}
            ]
        }
    
    def test_gamertag(self, sample_data):
        gen = SVGGenerator(sample_data)
        assert gen.gamertag == "TestUser"
    
    def test_top_game(self, sample_data):
        gen = SVGGenerator(sample_data)
        assert gen.top_game["name"] == "Game 1"
    
    def test_top3_games(self, sample_data):
        gen = SVGGenerator(sample_data)
        top3 = gen.top3_games
        assert len(top3) == 3
        assert top3[0]["name"] == "Game 1"
        assert top3[1]["name"] == "Game 2"
        assert top3[2]["name"] == "Game 3"
    
    def test_empty_data(self):
        gen = SVGGenerator({})
        assert gen.gamertag == "Unknown"
        assert gen.top_game == {}
        assert gen.top3_games == []
    
    @patch("src.svg_generator.fetch_image_base64")
    def test_generate_contains_gamertag(self, mock_fetch, sample_data):
        mock_fetch.return_value = None
        gen = SVGGenerator(sample_data)
        svg = gen.generate()
        
        assert "TESTUSER" in svg  # uppercased gamertag
        assert "LIFETIME" in svg
        assert "REVIEW" in svg
    
    @patch("src.svg_generator.fetch_image_base64")
    def test_generate_contains_stats(self, mock_fetch, sample_data):
        mock_fetch.return_value = None
        gen = SVGGenerator(sample_data)
        svg = gen.generate()
        
        assert "1.234,5" in svg  # formatted hours
        assert "100" in svg  # games count
        assert "50.000" in svg  # gamerscore
        assert "2.000" in svg  # achievements
    
    @patch("src.svg_generator.fetch_image_base64")
    def test_generate_contains_top3_games(self, mock_fetch, sample_data):
        mock_fetch.return_value = None
        gen = SVGGenerator(sample_data)
        svg = gen.generate()
        
        assert "TOP 3 JOGOS" in svg
        assert "Game 1" in svg
        assert "Game 2" in svg
        assert "Game 3" in svg

