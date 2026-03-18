import time
import logging
from .base import RateProvider

logger = logging.getLogger(__name__)

class RetryRateProvider(RateProvider):
    """Декоратор, добавляющий повторные попытки при сбоях."""

    def __init__(self, provider: RateProvider, max_retries: int = 3, delay: float = 2.0) -> None:
        self._provider = provider
        self.max_retries = max_retries
        self.delay = delay

    def get_rate(self, currency: str) -> float:
        for attempt in range(self.max_retries):
            try:
                return self._provider.get_rate(currency)
            except Exception as e:
                logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.delay)
        raise RuntimeError("Не удалось получить курс после нескольких попыток")