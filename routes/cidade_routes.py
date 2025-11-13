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
            prefeito = "---------------",
            vereadores = "-------------",
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
        return jsonify(error_message), 500
    

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
        return jsonify(error_message), 500


@city_bp.route('/any/<string:username>', methods=['GET']) # verificado
def readAnyCidade(username):
    try:
        c = Cidades.select().where(Cidades.username == username).get()

        city_dict = model_to_dict(c)

        
        response = {
            "data": city_dict
        }

        return jsonify(response), 200

    except Cidades.DoesNotExist:
        return jsonify({"error": "Cidade não encontrada"}), 404
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


###############################################################################

@city_bp.route('/busca/', methods=['GET']) # verificado
def buscarCity():
    try:
        filter_field = request.args.get('filter', type=str)

        if filter_field is not None:
            query_contain = Cidades.select()

            column = filter_field.split('_')[0]
            param = filter_field.split('_')[1]

            search_field_attr = getattr(Cidades, column)

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


@city_bp.route('/seguir', methods=['POST']) # verificado
def seguirCity():
    try:
        data = request.get_json()

        if 'seguidor_id' not in data or 'cidade_username' not in data:
            return jsonify({"error": "Faltando seguidor_id ou cidade_username"}), 400

        seguidor_id_json = data['seguidor_id']
        cidade_username = data['cidade_username']

        try:
            # .get() é um atalho para .select().where(...).get()
            cidade_seguida = Cidades.get(Cidades.username == cidade_username)
        except Cidades.DoesNotExist:
            return jsonify({"error": "Cidade a ser seguida não encontrada"}), 404

        
        ja_segue = CidadesSeguidas.select().where((CidadesSeguidas.seguidor == seguidor_id_json) & (CidadesSeguidas.cidade_seguida == cidade_seguida)).exists()


        if ja_segue:
            query = CidadesSeguidas.delete().where((CidadesSeguidas.seguidor == seguidor_id_json) & (CidadesSeguidas.cidade_seguida == cidade_seguida))

            query.execute() 

            return jsonify({"message": "Deixou de seguir com sucesso"}), 200

        # 3. Se não existe, cria o relacionamento
        CidadesSeguidas.create(
            seguidor = seguidor_id_json,
            cidade_seguida = cidade_seguida
        )
        
        response = {
            "message": "Seguindo com sucesso!"
        }

        return jsonify(response), 201

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500

