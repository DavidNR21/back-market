from flask import Blueprint, request, jsonify
from models.models import *
import json
from playhouse.shortcuts import model_to_dict


post_bp = Blueprint('posts',__name__)


@post_bp.route('/<string:username>', methods=['GET'])
def getPost(username):
    try:
        query_completa = (Post.select().join(Usuarios).where(Usuarios.username == username))

        posts_dict = [model_to_dict(post) for post in query_completa]

        contagem_de_posts = len(posts_dict)

        print(posts_dict[0]['usuario'])

        response = {
            "count": contagem_de_posts,
            "data": posts_dict 
        }

        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


@post_bp.route('/add', methods=['POST'])
def criarPost():
    try:
        data = request.get_json()

        # 1. 'cidade_id' foi REMOVIDO dos campos obrigatórios
        required_fields = [
            'content',
            'midia',
            'tag',
            'isVisible',
            'roles',
            'link',
            'usuario_id'
        ]

        erros = []
        for field in required_fields:
            if field not in data:
                erros.append(f'Campo {field} ausente!')
        
        if erros:
            return jsonify({'error': 'Campos ausentes', 'details': erros}), 400
        

        cidade_final = None
        
        cidade_id_raw = data.get('cidade_id') 

        if cidade_id_raw:
            try:
                # Verificamos se a cidade realmente existe
                cidade_obj = Cidades.get_by_id(cidade_id_raw)
                cidade_final = cidade_obj
            except Cidades.DoesNotExist:
                return jsonify({'error': f'A cidade com ID {cidade_id_raw} não foi encontrada.'}), 404
        

        novo_post = Post.create(
            active = True,
            content = data['content'],
            midia = data['midia'],
            likes = 0,
            comentarios = 0,
            share = 0,
            views = 0,
            tag = data['tag'],
            isVisible = data['isVisible'],
            roles = data['roles'],
            link = data['link'],
            usuario = data['usuario_id'],
            cidade = cidade_final
        )

        print(request.headers)
        
        # 5. Resposta de sucesso
        response = {
            "message": "Post criado com sucesso",
            "post_id": str(novo_post.id)
        }

        return jsonify(response), 201

    except KeyError as e:
        return jsonify({'error': f'Estrutura do JSON inválida, campo faltando: {str(e)}'}), 400
    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


