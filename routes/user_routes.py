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
            'active', 'nome', 'sobrenome', 'username', 'email', 'senha',
            'nascimento', 'cidade_Natal', 'isVerified', 'token', 'role',
            'isPrivate', 'banner', 'foto', 'bio', 'blocos'
        ]

        erros = []
        for field in required_fields:
            if field not in data:
                erros.append(f'Campo {field} ausente!')
        
        if erros:
            return jsonify({'error': 'Campos ausentes', 'details': erros}), 400
        
        b = {}
        
        
        novo_usuario = Usuarios.create(
            # Dados principais
            active = data['active'],
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

        #user = Usuarios.get_by_id(id)

        #user_dict = model_to_dict(user)


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


@user_bp.route('/any/<string:id>', methods=['GET']) # verificado
def readAnyUser(id):
    try:
        u = Usuarios.get_by_id(id)


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


