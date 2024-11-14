from app import app, db
from flask import abort, render_template, url_for, redirect, request, flash, send_file, jsonify, session
from app.forms import ReviewForm, CadastroForm, ItensForm, LoginForm, DelForm, CepForm, CarrinhoForm, CartaoForm, VoucherForm, RegistroForm, EditItensForm, DenunciaForm
from app.models import Usuario, Itens, Endereco, Carrinho, Voucher, Reserva, Pagamento, Review, EstoqueVouch, registro
from flask_login import login_required, current_user, login_user, logout_user, LoginManager
from app import bcrypt
from fpdf import FPDF
from werkzeug.utils import secure_filename
from datetime import datetime


from sqlalchemy import desc

import random
import os
import io

#-----#-----#-----#-----#-----#-----#

@app.route('/') #Aqui ficar de olho se está certo
def HomePage():

    useratual = current_user    #ele funciona, se não tiver logado ele aparece literalmente nada
        #se existe na tabela endereco se tiver useratual.id == id_user mostra 
    
    if useratual.is_authenticated:
        pega_endereco = Endereco.query.filter_by(id_usuario=useratual.id).first()
        if pega_endereco == None:
            id_endereco = None
        else:
            id_endereco = pega_endereco.id

        pega_cartao = Pagamento.query.filter_by(id_usuario=useratual.id).first()
            #parece que assim é ótimo para pegar apenas uma informação, será que tem como .all()?
        if pega_cartao == None:
            id_cartao = None
        else:
            id_cartao = pega_cartao.id
    else:
        pega_endereco = None
        id_endereco = None

        pega_cartao = None
        id_cartao = None

    mensagens = ["Nós temos ofertas novas sempre,fique de olho para não perder elas!"
                 ,"Não, não iremos entregar vouchers de graça, não insista."
                 ,"Estamos contratando! 3 voluntários com experiência em programação. Para trocar os últimos 3."
                 ,"Aproveite ás sextas e venha á nossa cafeteria! Temos Show ao-vivo"
                 ,"se estiver em um incêndio entre no chuveiro lá você não pega fogo."
                 ,"Se você parar pra pensar você vai pensar parado"
                 ,"Se beleza fosse crime eu seria inocente"
                 ,"eu acho que os [...]. Meus advogados não me permitiram acabar a frase"
                 ,"Eu queria ser um tijolo."
                 ,"Portal 2 é um bom jogo."
                 ,"Fabiano, você ainda me paga por ter me pego por trás no airsoft."
                 ,"Eu como o whey protein do rick, mas ele não sabe, ele acha que é um rato."
                 ,"Precisamos de alguns cobaias para nossos novos sabores 😈"
                 ,"Meu avô andava a pé, meu pai de ferrari, e eu com uma charrete, eu mantenho as tradições."
                 ,"O medo que você não supera se torna o seu limte - Marçal, Enzo, 2024 "
                 ,"Moisés abriu os mares, Elon Musk abriu a tesla e eu abri uma conta no SERASA."]
    
    aleatorio = random.randint(0,15)

    mensagem_escolhida = mensagens[aleatorio]
    
    return render_template('home.html', useratual = useratual, pega_endereco=pega_endereco, pega_cartao=pega_cartao, mensagem_escolhida = mensagem_escolhida,id_cartao=id_cartao, id_endereco=id_endereco)



@app.route('/sobrenos/')
def SNPage():
    useratual = current_user    #ele funciona, se não tiver logado ele aparece literalmente nada
    #preciso me lembrar como muda as infomações caso não tenha useratual
    
    return render_template('sobrecafe.html', useratual = useratual)


