from fragment_api_lib.client import FragmentAPIClient
from fragment_api_lib.models import *

client = FragmentAPIClient()

# Ping
print("API ping:", client.ping())

# Replace with your 24 words seed phrase from TON v4r2 Wallet
seed = "none"

# Replace with your Fragment cookies exported from Cookie-Editor extension as Header String
# https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
fragment_cookies = "your_fragment_cookies"

# Get balance
res = client.get_balance(seed=seed)
print("Balance:", res)


# Buy stars without KYC
res = client.buy_stars_without_kyc(
    username="@maga_dager", # or "@NightStrang6r", or "https://t.me/NightStrang6r"
    amount=50,
    seed=seed
)
print("Buy stars without KYC response:", res)