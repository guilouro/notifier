#coding: utf-8
from tornado import gen
import tornado.httpserver as httpserver
import tornado.web as web
import tornado.ioloop as ioloop
import redis
import tornadoredis
import json

# Cliente do Redis síncrono (StrictRedis)
# Eu costumo usar ele pra requisições simples como inserts, counts, etc
sync_redis = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cliente do Redis assíncrono (TornadoRedis)
# Here is the magic! Use esse client sempre que você precisar blockar o request
# para esperar por algum resultado
async_redis = tornadoredis.Client()
async_redis.connect()


class BaseHandler(web.RequestHandler):
    """
    Extendi o RequestHandler do Tornado para criar um método simples que pega
    o static_path nos settings da aplicação e concatena com o caminho dos
    templates. A partir de agora, todos os handlers que precisarem dessa função
    para renderizar os templates podem extender essa classe.
    """
    def templates_path(self):
        return self.application.settings['static_path'] + '/templates'


class MainHandler(BaseHandler):
    """
    O handler principal do projeto, nothing here!
    """
    def get(self):
        self.render(self.templates_path() + "/home.html")


class WorldHandler(BaseHandler):
    """
    Renderiza mensagens bufferizadas e form para envio de mensagens.
    """

    def get(self):
        self.render(self.templates_path() + "/world.html")


class UpdateHandler(BaseHandler):
    """
    Trabalha de forma síncrona fazendo um 'insert' na lista
    'global_notifications'. Um insert na lista pro redis é um push.
    """

    def post(self):
        post_data = json.loads(self.request.body.decode("utf-8"))
        message = post_data['message']
        sync_redis.rpush('global_notifications', message)
        self.set_status(200)


class FetchHandler(BaseHandler):
    """
    Aqui acontece toda coisa assíncrona da seguinte forma:
    1 - A aplicação recebe um request pra url '/fetch/' e despacha para o
        handler;
    2 - O hander inicia uma tarefa assíncrona do Tornado (algo BEM parecido as
        promises do JavaScript) e já atribui o seu retorno a uma variável
        'response';
    3 - Essa tarefa chama o redis assíncrono para executar um blpop: cria e/ou
        começa a 'escutar' uma lista no Redis;
    4 - Caso não haja nenhuma entrada nessa lista, o cliente do Redis blocka
        a requisição e espera um (in)determinado tempo (no caso 15 segundos) até
        que o Redis encontre alguma entrada nessa lista e devolve o valor dessa
        entrada;
    5 - Se já existe alguma entrada nessa lista, o Redis devolve esse valor
        imediatamente;
    """
    @gen.coroutine
    def get(self):
        response = {'status': 0}
        response['message'] = yield gen.Task(async_redis.blpop,
            'global_notifications', 15)

        if response['message']:
            response['status'] = 1

        self.write(response)


# Definição da aplicação
application = web.Application(
    [
        # urls da aplicação
        (r"/", MainHandler),
        (r"/world-chat", WorldHandler, None, 'world_chat'),
        (r"/fetch", FetchHandler),
        (r"/update", UpdateHandler),
    ],
    # settings da aplicação
    debug=True,
    static_path="/vagrant/static",)

# Instancia um Tornado server passando a aplicação como parâmetro.
# O server então sabe que deve servir essa aplicação
http_server = httpserver.HTTPServer(application)
# Dizemos que o servidor vai servir essa aplicação na porta '8080'
http_server.listen(8080)
# Levanta o servidor I/O non-blocking do Tornado
ioloop.IOLoop.instance().start()
