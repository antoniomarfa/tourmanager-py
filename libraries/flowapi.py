import hmac
import hashlib
import requests
from urllib.parse import quote_plus


class FlowApi:
    def __init__(self):
        self.secret_key = None
        self.api_url = None
        self.api_key = None

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def set_secret_key(self, secret_key: str):
        self.secret_key = secret_key

    def set_api_url(self, api_url: str):
        self.api_url = api_url

    def send(self, service: str, params: dict, method: str = "GET"):
        method = method.upper()
        url = f"{self.api_url}/{service}"

        params = {"apiKey": self.api_key, **params}
        data = self._get_pack(params, method)
        sign = self._sign(params)

        if method == "GET":
            response = self._http_get(url, data, sign)
        else:
            response = self._http_post(url, data, sign)

        if "info" in response:
            code = response["info"]
            body = response["output"]

            if code == 200:
                return body
            elif code in (400, 401):
                raise Exception(body.get("message", "Error"), body.get("code", code))
            else:
                raise Exception(f"Unexpected error occurred. HTTP_CODE: {code}", code)
        else:
            raise Exception("Unexpected error occurred.")

    def _get_pack(self, params: dict, method: str) -> str:
        keys = sorted(params.keys())
        data = ""
        for key in keys:
            if method == "GET":
                data += f"&{quote_plus(str(key))}={quote_plus(str(params[key]))}"
            else:
                data += f"&{key}={params[key]}"
        return data[1:]

    def _sign(self, params: dict) -> str:
        keys = sorted(params.keys())
        to_sign = "&".join([f"{k}={params[k]}" for k in keys])
        return hmac.new(
            self.secret_key.encode("utf-8"),
            to_sign.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _http_get(self, url: str, data: str, sign: str) -> dict:
        full_url = f"{url}?{data}&s={sign}"
        response = requests.get(full_url)

        return {
            "output": response.json() if response.text else {},
            "info": response.status_code,
        }

    def _http_post(self, url: str, data: str, sign: str) -> dict:
        payload = f"{data}&s={sign}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)

        return {
            "output": response.json() if response.text else {},
            "info": response.status_code,
        }
