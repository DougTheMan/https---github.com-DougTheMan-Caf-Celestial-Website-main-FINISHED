from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, BooleanField, FileField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from app.models import Usuario, Itens, Endereco, Carrinho, Pagamento, Voucher, Review, registro, EstoqueVouch, Denuncias
from app import db, app
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import current_user
#from app.security import f #ta no security

from werkzeug.utils import secure_filename
import os
from app import bcrypt

#-----#-----#-----#-----#-----#-----#
#Cadastro e Login

class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha: ', validators=[Length(min=6, max=24), DataRequired()])
    btnSubmit = SubmitField(' "Logar" ! ')


class CadastroForm(FlaskForm):
    usuario = StringField('Nome Usuário: ', validators=[Length(min=3, max=32), DataRequired()])
    email = StringField('E-mail: ', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha: ',validators=[Length(min=6, max=24), DataRequired()])
    senha2 = PasswordField('Confirme a Senha: ', validators=[DataRequired()]) #Lá no views diz que tem que ser comparado
    btnSubmit = SubmitField('Cadastrar!')
        

    def save(self):
        add = Usuario(  #RESUMIDAMENTE, a barreira é no views, aqui faz modificações e acaba no models
            usuario = self.usuario.data.title().strip(),
            email = self.email.data.lower(), #aqui transforma em minusculo
            senha = bcrypt.generate_password_hash(self.senha.data)  #Aqui Crypta a senha

        )
        db.session.add(add)
        db.session.commit()


   #colocar LOGIN AUQI TA NÂO SE ESQUECE
class CepForm(FlaskForm):

   cep = IntegerField('CEP: ', validators=[DataRequired(), Length(min=8, max=8)])
   logradouro = StringField('Logradouro: ', validators=[DataRequired()])
   numero = IntegerField('Número da casa: ', validators=[DataRequired()])
   complemento = StringField('Complemento: ', validators=[DataRequired()])
   bairro = StringField('Bairro: ', validators=[DataRequired()])
   cidade = StringField('Cidade: ', validators=[DataRequired()])
   sigla_estado = StringField('Sigla: ', validators=[DataRequired(), Length(min=2, max=2)])
   id_usuario = IntegerField("") # vai ser colocado abaixo

   btnSubmit = SubmitField('Cadastrar cep!')
   
   def save(self, id):
    add = Endereco(
        cep = self.cep.data,
        logradouro = self.logradouro.data,
        numero = self.numero.data,
        complemento = self.complemento.data,
        bairro = self.bairro.data,
        cidade = self.cidade.data,
        sigla_estado = self.sigla_estado.data,
        id_usuario = id #vem do views que joga user atual para cá
   )

    
    db.session.add(add)
    db.session.commit()

class CartaoForm(FlaskForm):
    nome_titular = StringField('Nome do Titular: ', validators=[DataRequired()])
    num_cartao = StringField('Número do Cartão', validators=[DataRequired(), Length(min=16, max=16)])
    data_vencimento = StringField('Data de Vencimento: ', validators=[DataRequired()])
    cvv = StringField('Número de Segurança',validators=[DataRequired(),Length(min=3, max=3) ])
    btnSubmit = SubmitField('Cadastrar Cartão')


    def save(self, id): 

        # self.num_cartao.data = bytes(self.num_cartao.data, 'utf-8')
        # self.data_vencimento.data = bytes(self.data_vencimento.data, 'utf-8')
        # self.cvv.data = bytes(self.cvv.data, 'utf-8')

        add = Pagamento(
            
            nome_titular = self.nome_titular.data, #será que ta certo? ele responde b'(coisa)'
            num_cartao = self.num_cartao.data, #f.encrypt(self.num_cartao.data),
            data_vencimento = self.data_vencimento.data, #f.encrypt(self.data_vencimento.data), 
            cvv = self.cvv.data, #f.encrypt(self.cvv.data), 
            id_usuario = id #vem do views que joga user atual para cá
        )
        db.session.add(add)
        db.session.commit()



#-----#-----#-----#-----#-----#-----#
    

class ItensForm(FlaskForm):
    titulo = StringField("Nome do Produto: ", validators=[DataRequired()])
    descricao = StringField("Descrição: ", validators=[DataRequired()])
    qntdestoque = IntegerField("Estoque", validators=[DataRequired()])
    preco = FloatField("Preço: | EX: 80.90", validators=[DataRequired()])
    especial = IntegerField("0 para não promoção || 1 para promoção ", validators=[])
    foto = FileField("Foto Num 1",validators=[DataRequired()])  #precisa mudar aqui, ali em baixo no save e db models
    foto2 = FileField("Foto Num 2")
    foto3 = FileField("Foto Num 3")
    foto4 = FileField("Foto Num 4")
    btnSubmit = SubmitField('Registrar Item')


    def save(self):

        #pega foto do form, transforma em seguro, vai ver se não tem dropdatabase.png

        foto = self.foto.data
        nome_seguro = secure_filename(foto.filename)

        caminho = os.path.join(
            #pegar a pasta que está nosso projeto
            os.path.abspath(os.path.dirname(__file__)),
            #define pasta que configuramos para upload
            app.config['UPLOAD_FILES'],
            #A pasta que está para Post
            'fotos',nome_seguro
        )

        foto.save(caminho)

        if self.foto2.data != None:

            foto2 = self.foto2.data
            nome_seguro2 = secure_filename(foto2.filename)

            caminho2 = os.path.join(
                #pegar a pasta que está nosso projeto
                os.path.abspath(os.path.dirname(__file__)),
                #define pasta que configuramos para upload
                app.config['UPLOAD_FILES'],
                #A pasta que está para Post
                'fotos',nome_seguro2
            )

            foto2.save(caminho2)
        else:
            nome_seguro2 = None

        if self.foto3.data != None:
            foto3 = self.foto3.data
            nome_seguro3 = secure_filename(foto3.filename)

            caminho3 = os.path.join(
                #pegar a pasta que está nosso projeto
                os.path.abspath(os.path.dirname(__file__)),
                #define pasta que configuramos para upload
                app.config['UPLOAD_FILES'],
                #A pasta que está para Post
                'fotos',nome_seguro3
            )

            foto3.save(caminho3)
        else:
            nome_seguro3 = None

        if self.foto4.data != None:
            foto4 = self.foto4.data
            nome_seguro4 = secure_filename(foto4.filename)
            #acho que o erro é que ele se enrola nesses if e fracassa o resto
            caminho4 = os.path.join(
                #pegar a pasta que está nosso projeto
                os.path.abspath(os.path.dirname(__file__)),
                #define pasta que configuramos para upload
                app.config['UPLOAD_FILES'],
                #A pasta que está para Post
                'fotos',nome_seguro4
            )

            foto4.save(caminho4)
        else:
            nome_seguro4 = None
            #Funciona. Como? parece que depende de computador ou algo do tipo
            #Porra, não entendo pq, ele tenta salvar o arquivo mas acha que o arquivo está em outro pc
            #exemplo: no mue pc em guaramirim funciona tudo. Aqui em senai não. QUE? 

        add = Itens(
            titulo = self.titulo.data,
            descricao = self.descricao.data,
            qntdestoque = self.qntdestoque.data,
            preco = self.preco.data,
            especial = self.especial.data,
            foto=nome_seguro,    #salvo em seguro
            foto2=nome_seguro2,
            foto3=nome_seguro3,
            foto4=nome_seguro4
        )
        
            #da erro quando tenta postar menos que 4 fotos, não entendo.
            #se você postar 1 imagem, da erro. se você tentar preencher o formulário colocando outra foto da certo. UE

        db.session.add(add)
        db.session.commit()

def novasenha(self):
    add = Usuario(
       senha = self.senha.data
    )
    db.session.commit()
        
class DelForm(FlaskForm):
    btnSubmit = SubmitField('DELETAR CONTA')
    
    def remove(self):
        db.session.delete(self)



class EditItensForm(FlaskForm):
    titulo = StringField("Nome do Produto: ", validators=[DataRequired()])
    descricao = StringField("Descrição: ", validators=[DataRequired()])
    qntdestoque = IntegerField("Estoque", validators=[DataRequired()])
    preco = FloatField("Preço: | EX: 80.90", validators=[DataRequired()])
    especial = IntegerField("0 para não promoção || 1 para promoção ", validators=[DataRequired()])

    btnSubmit = SubmitField('Editar Item')


class CarrinhoForm(FlaskForm):
    qntd_item = IntegerField("", validators=[DataRequired()])
    id_itens = IntegerField("")
    id_usuario = IntegerField("")
    btnSubmit = SubmitField('Adicionar ao Carrinho')

    def save(self, id, useratual):
        #pega do views Detalhes Item


        add=Carrinho(
            qntd_item = self.qntd_item.data,
            id_itens = id,
            id_usuario = useratual
        )
        db.session.add(add)
        db.session.commit()
    
class RegistroForm(FlaskForm):
    id_usuario_comprador = IntegerField(None)
    id_item_comprado = IntegerField(None)
    qntd_comprado = IntegerField(None)
    preco_total_comprado = FloatField(None)
    id_cartao = IntegerField(None)
    id_endereco = SelectField(None)
    btnSubmit = SubmitField("Comprar")

    def save(self, pid, c, q, useratual, cartao, end):
        #pega do views Detalhes Item

        add=registro(
            id_usuario_comprador = useratual,
            id_item_comprado = pid,
            qntd_comprado = q,
            preco_total_comprado = c,
            id_cartao = cartao,
            id_endereco = end
        )
        db.session.add(add)
        db.session.commit()

class EstoqueVouchForm(FlaskForm):
    id_usuario_comprador = IntegerField(None)
    id_voucher_comprado = IntegerField(None)
    btnSubmit = SubmitField("Resgatar")

    def save(self, pid, useratual):
        #pega do views Detalhes Item

        add=EstoqueVouch(
            id_usuario_comprador = useratual,
            id_item_comprado = pid,
        )
        db.session.add(add)
        db.session.commit()


class VoucherForm(FlaskForm):
    nome = StringField("Titulo do Voucher:",validators=[DataRequired(Length(min=0,max=64))])
    descricao = StringField("Descricao do Voucher:",validators=[DataRequired(Length(min=0,max=215))])
    qntd_cel = IntegerField("Celestianus do Voucher:",validators=[DataRequired(Length(min=0,max=1000000000))])
    foto = FileField("Foto:" ,validators=[DataRequired()])  #precisa mudar aqui, ali em baixo no save e db models
    btnSubmit = SubmitField('Registrar voucher')

    def save(self):

        foto = self.foto.data
        nome_seguro = secure_filename(foto.filename)

        add=Voucher(
        nome = self.nome.data,
        descricao = self.descricao.data,
        qntd_cel = self.qntd_cel.data,
        foto=nome_seguro
        )

         #caminho da foto
        caminho = os.path.join(
            #pegar a pasta que está nosso projeto
            os.path.abspath(os.path.dirname(__file__)),
            #define pasta que configuramos para upload
            app.config['UPLOAD_FILES'],
            #A pasta que está para Post
            'fotos',nome_seguro
        )

        foto.save(caminho)
        

        db.session.add(add)
        db.session.commit()

class ReviewForm(FlaskForm):
    descricao = StringField('Comentario:', validators=[DataRequired()])
    estrela = IntegerField('Estrelas: ', validators=[DataRequired()])
    btnSubmit = SubmitField('Enviar Comentário')

    def validate_estrela(self, field):
        if field.data < 1 or field.data > 5:
            raise ValidationError('As estrelas devem estar entre 1 e 5.')

    def save(self,iid, uid):
        add = Review(
            descricao=self.descricao.data,
            estrela=self.estrela.data,
            Itens_id= iid,
            id_usuario=uid
            
        )
        
        pega_item = Itens.query.filter_by(id=iid).first() #pega id do item
        pega_item.avaliacao = pega_item.avaliacao + float(self.estrela.data) #soma as estrelas
        pega_item.qntd_vendidas = pega_item.qntd_vendidas + 1 #NÃO É VENDIDAS, É REVISADAS MAS N DA PARA MUDAR O NOME

        db.session.add(add)
        db.session.commit()

class DenunciaForm(FlaskForm):
    motivo = StringField('Motivo da Denúncia-', validators=[DataRequired()])
    
    btnSubmit = SubmitField('Denunciar')

    def save(self,motivoR ,id_itemR, id_usuarioR, id_reviewR):
        add = Denuncias(
            motivo = motivoR,
            id_item = id_itemR,
            id_usuario = id_usuarioR,
            id_review = id_reviewR

        )
        db.session.add(add)
        db.session.commit()