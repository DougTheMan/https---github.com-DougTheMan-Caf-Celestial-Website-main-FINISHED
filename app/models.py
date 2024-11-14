from app import db, app
from datetime import datetime

from flask_login import UserMixin

#from app.security import f  

import os

#--------------------------------------
#está tendo tendo problema no upgrade "must add constriant "

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String, nullable=False)              
    email = db.Column(db.String, nullable=False, unique=True)   
    senha = db.Column(db.String, nullable=False)
    celestianus = db.Column(db.Integer, default=0)               
    adm = db.Column(db.Boolean, default=0)
    status = db.Column(db.String, nullable=True)           #status string, tipo se o cara faz merda
                                                        #ele ganha status de monitorar ou banido para banir       

class Denuncias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    motivo = db.Column(db.String)

    id_item = db.Column(db.Integer)
    id_usuario = db.Column(db.Integer)#pega do user atual no save do forms
    id_review = db.Column(db.Integer)# pq review? para saber se o cara escreveu niggers como avaliação

    tempo = db.Column(db.DateTime, default=datetime.now())
#---------------------------------------------------------------------------------------------------------------

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    descricao = db.Column(db.String)
    qntd_cel = db.Column(db.Integer)

    foto = db.Column(db.String, nullable=True, default='404.png')

class Itens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    descricao = db.Column(db.String, nullable=False)
    qntdestoque = db.Column(db.Integer, default=0)
    preco = db.Column(db.Float, nullable=False)
    preco_novo = db.Column(db.Float, nullable=True) #ok, cadastra com preço, se mudar o preço editando
                                    #os preços, ele considera como especial, add especial e mostra 
                                    #considerar pesquisar e entender mais a fundo
    
    avaliacao = db.Column(db.Float, default=0.0) #quantidade TOTAL D EESTRELAS
    qntd_vendidas = db.Column(db.Integer,default=0) #acaba dividindo a avaliação
    especial = db.Column(db.Integer, nullable=True, default=0)

    foto = db.Column(db.String, nullable=True, default=None)
    foto2 = db.Column(db.String, nullable=True, default=None)
    foto3 = db.Column(db.String, nullable=True, default=None)
    foto4 = db.Column(db.String, nullable=True, default=None)

    def descricao_resumo(self):
        return f"{self.descricao[:56]}..."
    
    def descricao_resumo_menor(self):
        return f"{self.descricao[:24]}..."
    
    def titulo_resumo(self):
        return f"{self.titulo[:42]}"
    
    def deliten(self):
        db.session.delete(self)



class registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    id_usuario_comprador = db.Column(db.Integer)
    id_item_comprado = db.Column(db.Integer)
    qntd_comprado = db.Column(db.Integer)   #quando comprado automaticamente negativar no banco de dados
    preco_total_comprado = db.Column(db.Float)
    id_cartao = db.Column(db.Integer)   #Precisa arrumar isso que não foi acabado
    id_endereco = db.Column(db.Integer) 
    #forma_de_entrega = db.Column(db.String(20), nullable=False) # Se o id endereço == 0: é para a loja
    tempo = db.Column(db.DateTime, default=datetime.now())
    # seria interessante fazer o seguinte, o dono afirma que enviou e o cliente avisa que chegou
    # enviado (para o chefe)
    # entregue (para o cliente)


class EstoqueVouch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario_scomprador = db.Column(db.Integer)
    id_voucher_comprado = db.Column(db.Integer)
#---------------------------------------------------------------------------------------------------------------

class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    logradouro = db.Column(db.String, nullable = False)     # se é uma rua, avenida, travessa ou vila
    numero = db.Column(db.Integer, nullable = False)        #num da casa
    complemento = db.Column(db.String, nullable = False)    #complemento
    bairro = db.Column(db.String, nullable = False)         #bairro duh
    cidade = db.Column(db.String, nullable = False)
    sigla_estado = db.Column(db.String, nullable = False)
    cep = db.Column(db.Integer, nullable = False)           #cep... é o cep

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    usuario = db.relationship('Usuario', backref=db.backref('endereco', lazy=True)) #aqui ta certo, segundo chatgpt


class Carrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_itens = db.Column(db.Integer, db.ForeignKey('itens.id'),nullable=True)
    itens = db.relationship(Itens, backref=("itens"))
    qntd_item = db.Column(db.Integer, nullable=True) 
    id_usuario = db.Column(db.Integer)#pega do user atual no save do forms


class Pagamento(db.Model):  #cara... many to one relationship
    id = db.Column(db.Integer, primary_key=True)
    nome_titular = db.Column(db.String, nullable = False)       # isso tudo é barrado na entrada pq aqui se cadastra só cryptado
    num_cartao = db.Column(db.String, nullable = False)        #max 16 digitos
    data_vencimento = db.Column(db.String, nullable = False)   #max 4 , ex 08/25
    cvv = db.Column(db.String, nullable = False)            #max de 3 pq é assim

    id_usuario = db.Column(db.Integer) #funfa mas n ta ligado
    #https://medium.com/@mandyranero/one-to-many-many-to-many-and-one-to-one-sqlalchemy-relationships-8415927fe8aa
    # id_usuario_pag = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    # usuario_pag = db.relationship('Usuario', backref=db.backref('pagamento')) #aqui ta certo, segundo chatgpt
    
    def revelar_num(self):  #tudo está encryptado mas está em bytes. 
                            #entender como seguir e tirar bytes do começo na string
        return f'{self.num_cartao}'
    
    def revelar_data(self):
        return f'{self.data_vencimento}'
    
    def revelar_cvv(self):
        return f'{self.cvv}'

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, nullable=True)

#criar o PODERCOMENTAR, que quando comprar cria um registro que a pessoa pode escrever um review

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(500), nullable=False)
    estrela = db.Column(db.Integer, nullable=False)
    Itens_id = db.Column(db.Integer, db.ForeignKey('itens.id'), nullable=True)  # Relacionando ao Produto
    Itens = db.relationship('Itens', backref='reviews', lazy=True)
    id_usuario = db.Column(db.Integer)  #botar nullable false (não deu agora pq tem nulos ja na tabela e ele não deixa)

#class Avalitem(db.Model):
#   id = db.Column(db.Integer, primary_key=True)
#    estrelas = db.Column(db.Integer, nullable=False)

# reviews de Usuario
# comentario
# estrela

# avaliação do Post
# pega todas as estelas do post e media

# se_usuario_comprou_estee_item 
# quando usuario compra é criado 

