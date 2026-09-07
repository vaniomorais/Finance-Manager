from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS

info = Info(title="API Biblioteca", version="1.0.0")
app = OpenAPI(
    __name__,
    info=info,
    doc_prefix='/docs',
    doc_url='/openapi.json'
)


@app.route('/openapi.json', methods=['GET'])
def openapi_json():
    return app.view_functions['openapi.doc_url']()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
CORS(app)

#MODELOS DE BANCO DE DADOS
class Biblioteca(db.Model):
    __tablename__ = 'livros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    gênero = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "gênero": self.gênero,
        }

#DEFININDO TAGS
home = Tag(name="Documentação", description="Seleção de documentação: Swagger")
livros = Tag(name="Livros", description="Adição, pesquisa e remoção de livros à base")
#ROTAS
@app.route('/livros', methods=['GET'])
def listar_livros():
    """
    Lista todos os livros cadastrados no banco  de dados

    tags:

Livros
      responses:
        200:
          description: Livros carregados com sucesso
        500:
          description: Erro no servidor
    """

    livros = Biblioteca.query.all()
    livros_data = []

    for livro in livros:
        livro_dict = livro.to_dict()
        livros_data.append(livro_dict)

    return jsonify(livros_data), 200


@app.route('/pesquisa',  methods=['POST'])
def pesquisa():
    return "nome_livros"


@app.route('/deletar/<id>livros', methods=['DELETE'])
def deletar(id):
    return f"livro deletado: {id}"

@app.route('/cadastro/<obra>')
def cadastro(obra):
    return f"cadastrar_obra: {obra}"

if __name__ == '__main__':
    # Cria tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()

    # Inicia servidor em modo debug
    app.run(debug=True, host='127.0.0.1', port=5000)
