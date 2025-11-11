from flask import Blueprint, request, jsonify
from models.models import *
import json
from playhouse.shortcuts import model_to_dict


city_bp = Blueprint('cidades',__name__)


@city_bp.route('/', methods=['GET']) # verificado
def getCidades():

    try:
        users = Cidades.select().limit(20)

        user_dict = [model_to_dict(u) for u in users]

        return jsonify(user_dict), 200

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400



@city_bp.route('/add', methods=['POST']) # verificado
def criarCidades():
    try:
        data = request.get_json()

        required_fields = [
            'nome', 'membros', 'status',
            'limite', 'logo', 'banner', 'bio', 'url', 'username'
        ]

        erros = []
        for field in required_fields:
            if field not in data:
                erros.append(f'Campo {field} ausente!')
        
        if erros:
            return jsonify({'error': 'Campos ausentes', 'details': erros}), 400
        
        # sufixo estado
        nomeCompleto = str(data['nome'])
        separacao = nomeCompleto.split('-')
        sufixo = separacao[1]
        
        sufixo = sufixo.upper()

        nova_cidade = Cidades.create(
            active = True,
            nome = data['nome'],
            sufixo = sufixo,
            membros = data['membros'],
            status = data['status'],
            username = data['username'],
            limite = data['limite'],
            logo = data['logo'],
            banner = data['banner'],
            bio = data['bio'],
            url = data['url']
        )

        print(request.headers)

        
        response = {
            "message": "Cidade criada com sucesso",
            "cidade_id": str(nova_cidade.id)
        }


        return jsonify(response), 201

    except KeyError as e:
        return jsonify({'error': f'Estrutura do JSON inválida, campo faltando: {str(e)}'}), 400
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400
    

@city_bp.route('/<string:id>', methods=['GET']) # verificado
def readCidade(id):
    try:
        c = Cidades.select().where((Cidades.active == True) & (Cidades.id == id)).get()

        cidade_dict = model_to_dict(c)

        
        response = {
            "data": cidade_dict
        }

        return jsonify(response), 200

    except Cidades.DoesNotExist:
        return jsonify({"error": "Cidade não encontrada"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


@city_bp.route('/update/<string:id>', methods=['PUT']) # verificado
def updateCidade(id):
    try:
        data = request.get_json()

        query = Cidades.update(**data).where(Cidades.id == id)

        query.execute()


        response = {
            "message": f"Cidade com ID: {id} foi atualizada com sucesso.",
        }

        return jsonify(response), 200

    except Cidades.DoesNotExist:
        error_message = {"error": f"Cidade com ID: {id} não encontrada."}
        return jsonify(error_message), 404

    except Exception as e:
        error_message = {"error": str(e)}
        print("Erro:", e)
        return jsonify(error_message), 400


@city_bp.route('/update/active/<string:id>', methods=['PUT']) # verificado
def update_active_cidade(id):
    try:
        data = request.get_json()

        active = data['active']

        print(type(active))

        if active == 'true':
            query = Cidades.update(active=True).where(Cidades.id == id)

            query.execute()


        else:
            query = Cidades.update(active=False).where(Cidades.id == id)

            query.execute()


        response = {
            "message": f"Cidade com ID: {id} foi atualizada com sucesso.",
        }

        return jsonify(response), 200

    except Cidades.DoesNotExist:
        error_message = {"error": f"Cidade com ID: {id} não encontrada."}
        return jsonify(error_message), 404

    except Exception as e:
        error_message = {"error": str(e)}
        print("Erro:", e)
        return jsonify(error_message), 400


@city_bp.route('/any/<string:id>', methods=['GET']) # verificado
def readAnyUser(id):
    try:
        c = Cidades.get_by_id(id)

        user_dict = model_to_dict(c)

        
        response = {
            "data": user_dict
        }

        return jsonify(response), 200

    except Cidades.DoesNotExist:
        return jsonify({"error": "Cidade não encontrada"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