@app.route('/fidelidade/', methods=['GET', 'POST'])
@login_required
def FidelidadePage():
    useratual = current_user
    dados = Voucher.query.order_by('id').all()


    estoque_vouch = EstoqueVouch.query.filter_by(id_usuario_scomprador=useratual.id).all()


    vouchers_resgatados = {}
    for item in estoque_vouch:
        if item.id_voucher_comprado in vouchers_resgatados:
            vouchers_resgatados[item.id_voucher_comprado] += 1
        else:
            vouchers_resgatados[item.id_voucher_comprado] = 1

    context = {'dados': dados, 'vouchers_resgatados': vouchers_resgatados}

    if request.method == 'POST':
        voucher_id = int(request.form.get('voucher_id'))
        voucher = Voucher.query.get(voucher_id)

        if voucher and current_user.celestianus >= voucher.qntd_cel:

            current_user.celestianus -= voucher.qntd_cel
            db.session.commit()

         
            novo_voucher = EstoqueVouch(id_usuario_scomprador=useratual.id, id_voucher_comprado=voucher.id)
            db.session.add(novo_voucher)
            db.session.commit()

            flash(f'Voucher de {voucher.qntd_cel} Celestianus adquirido com sucesso!', 'success')
        else:
            flash('Quantidade de Celestianus insuficiente para adquirir o voucher.', 'error')

 
        return redirect(url_for('FidelidadePage'))

    return render_template('fidelidade.html', useratual=useratual, context=context)


@app.route('/menu-produtos/',methods=['GET', 'POST'])
def MenuPage():
    useratual = current_user

    dados = Itens.query.order_by('id')
    context = {'dados' : dados.all()}


    return render_template('menu.html',useratual = useratual, context=context)

@app.route('/menu-produtos/pesquisa=', methods=['GET', 'POST'])
def MenuPesquisaPage():
    useratual = current_user

    query = request.form.get('pesquisa', '')
    dados = Itens.query.filter(Itens.titulo.ilike(f'%{query}%')).order_by('titulo')  # Consulta com LIKE para pesquisa
    context = {'dados' : dados.all()}

    return render_template('menupesquisa.html',useratual = useratual, context=context)


#ARRUMAR RESERVAS CALENDARIO TA FUDIDO                 VSFD ODEIO CALENDARIO DE MERDA AAAAAAAAAAAAAAAAAAAAAAAAAA
@app.route('/reservas/', methods=['GET', 'POST'])
@login_required
def ReservasPage():
    useratual = current_user

    dados = Reserva.query.order_by('id')
    context = {'dados' : dados.all()}
    usuario_id = session.get('user_id')
    reservas_usuario = Reserva.query.filter_by(user_id=usuario_id).all()
    
    reservas_dict = {reserva.data.strftime('%Y-%m-%d'): True for reserva in Reserva.query.all()}
    
    reservas_usuario_data = [{'data': reserva.data.strftime('%d/%m/%Y')} for reserva in reservas_usuario]

    return render_template('reservas.html', useratual=useratual, reservas=reservas_dict, reservas_usuario=reservas_usuario_data, context=context)


@app.route('/reservar/<data_reserva>', methods=['GET'])
@login_required
def reservar(data_reserva):

    return render_template('reserva_data.html', data_reserva=data_reserva, useratual=current_user)


@app.route('/confirmar_reserva/', methods=['POST'])
@login_required
def confirmar_reserva():
    data_reserva = request.form.get('data_reserva')
    useratual = current_user

    # Converte a string da data para um objeto datetime
    data_obj = datetime.strptime(data_reserva, '%Y-%m-%d').date()

    # Verifica se a data já está reservada
    reserva_existente = Reserva.query.filter_by(data=data_obj).first()
    if reserva_existente:
        flash('Essa data já foi reservada. Escolha outra.', 'danger')
        return redirect(url_for('ReservasPage'))

    # Cria uma nova reserva
    nova_reserva = Reserva(data=data_obj)
    nova_reserva.user_id = current_user.id
    db.session.add(nova_reserva)
    db.session.commit()

    flash(f'Reserva confirmada para {data_reserva}', 'success')
    return redirect(url_for('ReservasPage'))


@app.route('/carrinho-de-compras/')
@login_required
def CartPage():
    useratual = current_user

    pega_cartao = Pagamento.query.filter_by(id_usuario=useratual.id).first()
            #parece que assim é ótimo para pegar apenas uma informação, será que tem como .all()?

    checacart = Carrinho.query.filter_by(id_usuario=useratual.id).first()

    dados2 = Itens.query.order_by('id')
    context2 = {'dados2' : dados2.all()}

    dados = Carrinho.query.order_by('id')
    context = {'dados' : dados.all()}

    return render_template('carrinho.html', useratual = useratual, context=context, context2 = context2, pega_cartao=pega_cartao, checacart = checacart)


