db = SQLAlchemy()
    
# MODELOS DE BANCO DE DADOS
class Biblioteca(db.Model):
    __tablename__ = 'livros'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.titulo,
            'autor': self.autor,
            'genero': self.genero,
            
        }


info = Info(title="API Biblioteca", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home = Tag(name="Documentação", description="Seleção de documentação: Swagger")
livros = Tag(name="Livros", description="Adição, pesquisa e remoção de livros à base")


def listar_livros():
    """
    Lista todos os livros cadastrados no banco  de dados

    tags:
          - Livros
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
