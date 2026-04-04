from datetime import date
import json
import logging
import os
from kiteconnect import KiteConnect
from config.settings import TOKEN_CACHE_FILE, settings

logger = logging.getLogger(__name__)

class KiteAuth:
    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)

    def get_login_url(self) -> str:
        return self.kite.login_url()

    def generate_session(self, request_token: str) -> None:
        session = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.kite.set_access_token(session['access_token'])
        os.environ['KITE_ACCESS_TOKEN'] = session['access_token']
        os.environ['KITE_ACCESS_DATE'] = str(date.today())
        TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_CACHE_FILE.write_text(
            json.dumps({"access_token": session["access_token"], "access_date": str(date.today())}),
            encoding="utf-8",
        )

    def validate_session(self) -> bool:
        try:
            self.kite.profile()
            return True
        except Exception as exc:
            logger.warning('Session validation failed: %s', exc)
            return False

    def bootstrap(self) -> KiteConnect:
        token = settings.kite_access_token
        token_date = settings.kite_access_date
        if TOKEN_CACHE_FILE.exists():
            try:
                cached = json.loads(TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
                token = token or cached.get("access_token", "")
                token_date = token_date or cached.get("access_date", "")
            except json.JSONDecodeError:
                logger.warning("Ignoring malformed token cache")

        if token and token_date == str(date.today()):
            self.kite.set_access_token(token)
            if self.validate_session():
                return self.kite
        print(f'Login URL: {self.get_login_url()}')
        request_token = input('Enter request_token: ').strip()
        self.generate_session(request_token)
        if not self.validate_session():
            raise RuntimeError('Unable to validate session')
        return self.kite
