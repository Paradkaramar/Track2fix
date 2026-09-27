from app.config import Config

BASE_CURRENCY = "USD"


def convert_currency(amount: float, currency: str, config: Config) -> float:
    """Return *amount* converted to USD.

    For USD payments no conversion is needed.
    For other currencies the configured exchange rate is applied.
    """
    if currency == BASE_CURRENCY:
        return amount

    rate = config.get("EXCHANGE_RATE")
    if rate is None:
        raise ValueError(
            "EXCHANGE_RATE is not configured for the active environment. "
            "Non-base-currency payments cannot be processed."
        )
    converted = float(amount) * rate
    return converted