@app.route('/itens-comprados/lista/')
@login_required
def ItensCompradosPage():
    useratual = current_user
    
    ja_comprou = registro.query.filter_by(id_usuario_comprador=useratual.id).first()
    
    if ja_comprou != None:

        dados = registro.query.order_by('id')
        context = {'dados' : dados.all()}

        dados2 = Itens.query.order_by('id')
        context2 = {'dados2' : dados2.all()}

        dados3 = Usuario.query.order_by('id')
        context3 = {'dados3' : dados3.all()}
    else:
        context = None
        context2 = None

    return render_template('itenscomprados.html', useratual = useratual, context=context, context2 = context2, ja_comprou = ja_comprou)

@app.route('/carrinho-de-compras/comprando-item/<int:id> <float:custo> <int:quantidade> <int:idcarrinho> /', methods=['GET','POST'])#<int:idcartao>/-<int:idendereco>/
@login_required
def ConfirmaCompraPage(id,custo,quantidade, idcarrinho):
    useratual = current_user
    form = RegistroForm()

    erro_mensagem = None

    cid = idcarrinho

    pid = id
    c = custo
    q = quantidade
    
    # se for 0, é para pegar na loja, != 0 é que vai ser o id do cliente
    

    obj = Itens.query.get(pid)
    obj2 = Usuario.query.get(useratual.id)
    

    pega_item = Itens.query.filter_by(id=pid).first()
    if pega_item.qntdestoque < q:
        naopodecomprar = 1
    else:
        naopodecomprar = 0

    pega_cartao = Pagamento.query.filter_by(id_usuario=useratual.id).first()
            #parece que assim é ótimo para pegar apenas uma informação, será que tem como .all()?
    pega_endereco = Endereco.query.filter_by(id_usuario=useratual.id).first()


    if pega_endereco == None:
            choices = ['Pegar na Loja']
            form.id_endereco.choices = choices
    else:
            choices = ['Pegar na Loja','Receber no endereço']
            form.id_endereco.choices = choices

    if form.validate_on_submit():
        try:
            
            if pega_item.qntdestoque >= q:
                
                end=0

                if form.id_endereco.data == 'Pegar na Loja':
                    end = int(0)
                else:
                    end = int(pega_endereco.id)
                    #separação que se for 0 é retirar na loja e se for != 0 é no endereco


                form.save(pid, c, q, useratual.id, pega_cartao.id ,end)

                pega_item.qntdestoque = pega_item.qntdestoque - q

                obj2.celestianus = obj2.celestianus + int(custo)

                db.session.commit()

                obj2 = Carrinho.query.get(cid)
                db.session.delete(obj2)
                db.session.commit()
            else:
                return redirect(url_for('ConfirmaCompraPage'))
        except:
            print("Não foi possivel realizar a compra")

        
        return redirect(url_for('ItensCompradosPage'))
    flash("Produto comprado com sucesso, Processando compra.")
    return render_template('comprando.html', useratual = useratual, pid=pid, c=c, q=q, obj=obj, pega_cartao=pega_cartao, form=form, erro_mensagem=erro_mensagem, naopodecomprar = naopodecomprar, pega_endereco = pega_endereco) 



@app.route('/carrinho-de-compras/deletando-item <int:id> /')
@login_required
def DelCartItem(id):    #AQUI TEM QUE SER LINHA1 (acabei deletando coisas que não deveria)
    useratual = current_user

    objetado = Carrinho.query.filter_by(id_usuario=useratual.id).first()
    
    if objetado != None:    #se confere com o id de quem tenta deletar ele permite

        try:
            obj = Carrinho.query.get(id)   #aqui voce SABE qual id, o que você acabou de receber
            db.session.delete(obj)      #ta dando erro ainda...
            db.session.commit()  

        except:
            print("Não foi possivel Deletar o Item")
    else:
        return redirect(url_for('CartPage'))
    
    return redirect(url_for('CartPage'))
    

