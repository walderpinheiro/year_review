"""Tests for Xbox API client."""

import pytest
from src.api import XboxCredentials, XboxAPI


class TestXboxCredentials:
    def test_from_tokens(self):
        tokens = {
            "user_hash": "abc123",
            "xsts_token": "token456",
            "xuid": "789"
        }
        creds = XboxCredentials.from_tokens(tokens)
        
        assert creds.user_hash == "abc123"
        assert creds.xsts_token == "token456"
        assert creds.xuid == "789"
    
    def test_auth_header(self):
        creds = XboxCredentials(
            user_hash="hash",
            xsts_token="token",
            xuid="123"
        )
        header = creds.auth_header()
        
        assert header == "XBL3.0 x=hash;token"
    
    def test_missing_field(self):
        tokens = {"user_hash": "abc"}
        
        with pytest.raises(KeyError):
            XboxCredentials.from_tokens(tokens)


class TestXboxAPI:
    def test_headers(self):
        creds = XboxCredentials("hash", "token", "123")
        api = XboxAPI(creds)
        
        headers = api._headers("2")
        
        assert "Authorization" in headers
        assert headers["x-xbl-contract-version"] == "2"
        assert headers["Accept"] == "application/json"
    
    def test_headers_custom_version(self):
        creds = XboxCredentials("hash", "token", "123")
        api = XboxAPI(creds)
        
        headers = api._headers("4")
        
        assert headers["x-xbl-contract-version"] == "4"

