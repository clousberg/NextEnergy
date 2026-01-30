"""Constants for the NextEnergy integration."""
from datetime import timedelta

DOMAIN = "nextenergy"

# API Configuration
BASE_URL = "https://mijn.nextenergy.nl"
LOGIN_URL = f"{BASE_URL}/Mobile_EnergyNext/Login"
MARKET_PRICES_URL = f"{BASE_URL}/Mobile_EnergyNext/MarketPrices"
MODULE_VERSION_URL = f"{BASE_URL}/Mobile_EnergyNext/moduleservices/moduleversioninfo"
SCREENSERVICES_URL = f"{BASE_URL}/Mobile_EnergyNext/screenservices"

# API Endpoints
PRICE_DATA_ENDPOINT = f"{SCREENSERVICES_URL}/Mobile_EnergyNext_CW/WidgetFlow/MarketPrices_Quarterly/DataActionGetPriceDataPoints"
COSTS_LEVELS_ENDPOINT = f"{SCREENSERVICES_URL}/CustomerPortal_CW/ReusableFlow/PriceCostsLevelSelector_NEW/ScreenDataSetGetCostsLevels"
SITE_PROPERTIES_ENDPOINT = f"{SCREENSERVICES_URL}/Mobile_EnergyNext_CW/WidgetFlow/MarketPrices_Quarterly/DataActionGetSiteProperties"

# Default API versions (may need updating when NextEnergy deploys)
DEFAULT_MODULE_VERSION = "70n6yEAoyavGBAoPNutE2Q"
DEFAULT_API_VERSION_PRICES = "YfqvMpHd6TWpPqiZ61s6Cw"
DEFAULT_API_VERSION_COSTS = "O_moHZeIoEf9C2VeIRpb6Q"

# Update interval
SCAN_INTERVAL = timedelta(minutes=15)

# Config keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COST_LEVEL = "cost_level"

# Cost levels
COST_LEVEL_MARKET = "Market"
COST_LEVEL_MARKET_PLUS = "Market+"

COST_LEVEL_OPTIONS = [
    COST_LEVEL_MARKET,
    COST_LEVEL_MARKET_PLUS,
]

# Sensor types
SENSOR_CURRENT_PRICE = "current_price"
SENSOR_GAS_PRICE = "gas_price"
SENSOR_AVERAGE_OFFPEAK = "average_offpeak"