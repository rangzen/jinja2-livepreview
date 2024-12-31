import json

import aiohttp_jinja2
import jinja2
from aiohttp import web
from jinja2 import Environment
from jinja2.exceptions import TemplateError
from project_runpy import env

last_output = None


@aiohttp_jinja2.template("index.html")
async def index(request):
    return {
        "ansible_version": "no ansible",
        "jinja2_version": jinja2.__version__,
    }


async def index_html(request):
    global last_output
    if last_output is None:
        return web.Response(text="No output available", content_type="text/plain")
    return web.Response(text=last_output, content_type="text/html")


class WebSocketHandler(web.View):
    context: dict = {}
    j2_env = Environment()
    j2_template = ""
    _content_type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def context_type(self, value):
        if self._content_type is not None and value == self._content_type:
            return

        self._content_type = value
        await self.send({"context_type": value})

    async def send(self, data):
        await self.ws.send_str(json.dumps(data))

    async def process_context(self, context_str):
        if not context_str:
            self.context = {}
            self.context_type = None
            return

        await self.context_type("json")
        try:
            self.context = json.loads(context_str)
        except Exception as e:
            await self.send(
                {
                    "error": "{}: {}".format(e.__class__.__name__, e),
                    "state": "error-context-json",
                }
            )

        if not isinstance(self.context, dict):
            self.context = {}
            await self.send(
                {
                    "error": "Context is not a hash",
                    "state": "error-context",
                }
            )

    async def render_to_user(self):
        try:
            out = self.j2_env.from_string(self.j2_template).render(**self.context)
            global last_output
            last_output = out
        except TemplateError as e:
            await self.send(
                {
                    "error": "Invalid jinja2 {}".format(e),
                    "state": "error-jinja2",
                }
            )
        else:
            await self.send({"render": out})

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        self.ws = ws

        async for msg in ws:
            try:
                in_data = json.loads(msg.data)
            except TypeError as e:
                self.send({"error": "Invalid message {}".format(e)})

            if "context" in in_data:
                await self.process_context(in_data["context"].strip())

            if "jinja2" in in_data:
                self.j2_template = in_data["jinja2"]

            await self.render_to_user()
        return ws


if __name__ == "__main__":
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("public"))

    app.router.add_route("GET", "/", index)  # TODO try and see if add_static will work
    app.router.add_route("GET", "/html", index_html)
    app.router.add_route("GET", "/ws", WebSocketHandler)
    app.router.add_static("/static", "assets")

    web.run_app(
        app,
        port=env.get("PORT", 9797),
    )