@app.route('/detalhes-do-item/<int:id>/',methods = ['GET', 'POST'])  #|INACABADO| Precisa fazer que quando clica no adicionar no carrinho, se autenticado ele permite comprar mas se não modal
def DetalhesItemPage(id):
    useratual = current_user
    erro_mensagem = None

    form3 = DenunciaForm()
    #DENUNCIAS, parece que não funfa ou não envia a nenuncia

    #Fazer assim: Filtra qual id do item é
    #Filtra se o usuário já comprou esse id
    #como fazer? pensar

    item = Itens.query.get(id)

    if useratual.is_authenticated:
        #X = Pesquisar qual registros tem o mesmo id do post
        
        #pesquisar qual X tem o mesmo id do usuário
        permissao_para_comentar = True
        
    else:
        permissao_para_comentar = False

    
    if item is None:
        return render_template('404.html'),404
    
    permissao_para_comentar = registro.query.filter_by(id_usuario_comprador=useratual.id, id_item_comprado=item.id).first() is not None if useratual.is_authenticated else False

    dados2 = Usuario.query.order_by('id')   #procurar uma forma melhor dele fazer a pesquisa
    context2 = {'dados2' : dados2.all()}    

    dados = Review.query.filter_by(Itens_id=id).order_by(Review.id).all()  # Filtrando por id_itens

    dados3 = registro.query.order_by('id')
    context3 = {'dados3' : dados3.all()}
    

    form = CarrinhoForm()
    if form.validate_on_submit():
        if form.qntd_item.data <= item.qntdestoque:
            if form.qntd_item.data >= 1:
                form.save(item.id, useratual.id)
                return redirect(url_for('CartPage'))
            else:
                erro_mensagem = 'Quantidade Inválida'
        else:
            erro_mensagem = 'Quantidade Inválida'

    form2 = ReviewForm()
    if form2.validate_on_submit():
        #AS FUNÇÕES DE AVALIAÇÃO ESTÃO DENTRO DO SAVE
        form2.save(item.id, useratual.id)
        
        return redirect(url_for('DetalhesItemPage', id=item.id)) 
    
    
    return render_template('detalhesitem.html', useratual=useratual, context3=context3, item=item, form=form, form2=form2, form3=form3, dados=dados,context2=context2, erro_mensagem=erro_mensagem, permissao_para_comentar=permissao_para_comentar)

@app.route('/denunciando/<motivoR><int:id_itemR><int:id_usuarioR><int:id_reviewR>', methods=['GET','POST'])
def Denunciando(motivoR,id_itemR,id_usuarioR,id_reviewR):
    form = DenunciaForm()
    #salva e segue a vida
    form.save(motivoR,id_itemR,id_usuarioR,id_reviewR)

    return redirect(url_for('DetalhesItemPage', id=id_itemR))

    

#-- Logins e Cadastros

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "HomePage"  #Joga para Cá se não tiver login

@login_manager.user_loader #|PRONTO|
def load_user(usuario_id):
    return Usuario.query.get(int(usuario_id))

@app.errorhandler(404)
def page_not_found(e):
    #está setado para 404 explicitamente
    return render_template('404.html'),404

@app.route('/cadastro/', methods = ['GET', 'POST']) #|PRONTO| transforma email em minusculo, transforma usuario title(), tem avisos de erros e aviso de ja estar logado
def CadastroPage():
    useratual = current_user

    form = CadastroForm()
    erro_mensagem = None

    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data.lower().strip()).first():
            erro_mensagem = "Opa! Esse email ja foi cadastrado!"
        else:
            if form.senha.data != form.senha2.data:
                erro_mensagem = "Revise! As senhas não são iguais!"
            else:
                form.save()

                user = Usuario.query.filter_by(email=form.email.data.lower()).first()       #entenda a lógica, aqui checa se email existe
                if user:
                    if bcrypt.check_password_hash(user.senha, form.senha.data):    #checa se existe a senha
                        login_user(user, remember=True)    #CONSEGUI PORRA VOU CHORAR mudei para remember true
                        return redirect(url_for('HomePage'))
                
    return render_template('cadastro.html', form = form, useratual = useratual, erro_mensagem = erro_mensagem)

