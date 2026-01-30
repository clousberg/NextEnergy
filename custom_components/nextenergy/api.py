"""NextEnergy API client."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import unquote

import aiohttp

from .const import (
    BASE_URL,
    DEFAULT_API_VERSION_COSTS,
    DEFAULT_API_VERSION_PRICES,
    DEFAULT_MODULE_VERSION,
    LOGIN_URL,
    MODULE_VERSION_URL,
    PRICE_DATA_ENDPOINT,
    COST_LEVEL_MARKET_PLUS,
)

_LOGGER = logging.getLogger(__name__)


class NextEnergyApiError(Exception):
    """Exception for NextEnergy API errors."""


class NextEnergyAuthError(NextEnergyApiError):
    """Exception for authentication errors."""


class NextEnergyApi:
    """NextEnergy API client."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the API client."""
        self.username = username
        self.password = password
        self._session: aiohttp.ClientSession | None = None
        self._session_cookie: str | None = None
        self._csrf_token: str | None = None
        self._module_version: str = DEFAULT_MODULE_VERSION
        self._api_version_prices: str = DEFAULT_API_VERSION_PRICES
        self._api_version_costs: str = DEFAULT_API_VERSION_COSTS

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def authenticate(self) -> bool:
        """Authenticate with NextEnergy."""
        session = await self._get_session()

        try:
            # First, get the login page to establish session
            async with session.get(LOGIN_URL) as response:
                if response.status != 200:
                    raise NextEnergyAuthError("Failed to load login page")

            # Get module version
            async with session.get(f"{MODULE_VERSION_URL}?{int(datetime.now().timestamp() * 1000)}") as response:
                if response.status == 200:
                    data = await response.json()
                    self._module_version = data.get("versionToken", DEFAULT_MODULE_VERSION)

            # Perform login using OutSystems screenservices
            login_endpoint = f"{BASE_URL}/Mobile_EnergyNext/screenservices/Mobile_EnergyNext/MainFlow/Login/ActionLogin"
            
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json",
                "OutSystems-locale": "en-US",
            }

            login_body = {
                "versionInfo": {
                    "moduleVersion": self._module_version,
                    "apiVersion": self._module_version
                },
                "viewName": "MainFlow.Login",
                "screenData": {
                    "variables": {
                        "Username": self.username,
                        "Password": self.password,
                        "RememberUsername": False
                    }
                }
            }

            async with session.post(login_endpoint, json=login_body, headers=headers) as response:
                if response.status != 200:
                    raise NextEnergyAuthError(f"Login failed with status {response.status}")

                result = await response.json()
                
                if "exception" in result and result["exception"]:
                    raise NextEnergyAuthError(f"Login failed: {result['exception'].get('message', 'Unknown error')}")

            # Extract session cookie
            cookies = session.cookie_jar.filter_cookies(BASE_URL)
            for cookie in cookies.values():
                if cookie.key == "nr2Users_Customers":
                    self._session_cookie = cookie.value
                    # Extract CSRF token from cookie
                    decoded = unquote(cookie.value)
                    csrf_match = re.search(r'crf=([^;]+)', decoded)
                    if csrf_match:
                        self._csrf_token = csrf_match.group(1)
                    break

            if not self._session_cookie:
                raise NextEnergyAuthError("No session cookie received after login")

            _LOGGER.debug("Successfully authenticated with NextEnergy")
            return True

        except aiohttp.ClientError as err:
            raise NextEnergyApiError(f"Connection error: {err}") from err

    async def get_hourly_prices(self, date: datetime | None = None, cost_level: str = COST_LEVEL_MARKET_PLUS) -> dict[str, Any]:
        """Get hourly electricity prices for a given date."""
        if not self._session_cookie:
            await self.authenticate()

        session = await self._get_session()
        
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
            "OutSystems-locale": "en-US",
            "X-CSRFToken": self._csrf_token or "",
        }

        body = {
            "versionInfo": {
                "moduleVersion": self._module_version,
                "apiVersion": self._api_version_prices
            },
            "viewName": "MainFlow.MarketPrices",
            "screenData": {
                "variables": {
                    "DateTime": f"{date_str}T00:00:00Z",
                    "_dateTimeInDataFetchStatus": 1,
                    "ContractId": 0,
                    "_contractIdInDataFetchStatus": 1
                }
            },
            "clientVariables": {
                "PriceDate": date_str,
                "PriceCostsLevelId": cost_level
            }
        }

        try:
            async with session.post(PRICE_DATA_ENDPOINT, json=body, headers=headers) as response:
                if response.status != 200:
                    raise NextEnergyApiError(f"Failed to get prices: status {response.status}")

                result = await response.json()

                if "exception" in result and result["exception"]:
                    error_msg = result["exception"].get("message", "Unknown error")
                    if "Invalid Login" in error_msg:
                        # Session expired, re-authenticate
                        self._session_cookie = None
                        await self.authenticate()
                        return await self.get_hourly_prices(date, cost_level)
                    raise NextEnergyApiError(f"API error: {error_msg}")

                return self._parse_price_response(result, date)

        except aiohttp.ClientError as err:
            raise NextEnergyApiError(f"Connection error: {err}") from err

    def _parse_price_response(self, response: dict[str, Any], date: datetime) -> dict[str, Any]:
        """Parse the price response from the API."""
        data = response.get("data", {})
        
        # Extract hourly prices
        hourly_prices = {}
        pricing_list = data.get("PricingList", [])
        
        for item in pricing_list:
            hour = item.get("Hour", 0)
            price = item.get("Price", 0)
            hourly_prices[hour] = round(price, 4)

        # Get current hour price
        current_hour = datetime.now().hour
        current_price = hourly_prices.get(current_hour, 0)

        # Get gas price
        gas_price = data.get("GasPrice", 0)

        # Calculate off-peak average (typically 00:00-06:00)
        off_peak_prices = [hourly_prices.get(h, 0) for h in range(0, 6)]
        avg_off_peak = sum(off_peak_prices) / len(off_peak_prices) if off_peak_prices else 0

        # Find min and max prices
        all_prices = list(hourly_prices.values())
        min_price = min(all_prices) if all_prices else 0
        max_price = max(all_prices) if all_prices else 0
        min_price_hour = [h for h, p in hourly_prices.items() if p == min_price][0] if all_prices else 0
        max_price_hour = [h for h, p in hourly_prices.items() if p == max_price][0] if all_prices else 0

        return {
            "date": date.strftime("%Y-%m-%d"),
            "hourly_prices": hourly_prices,
            "current_hour": current_hour,
            "current_price": round(current_price, 4),
            "gas_price": round(gas_price, 4),
            "average_off_peak": round(avg_off_peak, 4),
            "average_price": round(sum(all_prices) / len(all_prices), 4) if all_prices else 0,
            "min_price": round(min_price, 4),
            "max_price": round(max_price, 4),
            "min_price_hour": min_price_hour,
            "max_price_hour": max_price_hour,
        }