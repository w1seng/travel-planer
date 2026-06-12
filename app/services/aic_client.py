import httpx
import time
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# inmemory cache

_cache: dict[int, dict] = {}


def _get_cached(external_id: int) -> Optional[dict]:
    """Returns cached artwork data if it exists and hasn't expired."""
    entry = _cache.get(external_id)
    if entry and time.time() < entry["expires_at"]:
        logger.debug(f"Cache HIT for artwork {external_id}")
        return entry["data"]
    return None


def _set_cache(external_id: int, data: dict) -> None:

    _cache[external_id] = {
        "data": data,
        "expires_at": time.time() + settings.CACHE_TTL_SECONDS,
    }
    logger.debug(f"Cache SET for {external_id}, TTL={settings.CACHE_TTL_SECONDS}s")



class AICClient:

    FIELDS = "id,title,artist_display,image_id"

    def __init__(self) -> None:
        self.base_url = settings.AIC_API_BASE_URL
        self.timeout = settings.AIC_TIMEOUT_SECONDS

    def get_artwork(self, external_id: int) -> Optional[dict]:

        # check cache 
        cached = _get_cached(external_id)
        if cached:
            return cached

        # all AIC API
        url = f"{self.base_url}/artworks/{external_id}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params={"fields": self.FIELDS})

            if response.status_code == 404:
                logger.info(f"Artwork {external_id} not found in AIC API")
                return None

            response.raise_for_status()
            raw = response.json().get("data", {})

        except httpx.TimeoutException:
            logger.error(f"AIC API timeout  {external_id}")
            raise AICClientError("timed out Please try again later.", status_code=503)

        except httpx.HTTPStatusError as e:
            logger.error(f"AIC API error {e.response.status_code} for  {external_id}")
            raise AICClientError(f"API returned error: {e.response.status_code}", status_code=502)

        except httpx.RequestError as e:
            logger.error(f"API request faill: {e}")
            raise AICClientError("Couldn't reach API.", status_code=503)

        # normalize
        artwork = self._normalize(raw)

        #store in cache
        _set_cache(external_id, artwork)

        return artwork

    def artwork_exists(self, external_id: int) -> bool:
        return self.get_artwork(external_id) is not None

    @staticmethod
    def _normalize(raw: dict) -> dict:
        return {
            "external_id": raw.get("id"),
            "title":       raw.get("title") or "Untitled",
            "artist":      raw.get("artist_display"),   
            "image_id":    raw.get("image_id"),         
        }



# exception to see status code 

class AICClientError(Exception):

    def __init__(self, message: str, status_code: int = 503) -> None:
        super().__init__(message)
        self.status_code = status_code


aic_client = AICClient()