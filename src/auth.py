"""Authentication module."""

import asyncio
import httpx
from aiohttp import web

from .config import (
    CLIENT_ID, CLIENT_SECRET, REDIRECT_URI,
    OAUTH_AUTHORIZE, OAUTH_TOKEN, XBOX_USER_AUTH, XBOX_XSTS_AUTH, SCOPES
)
from .utils import save_tokens, tokens_exist


class OAuthServer:
    """Local server to capture OAuth callback."""
    
    def __init__(self):
        self.code = None
        self.app = web.Application()
        self.app.router.add_get('/auth/callback', self._handler)
        self.runner = None
    
    async def _handler(self, request):
        self.code = request.query.get('code')
        if request.query.get('error'):
            return web.Response(text="Error", status=400)
        return web.Response(text="OK - close this window", content_type='text/html')
    
    async def start(self, port=8080):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        await web.TCPSite(self.runner, '0.0.0.0', port).start()
    
    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
    
    async def wait_for_code(self, timeout=300):
        for _ in range(timeout):
            if self.code:
                return self.code
            await asyncio.sleep(1)
        return None


class Authenticator:
    """Xbox Live authenticator."""
    
    @staticmethod
    def auth_url() -> str:
        """Generate authorization URL."""
        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": SCOPES,
            "redirect_uri": REDIRECT_URI,
        }
        query = "&".join(f"{k}={v.replace(' ', '+')}" for k, v in params.items())
        return f"{OAUTH_AUTHORIZE}?{query}"
    
    @staticmethod
    async def _post(url: str, data: dict = None, json_data: dict = None) -> dict:
        """Make POST request."""
        async with httpx.AsyncClient() as client:
            if data:
                resp = await client.post(url, data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"})
            else:
                resp = await client.post(url, json=json_data,
                    headers={"Content-Type": "application/json", "x-xbl-contract-version": "1"})
            resp.raise_for_status()
            return resp.json()
    
    async def exchange_code(self, code: str) -> dict:
        """Exchange auth code for OAuth tokens."""
        return await self._post(OAUTH_TOKEN, data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
        })
    
    async def get_user_token(self, access_token: str) -> dict:
        """Get Xbox user token."""
        return await self._post(XBOX_USER_AUTH, json_data={
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={access_token}"
            }
        })
    
    async def get_xsts_token(self, user_token: str) -> dict:
        """Get XSTS token."""
        return await self._post(XBOX_XSTS_AUTH, json_data={
            "RelyingParty": "http://xboxlive.com",
            "TokenType": "JWT",
            "Properties": {"UserTokens": [user_token], "SandboxId": "RETAIL"}
        })
    
    async def authenticate(self) -> dict:
        """Full authentication flow."""
        if tokens_exist():
            print("Tokens already exist")
            return {}
        
        if not CLIENT_ID:
            raise ValueError("XBOX_CLIENT_ID not set")
        
        print(f"Open this URL:\n{self.auth_url()}\n")
        
        server = OAuthServer()
        await server.start(8080)
        print("Waiting for callback on http://localhost:8080 ...")
        
        code = await server.wait_for_code(300)
        await server.stop()
        
        if not code:
            raise TimeoutError("Auth timeout")
        
        print("Code received, getting tokens...")
        
        oauth = await self.exchange_code(code)
        user_resp = await self.get_user_token(oauth["access_token"])
        xsts_resp = await self.get_xsts_token(user_resp["Token"])
        
        xui = xsts_resp["DisplayClaims"]["xui"][0]
        
        tokens = {
            "oauth": {
                "access_token": oauth["access_token"],
                "refresh_token": oauth.get("refresh_token")
            },
            "user_token": user_resp["Token"],
            "xsts_token": xsts_resp["Token"],
            "user_hash": xui["uhs"],
            "xuid": xui["xid"],
            "gamertag": xui["gtg"],
        }
        
        save_tokens(tokens)
        print(f"Authenticated as {tokens['gamertag']}")
        
        return tokens