@app.route('/login/', methods=['GET','POST']) # |PRONTO| Transforma gmail em minusculo, tem avisos de erro e aviso de ja estar logado
def LoginPage():                    
    useratual = current_user                           
    form = LoginForm() 
    erro_mensagem = None

    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data.lower()).first()       #entenda a lógica, aqui checa se email existe
        if user:
            if bcrypt.check_password_hash(user.senha, form.senha.data):    #checa se existe a senha
                login_user(user, remember=True)    #CONSEGUI PORRA VOU CHORAR mudei para remember true
                return redirect(url_for('HomePage'))
            else:
                erro_mensagem = 'Erro: Senha inválida!'
        else:
                erro_mensagem = 'Erro: Email Não existe!'           
    elif erro_mensagem != None: 
        erro_mensagem = 'Erro: Email e Senha Incorretos!' #não da nada quando escreve dadawda dwasdaw (baboseira)

    return render_template('login.html', form = form, useratual = useratual, erro_mensagem = erro_mensagem )

@app.route('/logout/', methods=['GET','POST']) #|PRONTO|
@login_required
def LogoutPage():
    logout_user()
    return redirect(url_for('MenuPage'))


#-- Para Testes / ADMINISTRAÇÃO

@app.route('/index/')  # |INACABADO|
def IndexPage():                

    return redirect(url_for('MenuPage'))


@app.route('/!@#$%Administração-De-Adm%$#@!/itens/', methods = ['GET', 'POST'])   # |INACABADO| Cadastro produto e mostra eles, cadastro vouchers, PRECISA deletar eles e bloquear Usuários?
@login_required #e que seja de adm o login em. quero que em confirgs, se for adm ele possa entrar
def CadProdPage():
    #if login epsecial == True permitir entrada
    useratual = current_user
    
    if useratual.adm == 1:
        form = ItensForm()

        dados = Itens.query.order_by('id')
        context = {'dados' : dados.all()}

        if form.validate_on_submit():
            form.save()
            #PORRA MUDAR QUE NAO DA PARA CADASTRAR PRODUTO COM , 
            return redirect(url_for('CadProdPage'))
    else:
        print("Usuário nome: " ,useratual.usuario, " | Id: " ,useratual.id ," | Tentou acessar a administração sem permissão") 
        return redirect(url_for('HomePage'))
    
    return render_template('cadproduto.html', form=form, useratual = useratual, context=context)

@app.route('/321yed65twfqy3e2q"adm"3rdcyqfkie2e2hpe12/deletando-item/<int:id>/')# |PRONTO|
@login_required
def DelItemPage(id):
    useratual = current_user
    if useratual.adm == 1:
        obj = Itens.query.get(id)
        #deleta foto, o arquivo dela
        if obj.foto:
            try:
                os.unlink(os.path.join(r'app/static/img/fotos/',str(obj.foto)))
            except:
                print('erro')
        if obj.foto2:
            try:
                os.unlink(os.path.join(r'app/static/img/fotos/',str(obj.foto2)))
            except:
                print("imagem não existe mais")
        if obj.foto3:
            try:
                os.unlink(os.path.join(r'app/static/img/fotos/',str(obj.foto3)))
            except:
                print("imagem não existe mais")
        if obj.foto4: 
            try:
                os.unlink(os.path.join(r'app/static/img/fotos/',str(obj.foto4)))
            except:
                print("imagem não existe mais")
        
        db.session.delete(obj)
        db.session.commit()

        return redirect(url_for('CadProdPage'))
    else:
        return redirect(url_for('MenuPage'))


