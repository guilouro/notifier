from tornado import gen
import tornado.httpserver as httpserver
import tornado.web as web
import tornado.ioloop as ioloop
import redis
import tornadoredis

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
    o static_path nos settings da aplicação. A partir de agora, todos meus
    handlers que precisarem dessa função para acessar os arquivos estáticos
    podem extender essa classe.
    """
    def static_url(self):
        return self.application.settings['static_path']


class MainHandler(BaseHandler):
    """
    O handler principal do projeto, nothing here!
    """
    def get(self):
        self.render(self.static_url() + "/index.html")


class UpdateHandler(BaseHandler):
    """
    Esse handler trabalha de forma síncrona seguindo os seguintes passos:
    1 - A aplicação recebe um request pra url '/update/' e despacha para o
        handler;
    2 - O handler possui a inteligência de reconhecer se essa requisição é um
        GET ou um POST (ou um PATCH, UPDATE ou DELETE);
    3 - Caso ele reconheça um GET, ele irá renderizar uma view contendo um
        formulário para o envio de uma mensagem;
    4 - Caso tenha sido um POST, ou seja, o formulário foi preenchido e enviado,
        ele vai fazer um 'insert' na lista 'global_notifications'. Um insert na
        lista pro redis é um push.
    """

    def get(self):
        self.render(self.static_url() + "/update.html")

    def post(self):
        sync_redis.rpush('global_notifications',
            self.get_body_argument('message'))
        self.set_status(200)


class FetchHandler(BaseHandler):
    """
    Nesse handler acontece toda coisa assíncrona da seguinte forma:
    1 - A aplicação recebe um request pra url '/fetch/' e despacha para o
        handler;
    2 - O hander inicia uma tarefa assíncrona do Tornado (algo BEM parecido as
        promises do JavaScript) e já atribui o seu retorno a uma variável
        'response';
    3 - Essa tarefa chama o redis assíncrono para executar um blpop: cria e/ou
        começa a 'escutar' uma lista no Redis;
    4 - Caso não haja nenhuma entrada nessa lista, o cliente do Redis blocka
        a requisição e espera um (in)determinado tempo (no caso 0, pra sempre)
        até que o Redis encontre alguma entrada nessa lista e devolve o valor
        dessa entrada;
    5 - Se já existe alguma entrada nessa lista, o Redis devolve esse valor
        imediatamente;
    """
    @gen.coroutine
    def get(self):
        response = yield gen.Task(async_redis.blpop,
            'global_notifications', 0)
        self.write(response)


# Definição da aplicação
application = web.Application(
    [
        # urls da aplicação
        (r"/", MainHandler),
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
