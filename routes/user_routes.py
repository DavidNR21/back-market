from flask import Blueprint, request, jsonify
from models.models import *
import json
from playhouse.shortcuts import model_to_dict
from utils.userDto import serialize_usuario


user_bp = Blueprint('users',__name__)


@user_bp.route('/', methods=['GET']) # verificado
def getUsers():

    try:
        users = Usuarios.select().limit(20)

        user_dict = [model_to_dict(u) for u in users]

        return jsonify(user_dict), 200

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400



@user_bp.route('/add', methods=['POST'])
def criarUser():
    try:
        data = request.get_json()

        required_fields = [
            'nome', 'sobrenome', 'username', 'email', 'senha',
            'nascimento', 'cidade_Natal', 'isVerified', 'token', 'role',
            'isPrivate', 'banner', 'foto', 'bio'
        ]

        erros = []
        for field in required_fields:
            if field not in data:
                erros.append(f'Campo {field} ausente!')
        
        if erros:
            return jsonify({'error': 'Campos ausentes', 'details': erros}), 400
        
        b = {}

        query_username = Seguidores.select().where(Usuarios.username == data['username']).exists()
        
        if query_username:
            return jsonify({'message': 'Username já usado', 'type' : "conflict"}), 200
        
        
        novo_usuario = Usuarios.create(
            # Dados principais
            active = True,
            nome = data['nome'],
            sobrenome = data['sobrenome'],
            username = data['username'],
            email = data['email'],
            senha = data['senha'],
            
            # Dados de perfil
            nascimento = data['nascimento'],
            cidade_Natal = data['cidade_Natal'],
            banner = data['banner'],
            foto = data['foto'],
            bio = data['bio'],
            
            # Dados de controle
            isVerified = data['isVerified'],
            token = data['token'],
            role = data['role'],
            isPrivate = data['isPrivate'],
            blocos = b,
            
            ipAddress = request.remote_addr
        )

        print(request.headers)

        response = {
            "message": "Usuário criado com sucesso",
            "user_id": str(novo_usuario.id) 
        }

        # 201 Created é o status HTTP correto
        return jsonify(response), 201

    except KeyError as e:
        return jsonify({'error': f'Estrutura do JSON inválida, campo faltando: {str(e)}'}), 400
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400
    

@user_bp.route('/<string:id>', methods=['GET']) # verificado
def readUser(id):
    try:
        u = Usuarios.select().where((Usuarios.active == True) & (Usuarios.id == id)).get()


        user_dict = serialize_usuario(u)


        user_dict['id'] = str(user_dict['id'])
        if user_dict['nascimento']:
            user_dict['nascimento'] = user_dict['nascimento'].isoformat()

        # Checagem de status
        if user_dict['active'] == False:
            return jsonify({'message': 'Usuário não está disponível'}), 404
        
        response = {
            "data": user_dict
        }

        return jsonify(response), 200

    except Usuarios.DoesNotExist:
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400
    

@user_bp.route('/update/<string:id>', methods=['PUT']) # verificado
def updateUser(id):
    try:
        data = request.get_json()

        query = Usuarios.update(**data).where(Usuarios.id == id)

        query.execute()


        response = {
            "message": f"Usuário com ID: {id} foi atualizado com sucesso.",
        }

        return jsonify(response), 200

    except Usuarios.DoesNotExist:
        error_message = {"error": f"Usuário com ID: {id} não encontrado."}
        return jsonify(error_message), 404

    except Exception as e:
        error_message = {"error": str(e)}
        print("Erro:", e)
        return jsonify(error_message), 400


@user_bp.route('/update/active/<string:id>', methods=['PUT']) # verificado
def update_active_User(id):
    try:
        data = request.get_json()

        active = data['active']

        if active == 'true':
            query = Usuarios.update(active=True).where(Usuarios.id == id)

            query.execute()


        else:
            query = Usuarios.update(active=False).where(Usuarios.id == id)

            query.execute()


        response = {
            "message": f"Usuário com ID: {id} foi atualizado com sucesso.",
        }

        return jsonify(response), 200

    except Usuarios.DoesNotExist:
        error_message = {"error": f"Usuário com ID: {id} não encontrado."}
        return jsonify(error_message), 404

    except Exception as e:
        error_message = {"error": str(e)}
        print("Erro:", e)
        return jsonify(error_message), 400


@user_bp.route('/any/<string:username>', methods=['GET']) # verificado
def readAnyUser(username):
    try:
        u = Usuarios.select().where(Usuarios.username == username).get()

        user_dict = serialize_usuario(u)

        user_dict['id'] = str(user_dict['id'])
        if user_dict['nascimento']:
            user_dict['nascimento'] = user_dict['nascimento'].isoformat()

        
        response = {
            "data": user_dict
        }

        return jsonify(response), 200

    except Usuarios.DoesNotExist:
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


############################################################################

@user_bp.route('/busca/', methods=['GET']) # verificado
def buscarUser():
    try:
        filter_field = request.args.get('filter', type=str)

        if filter_field is not None:
            query_contain = Usuarios.select()

            column = filter_field.split('_')[0]
            param = filter_field.split('_')[1]

            search_field_attr = getattr(Usuarios, column)

            print(column, param)
    
            user_contain = query_contain.where(search_field_attr.contains(param))

            usuario_contain_dict = [model_to_dict(f) for f in user_contain]

            response = {
                "data" : usuario_contain_dict
            }

            return jsonify(response), 200
        
        response = {
            "data" : []
        }

        return jsonify(response), 200


    except Usuarios.DoesNotExist:
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


@user_bp.route('/seguir', methods=['POST']) # verificado
def seguirUser():
    try:
        data = request.get_json()

        if 'seguidor_id' not in data or 'seguido_username' not in data:
            return jsonify({"error": "Faltando seguidor_id ou seguido_username"}), 400

        seguidor_id_json = data['seguidor_id']
        seguido_username = data['seguido_username']

        try:
            # .get() é um atalho para .select().where(...).get()
            usuario_seguido = Usuarios.get(Usuarios.username == seguido_username)
        except Usuarios.DoesNotExist:
            return jsonify({"error": "Usuário a ser seguido não encontrado"}), 404

        
        ja_segue = Seguidores.select().where((Seguidores.seguidor == seguidor_id_json) & (Seguidores.seguido == usuario_seguido)).exists()


        if ja_segue:
            query = Seguidores.delete().where((Seguidores.seguidor == seguidor_id_json) & (Seguidores.seguido == usuario_seguido))

            query.execute() 

            return jsonify({"message": "Deixou de seguir com sucesso"}), 200

        # 3. Se não existe, cria o relacionamento
        Seguidores.create(
            seguidor = seguidor_id_json,
            seguido = usuario_seguido
        )
        
        response = {
            "message": "Seguindo com sucesso!"
        }

        return jsonify(response), 201

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


@user_bp.route('/geral/<string:username>', methods=['GET']) # verificado
def readUserGeral(username):
    try:
        u = Usuarios.select().where((Usuarios.active == True) & (Usuarios.username == username)).get()


        user_dict = serialize_usuario(u)


        user_dict['id'] = str(user_dict['id'])
        if user_dict['nascimento']:
            user_dict['nascimento'] = user_dict['nascimento'].isoformat()

        # Checagem de status
        if user_dict['active'] == False:
            return jsonify({'message': 'Usuário não está disponível'}), 404
        
        response = {
            "data": user_dict
        }

        return jsonify(response), 200

    except Usuarios.DoesNotExist:
        return jsonify({"error": "Usuário não encontrado"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500