@app.route('/!@#$%Administração-De-Adm%$#@!/vouchers/', methods = ['GET', 'POST'])   # |INACABADO| Cadastro produto e mostra eles, cadastro vouchers, PRECISA deletar eles e bloquear Usuários?
@login_required 
def CadVouPage():
    useratual = current_user
    
    if useratual.adm == 1:
        form2 = VoucherForm()

        dados3 = Usuario.query.order_by('id')
        context3 = {'dados3' : dados3.all()}

        dados2 = EstoqueVouch.query.order_by('id')
        context2 = {'dados2' : dados2.all()}

        dados = Voucher.query.order_by('id')
        context = {'dados' : dados.all()}

        if form2.validate_on_submit():
            form2.save()
            
            return redirect(url_for('CadVouPage'))
    else:
        print("Usuário nome: " ,useratual.usuario, " | Id: " ,useratual.id ," | Tentou acessar a administração sem permissão") 
        return redirect(url_for('HomePage'))
    
    return render_template('cadvoucher.html', form2=form2, useratual = useratual, context=context, context2=context2, context3=context3)

@app.route('/321yed65twfqy3e2q"adm"3rdcyqfkie2e2hpe12/deletando-voucher/<int:id>/')# |PRONTO|
@login_required
def DelVouPage(id):
    useratual = current_user
    if useratual.adm == 1:
        obj = Voucher.query.get(id)
        #deleta foto, o arquivo dela
        if obj.foto: 
            os.unlink(os.path.join(r'app/static/img/fotos/',str(obj.foto)))

        db.session.delete(obj)
        db.session.commit()

        return redirect(url_for('CadVouPage'))
    else:
        return redirect(url_for('MenuPage'))
    
@app.route('/321yed65twfqy3e2q"adm"3rdcyqfkie2e2hpe12/deletando-voucher-compra/<int:id>/')# |PRONTO|
@login_required
def  DelVouPageCOMRPADO(id):
    useratual = current_user
    if useratual.adm == 1:
        obj = EstoqueVouch.query.get(id)
        #deleta foto, o arquivo dela

        db.session.delete(obj)
        db.session.commit()

        return redirect(url_for('CadVouPage'))
    else:
        return redirect(url_for('MenuPage'))
    


@app.route('/!@#$%Administração-De-Adm%$#@!/usuarios/', methods = ['GET', 'POST'])   # |INACABADO| Cadastro produto e mostra eles, cadastro vouchers, PRECISA deletar eles e bloquear Usuários?
@login_required 
def CadUsPage():
    useratual = current_user
    
    if useratual.adm == 1:

        dados = Usuario.query.order_by('id')
        context = {'dados' : dados.all()}

    else:
        print("Usuário nome: " ,useratual.usuario, " | Id: " ,useratual.id ," | Tentou acessar a administração sem permissão") 
        return redirect(url_for('HomePage'))
    
    return render_template('cadus.html', useratual = useratual, context=context)


@app.route('/!@#$%Administração-De-Adm%$#@!/vendas', methods = ['GET', 'POST'])   # |INACABADO| Cadastro produto e mostra eles, cadastro vouchers, PRECISA deletar eles e bloquear Usuários?
@login_required #e que seja de adm o login em. quero que em confirgs, se for adm ele possa entrar
def CadVendasPage():
    #if login epsecial == True permitir entrada
    useratual = current_user
    
    if useratual.adm == 1:

       
       
        dados = registro.query.order_by(desc('id'))
        context = {'dados' : dados.all()}

        dados2 = Usuario.query.order_by('id')
        context2 = {'dados2' : dados2.all()}

        dados3 = Itens.query.order_by('id')
        context3 = {'dados3' : dados3.all()} 

        return render_template('cadvendas.html', useratual = useratual, context=context, context2=context2, context3=context3)

        
       
    else:
        print("Usuário nome: " ,useratual.usuario, " | Id: " ,useratual.id ," | Tentou acessar a administração sem permissão") 
        return redirect(url_for('HomePage'))
    
   
@app.route('/!@#$%Administração-De-Adm%$#@!/vendas/<int:id>', methods=['GET','POST'])
@login_required
def DetalhesVendas():
    useratual = current_user
    
    if useratual.adm == 1:

        #Aqui era para ter detalhes da venda. Não eu não vou fazer não. Não tenho tempo
       
        dados = registro.query.order_by(desc('id'))
        context = {'dados' : dados.all()}

        dados2 = Usuario.query.order_by('id')
        context2 = {'dados2' : dados2.all()}

        dados3 = Itens.query.order_by('id')
        context3 = {'dados3' : dados3.all()} 

        return render_template('cadvendas.html', useratual = useratual, context=context, context2=context2, context3=context3)

        
       
    else:
        print("Usuário nome: " ,useratual.usuario, " | Id: " ,useratual.id ," | Tentou acessar a administração sem permissão") 
        return redirect(url_for('HomePage'))


