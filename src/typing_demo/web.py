import logging
import typing as t

from django.core.handlers.wsgi import WSGIHandler, WSGIRequest
from django.http import HttpRequest, HttpResponse
from django.urls import path

from typing_demo.config import AppConfiguration

logger = logging.getLogger(__name__)


T = t.TypeVar("T")


class AppData(t.Generic[T]):
    def __init__(self, data: T) -> None:
        self.data = data


class WebRequest(WSGIRequest):
    _app_data: dict[int, AppData[t.Any]]

    def set_app_data(self, app_data: dict[int, AppData[t.Any]]):
        self._app_data = app_data

    def data(self, _type: type[T]) -> t.Optional[AppData[T]]:
        return self._app_data.get(id(_type))


class WebApplication(WSGIHandler):
    request_class = WebRequest

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._app_data: dict[int, AppData[t.Any]] = {}

    def app_data(self, data: AppData[t.Any]):
        self._app_data[id(data.data.__class__)] = data
        return self

    def get_response(self, request: WebRequest):
        request.set_app_data(self._app_data)
        return super().get_response(t.cast(HttpRequest, request))


def index(request: WebRequest) -> HttpResponse:
    logger.info("hello world")
    config_data = request.data(AppConfiguration)
    logger.info(config_data.data.secret_key)
    import time
    time.sleep(3)
    return HttpResponse(b"hello world", "text/plain")


urlpatterns = [
    path("", index)
]


def create_app(config_fo: t.Optional[t.TextIO] = None):
    from typing_demo.config import configure

    config = configure(config_fo)

    app = WebApplication().app_data(AppData(config))

    return app
