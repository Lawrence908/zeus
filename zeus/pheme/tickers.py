# zeus/pheme/tickers.py - Deterministic company-name <-> ticker resolution.
#
# Stage 4 correlation candidates require exact entity overlap, so a Canary
# story saying "Nvidia" never matches a CapitolScope NVDA trade unless the 7B
# extractor happened to emit the ticker. This static map makes that link
# deterministic: company-name mentions add the ticker as an entity, and bare
# tickers add the canonical company name. Curated toward names that actually
# appear in congressional disclosures (mega caps, chips, banks, energy,
# defense, pharma, retail); extend freely - keys are casefolded substrings
# matched on word boundaries.
from __future__ import annotations

import re

# name variant (casefolded) -> ticker
NAME_TO_TICKER: dict[str, str] = {
    # Tech mega caps
    "apple": "AAPL", "microsoft": "MSFT", "alphabet": "GOOGL", "google": "GOOGL",
    "amazon": "AMZN", "meta platforms": "META", "facebook": "META", "instagram": "META",
    "tesla": "TSLA", "netflix": "NFLX", "oracle": "ORCL", "salesforce": "CRM",
    "adobe": "ADBE", "ibm": "IBM", "palantir": "PLTR", "uber": "UBER",
    "airbnb": "ABNB", "shopify": "SHOP", "paypal": "PYPL", "zoom": "ZM",
    # Chips / hardware
    "nvidia": "NVDA", "amd": "AMD", "advanced micro devices": "AMD", "intel": "INTC",
    "tsmc": "TSM", "taiwan semiconductor": "TSM", "broadcom": "AVGO",
    "qualcomm": "QCOM", "micron": "MU", "arm holdings": "ARM", "asml": "ASML",
    "texas instruments": "TXN", "super micro": "SMCI", "dell": "DELL",
    # Finance
    "jpmorgan": "JPM", "jp morgan": "JPM", "goldman sachs": "GS",
    "morgan stanley": "MS", "bank of america": "BAC", "wells fargo": "WFC",
    "citigroup": "C", "blackrock": "BLK", "berkshire hathaway": "BRK.B",
    "visa": "V", "mastercard": "MA", "american express": "AXP",
    "charles schwab": "SCHW", "coinbase": "COIN", "robinhood": "HOOD",
    # Energy
    "exxon": "XOM", "exxonmobil": "XOM", "chevron": "CVX", "conocophillips": "COP",
    "occidental": "OXY", "nextera": "NEE", "enbridge": "ENB", "suncor": "SU",
    # Defense / aerospace
    "lockheed martin": "LMT", "raytheon": "RTX", "rtx corporation": "RTX",
    "northrop grumman": "NOC", "general dynamics": "GD", "boeing": "BA",
    "l3harris": "LHX", "spacex": "SPACEX",  # private; still a useful link token
    # Pharma / health
    "pfizer": "PFE", "moderna": "MRNA", "johnson & johnson": "JNJ",
    "unitedhealth": "UNH", "eli lilly": "LLY", "abbvie": "ABBV", "merck": "MRK",
    # Retail / consumer
    "walmart": "WMT", "costco": "COST", "home depot": "HD", "target": "TGT",
    "mcdonald's": "MCD", "mcdonalds": "MCD", "starbucks": "SBUX", "nike": "NKE",
    "coca-cola": "KO", "coca cola": "KO", "pepsico": "PEP", "procter & gamble": "PG",
    "disney": "DIS", "comcast": "CMCSA",
    # Industrial / auto / telecom
    "general motors": "GM", "ford": "F", "caterpillar": "CAT", "deere": "DE",
    "general electric": "GE", "honeywell": "HON", "3m": "MMM",
    "at&t": "T", "verizon": "VZ", "t-mobile": "TMUS", "bell canada": "BCE",
    # Canada-relevant
    "shopify inc": "SHOP", "royal bank of canada": "RY", "td bank": "TD",
    "canadian national railway": "CNR", "telus": "TU",
}

# ticker -> canonical company token (first/most canonical variant)
TICKER_TO_NAME: dict[str, str] = {}
for _name, _ticker in NAME_TO_TICKER.items():
    TICKER_TO_NAME.setdefault(_ticker, _name)

_NAME_PATTERNS: dict[str, re.Pattern] | None = None


def _patterns() -> dict[str, re.Pattern]:
    global _NAME_PATTERNS
    if _NAME_PATTERNS is None:
        _NAME_PATTERNS = {
            name: re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
            for name in NAME_TO_TICKER
        }
    return _NAME_PATTERNS


def resolve_tickers(entities: list[str], text: str = "") -> list[str]:
    """Return extra entities implied by known names/tickers.

    - A known company name in the entities or the text adds its ticker.
    - A bare ticker in the entities adds the canonical company name, so
      entity-token overlap links a CapitolScope trade to name-only prose.
    Returns only the additions (deduped, casefolded like pipeline entities).
    """
    have = {e.strip().casefold() for e in entities if e and e.strip()}
    extras: set[str] = set()

    for name, ticker in NAME_TO_TICKER.items():
        tick = ticker.casefold()
        if tick in have or name in have:
            extras.add(tick)
            extras.add(name)

    scan = text[:1500]
    if scan:
        for name, pattern in _patterns().items():
            tick = NAME_TO_TICKER[name].casefold()
            if tick not in have and tick not in extras and pattern.search(scan):
                extras.add(tick)
                extras.add(name)

    for entity in have:
        upper = entity.upper()
        if upper in TICKER_TO_NAME:
            extras.add(TICKER_TO_NAME[upper])

    return sorted(extras - have)