#-- Configurações

@app.route('/home/configuracoes/') # |INACABADO| 
@login_required
def ConfigUser():
    useratual = current_user

    pega_endereco = Endereco.query.filter_by(id_usuario=useratual.id).first()
    
    pega_cartao = Pagamento.query.filter_by(id_usuario=useratual.id).first()


    return render_template('configs.html', useratual = useratual, pega_endereco=pega_endereco, pega_cartao=pega_cartao)

@app.route('/home/configuracoes/deletando-conta/')   #|INACABADO - PRONTO| deleta usuário, precisa apagar todas tabelas que tem o id do usuário
@login_required
def DelUser():
    useratual = current_user
    obj = Usuario.query.get(useratual.id)
    #aqui deveria buscar se o usuário tem endereço, cartão e carrinho, review e apagar eles também.
    try:
        db.session.delete(obj)
        db.session.commit()

        return redirect(url_for('CadProdPage'))
    except:
        print("Não foi possivel Deletar a conta")
    
    return render_template('configs.html', useratual=useratual)

@app.route('/troca-apelido/', methods=['GET', 'POST']) # |PRONTO| Troca Nome e aplica title()
@login_required
def trocapelido():
    useratual = current_user
    if request.method == 'POST':
        new_apelido = request.form.get('new_apelido')
        if useratual:
            useratual.usuario = new_apelido.title()
            db.session.commit()
            return redirect(url_for('HomePage'))
    return render_template('trocapelido.html', useratual=useratual)

@app.route('/troca-senha/', methods=['GET', 'POST']) # |INACABADO| Teoria: Pergunta senha velha e se souber pode ja trocar. Se não souber senha antiga troca com email
@login_required
def trocasenha():
    useratual = current_user
    if request.method == 'POST':
        new_password = request.form.get('new_pass')
        if useratual:
            useratual.senha = bcrypt.generate_password_hash(new_password)
            db.session.commit()
            return redirect(url_for('HomePage'))
        
    return render_template('trocasenha.html', useratual=useratual)

@app.route('/troca-email/', methods=['GET', 'POST']) # |INACABADO| Teoria: Pergunta email antigo
@login_required
def trocaemail():
    useratual = current_user
    if request.method == 'POST':
        new_email = request.form.get('new_email')
        if useratual:
            useratual.email = new_email.lower()
            db.session.commit()
            return redirect(url_for('HomePage'))
    return render_template('trocaemail.html', useratual=useratual)

@app.route('/home/configurações/gerenciando-pagamentos/ <int:id_cartao> /')   #| PRONTO| Deleta Enderaço Usuário, precisa testar se apaga só o cert
@login_required
def CheckPag(id_cartao):
    useratual = current_user

    obj = Pagamento.query.get(id_cartao)

    if obj != None:

        if obj.id_usuario == useratual.id:

            return render_template('checkpagamento.html', useratual = useratual, obj=obj)
        else:
            return redirect(url_for('HomePage'))
    else:
        return redirect(url_for('HomePage'))     
    
@app.route('/home/configurações/gerenciando-enderecos/ <int:id_endereco> /')   #| PRONTO| Deleta Enderaço Usuário, precisa testar se apaga só o cert
@login_required
def CheckEnd(id_endereco):
    useratual = current_user

    obj = Endereco.query.get(id_endereco)

    if obj != None:

        if obj.id_usuario == useratual.id:

            return render_template('checkendereco.html', useratual = useratual, obj=obj)
        else:
            return redirect(url_for('HomePage'))
    else:
        return redirect(url_for('HomePage'))   


