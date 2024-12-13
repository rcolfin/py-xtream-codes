from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Final, Self
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

if TYPE_CHECKING:
    from types import TracebackType

logger = logging.getLogger(__name__)


class XTream:
    MAX_NUMBER_RETRIES: Final[int] = 3
    DEFAULT_TIMEOUT: Final[tuple[float, float]] = (5, 30)

    live_type = "Live"
    vod_type = "VOD"
    series_type = "Series"

    def __init__(self, server: str, username: str, password: str) -> None:
        self.server = server
        self.username = username
        self.__password = password
        self._session: requests.Session | None = None
        self.url = urljoin(self.server, "player_api.php")

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: object,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session is not None:
            self._session.close()

    # Note: The API Does not provide Full links to the requested stream. You have to build the url to the stream in order to play it.
    #
    # For Live Streams the main format is
    #            http(s)://domain:port/live/username/password/streamID.ext ( In  allowed_output_formats element you have the available ext )
    #
    # For VOD Streams the format is:
    #
    # http(s)://domain:port/movie/username/password/streamID.ext ( In  target_container element you have the available ext )
    #
    # For Series Streams the format is
    #
    # http(s)://domain:port/series/username/password/streamID.ext ( In  target_container element you have the available ext )

    # If you want to limit the displayed output data, you can use params[offset]=X & params[items_per_page]=X on your call.

    # Authentication returns information about the account and server:
    def authenticate(self) -> requests.Response:
        return self._make_request(self.url)

    # GET Stream Categories
    def categories(self, stream_type: str) -> requests.Response:
        params: dict[str, Any] = {}
        if stream_type == self.live_type:
            params = self._get_live_categories_params()
        elif stream_type == self.vod_type:
            params = self._get_vod_cat_params()
        elif stream_type == self.series_type:
            params = self._get_series_cat_params()

        return self._make_request(self.url, params=params)

    # GET Streams
    def streams(self, stream_type: str) -> requests.Response:
        params: dict[str, Any] = {}
        if stream_type == self.live_type:
            params = self._get_live_streams_params()
        elif stream_type == self.vod_type:
            params = self._get_vod_streams_params()
        elif stream_type == self.series_type:
            params = self._get_series_params()

        return self._make_request(self.url, params=params)

    # GET Streams by Category
    def streams_by_category(
        self,
        stream_type: str,
        category_id: str,
    ) -> requests.Response:
        params: dict[str, Any] = {}
        if stream_type == self.live_type:
            params = self._get_live_streams_by_category_params(category_id)
        elif stream_type == self.vod_type:
            params = self._get_vod_streams_by_category_params(category_id)
        elif stream_type == self.series_type:
            params = self._get_series_by_category_params(category_id)

        return self._make_request(self.url, params=params)

    # GET SERIES Info
    def series_info_by_id(self, series_id: str) -> requests.Response:
        return self._make_request(
            self.url,
            params=self._get_series_info_by_id_params(series_id),
        )

    # The seasons array, might be filled or might be completely empty.
    # If it is not empty, it will contain the cover, overview and the air date of the selected season.
    # In your APP if you want to display the series, you have to take that from the episodes array.

    # GET VOD Info
    def vod_info_by_id(self, vod_id: str) -> requests.Response:
        return self._make_request(
            self.url,
            params=self._get_vod_info_by_id_params(vod_id),
        )

    # GET short_epg for LIVE Streams (same as stalker portal, prints the next X EPG that will play soon)
    def live_epg_by_stream(self, stream_id: str) -> requests.Response:
        return self._make_request(
            self.url,
            params=self._get_live_epg_by_stream_params(stream_id),
        )

    def live_epg_by_stream_and_limit(
        self,
        stream_id: str,
        limit: int,
    ) -> requests.Response:
        return self._make_request(
            self.url,
            params=self.get_live_epg_by_stream_and_limit_params(stream_id, limit),
        )

    #  GET ALL EPG for LIVE Streams (same as stalker portal, but it will print all epg listings regardless of the day)
    def all_live_epg_by_stream(self, stream_id: str) -> requests.Response:
        return self._make_request(
            self.url,
            params=self._get_all_live_epg_by_stream_params(stream_id),
        )

    # Full EPG List for all Streams
    def all_epg(self) -> requests.Response:
        return self._make_request(self._get_all_epg_url())

    ## URL-builder methods
    def __get_authentication_params(
        self,
    ) -> dict[str, Any]:
        return {"username": self.username, "password": self.__password}

    def _make_request(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> requests.Response:
        auth_params = self.__get_authentication_params()
        logger.debug("Sending %s, params=%s", url, params if params else "")
        params = {**auth_params, **params} if params else auth_params
        r = self._ensure_session().get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
        logger.debug("%s", self._get_status(r))
        r.raise_for_status()
        return r

    def _get_all_epg_url(
        self,
    ) -> str:
        return urljoin(self.server, "/xmltv.php")

    def _get_action_params(self, action: str) -> dict[str, Any]:
        return {"action": action}

    def _get_action_category(self, action: str, category_id: str) -> dict[str, Any]:
        return {**self._get_action_params(action), "category_id": category_id}

    def _get_live_categories_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_live_categories")

    def _get_live_streams_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_live_streams")

    def _get_live_streams_by_category_params(self, category_id: str) -> dict[str, Any]:
        return self._get_action_category("get_live_streams", category_id)

    def _get_vod_cat_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_vod_categories")

    def _get_vod_streams_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_vod_streams")

    def _get_vod_streams_by_category_params(self, category_id: str) -> dict[str, Any]:
        return self._get_action_category("get_vod_streams", category_id)

    def _get_series_cat_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_series_categories")

    def _get_series_params(
        self,
    ) -> dict[str, Any]:
        return self._get_action_params("get_series")

    def _get_series_by_category_params(self, category_id: str) -> dict[str, Any]:
        return self._get_action_category("get_series", category_id)

    def _get_series_info_by_id_params(self, series_id: str) -> dict[str, Any]:
        return {
            **self._get_action_params("get_series_info"),
            "series_id": series_id,
        }

    def _get_vod_info_by_id_params(self, vod_id: str) -> dict[str, Any]:
        return {**self._get_action_params("get_vod_info"), "vod_id": vod_id}

    def _get_live_epg_by_stream_params(self, stream_id: str) -> dict[str, Any]:
        return {**self._get_action_params("get_short_epg"), "stream_id": stream_id}

    def get_live_epg_by_stream_and_limit_params(
        self,
        stream_id: str,
        limit: int,
    ) -> dict[str, Any]:
        return {
            **self._get_action_params("get_short_epg"),
            "stream_id": stream_id,
            "limit": limit,
        }

    def _get_all_live_epg_by_stream_params(self, stream_id: str) -> dict[str, Any]:
        return {
            **self._get_action_params("get_simple_data_table"),
            "stream_id": stream_id,
        }

    def _ensure_session(self) -> requests.Session:
        if self._session is None:
            self._session = self._create_session()
        return self._session

    @classmethod
    def _create_session(cls) -> requests.Session:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(total=cls.MAX_NUMBER_RETRIES))
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @staticmethod
    def _get_status(response: requests.Response) -> str:
        try:
            return f"{response.status_code} ({HTTPStatus(response.status_code).name})"
        except ValueError:
            return str(response.status_code)
