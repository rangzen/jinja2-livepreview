import json

import yaml
from aiohttp import web
from project_runpy import env
from jinja2 import Environment
from jinja2.exceptions import TemplateError


async def index(request):
    with open('public/index.html', 'rb') as f:
        return web.Response(body=f.read())


class WebSocketHandler(web.View):
    context = {}
    context_type = None
    jinja2 = ''

    def send(self, data):
        self.ws.send_str(json.dumps(data))

    def process_context(self, context_str):
        if not context_str:
            self.context = {}
            self.context_type = None
            return

        if context_str.startswith('{'):
            self.context_type = 'json'
            try:
                self.context = json.loads(context_str)
            except Exception as e:
                self.send({
                    'error': '{}: {}'.format(e.__class__.__name__, e),
                    'state': 'error-context-json',
                })
        else:
            self.context_type = 'yaml'
            try:
                self.context = yaml.load(context_str)
            except Exception as e:
                self.send({
                    'error': '{}: {}'.format(e.__class__.__name__, e),
                    'state': 'error-context-yaml',
                })

        if not isinstance(self.context, dict):
            self.context = {}
            self.send({
                'error': 'Context is not a hash',
                'state': 'error-context',
            })

    def render_to_user(self):
        print('render', self.jinja2, self.context)  # DELETEME
        try:
            out = Environment().from_string(self.jinja2).render(**self.context)
        except TemplateError as e:
            self.send({
                'error': 'Invalid jinja2 {}'.format(e),
                'state': 'error-jinja2',
            })
        else:
            self.send({'render': out})

    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        self.ws = ws

        async for msg in ws:
            print(msg.data)

            try:
                in_data = json.loads(msg.data)
            except TypeError as e:
                self.send({'error': 'Invalid message {}'.format(e)})

            if 'context' in in_data:
                self.process_context(in_data['context'].strip())

            if 'jinja2' in in_data:
                self.jinja2 = in_data['jinja2']

            self.render_to_user()

        return ws


if __name__ == '__main__':
    app = web.Application()

    app.router.add_route('GET', '/', index)  # TODO try and see if add_static will work
    app.router.add_route('GET', '/ws', WebSocketHandler)
    app.router.add_static('/static', 'assets')

    web.run_app(
        app,
        port=env.get('PORT', 8080),
    )