@app.route('/home/configurações/deletando-endereco/')   #| PRONTO| Deleta Enderaço Usuário, precisa testar se apaga só o cert
@login_required
def DelEnd():
    useratual = current_user

    endereco_para_deletar = Endereco.query.filter_by(id_usuario=useratual.id).first()
    #ok... filtra aonde na tabela tem id_usuario = useratual.id e pega o primeiro
    try:
        db.session.delete(endereco_para_deletar)    #tomara que ele só deleta oque quer
        db.session.commit()

        return redirect(url_for('HomePage'))
    except:
        print("Não foi possivel Deletar o Endereço")
    
    return render_template('configs.html', useratual=useratual)

@app.route('/home/configurações/deletando-cartão-cadastrado/')  #|PRONTO| Deleta cartão do Usuário, Precisa testar se 
@login_required
def DelPag():
    useratual = current_user

    cartao_para_deletar = Pagamento.query.filter_by(id_usuario=useratual.id).first()
    #ok... filtra aonde na tabela tem id_usuario = useratual.id e pega o primeiro
    try:
        db.session.delete(cartao_para_deletar)    #tomara que ele só deleta oque quer
        db.session.commit()

        return redirect(url_for('HomePage'))
    except:
        print("Não foi possivel Deletar o Endereço")
    
    return render_template('configs.html', useratual=useratual)



#-- Adicionar novo endereco e cartão

@app.route('/addcep/', methods=['GET', 'POST']) # |INACABADO| adicionar try e except... EM TUDO AAAA
@login_required
def CepPage():
    useratual = current_user

    form = CepForm()

    if form.validate_on_submit():
        
        form.save(useratual.id)

    
        return redirect(url_for('HomePage'))
    
    return render_template('addcep.html', useratual=useratual, form=form)


@app.route('/addcartao/', methods=['GET', 'POST']) # |INACABADO| botar bycrypt em tudo literal tudo
@login_required
def CartaoPage():
    useratual = current_user
    form = CartaoForm()

    if form.validate_on_submit():
        form.save(useratual.id)

        return redirect(url_for('HomePage'))
    return render_template('addcartao.html', form=form, useratual=useratual)


@app.route('/review/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def ReviewPage(produto_id):
    useratual = current_user
    form = ReviewForm()
    item = Itens.query.get(produto_id) 

    if form.validate_on_submit():
        #AS FUNÇÕES DE AVALIAÇÃO ESTÃO DENTRO DO SAVE
        form.save(item.id, useratual.id)
        return redirect(url_for('DetalhesItemPage', id=produto_id)) 

    print(form.errors)  

    return render_template('criarcoment.html', form=form, useratual=useratual, item=item, produto_id=produto_id)


@app.route('/!@#$%Administração-De-Adm%$#@!/editar-item/<int:id>/', methods=['GET', 'POST'])
@login_required
def EditPage(id):
    useratual = current_user

    obj = Itens.query.get(id)
    form = EditItensForm()

    if form.validate_on_submit():
        obj.titulo = form.titulo.data
        obj.descricao = form.descricao.data
        obj.qntdestoque = form.qntdestoque.data
        obj.preco   = form.preco.data
        obj.especial = form.especial.data

        db.session.add(obj)
        db.session.commit()
        return redirect(url_for('CadProdPage'))

    return render_template('editaritem.html',  useratual = useratual, form=form, obj=obj)

@app.route('/pdfteste/')
def pdfteste():
    return render_template('pdf')


@app.route('/voucher-estoque/comprando-voucher/<int:idvoucher>/', methods=['GET','POST'])
@login_required
def ConfirmaVoucherPage(idvoucher):
    useratual = current_user
    form = VoucherForm()

    erro_mensagem = None

    cid = idvoucher

    obj = Voucher.query.get(id)

    if form.validate_on_submit():
        form.save(cid, useratual.id)
        db.session.commit()
        obj2 = Carrinho.query.get(cid)
        db.session.delete(obj2) 
        db.session.commit()
        return redirect(url_for('HomePage'))

    return render_template('comprando.html', useratual = useratual,bj=obj, form=form, erro_mensagem=erro_mensagem)

@app.route('/teste/')
def background():
    useratual = current_user  
    return render_template('teste.html', useratual=useratual)



