from flask import Blueprint, request, jsonify
from models.models import *
import json
import peewee
from playhouse.shortcuts import model_to_dict


post_bp = Blueprint('posts',__name__)


@post_bp.route('/me/<string:username>', methods=['GET'])
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


@post_bp.route('/add', methods=['POST']) # verificado
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


@post_bp.route('/update/<string:id>', methods=['PUT']) #verificado
def updatePost(id):
    try:
        data = request.get_json()

        query = Post.update(**data).where(Post.id == id)

        query.execute()


        response = {
            "message": f"Post com ID: {id} foi atualizado com sucesso.",
        }

        return jsonify(response), 200

    except Post.DoesNotExist:
        error_message = {"error": f"Post com ID: {id} não encontrado."}
        return jsonify(error_message), 404

    except Exception as e:
        error_message = {"error": str(e)}
        print("Erro:", e)
        return jsonify(error_message), 500


@post_bp.route('/like', methods=['POST']) # verificado
def likePost():
    try:
        data = request.get_json()
        post_id = data['postId']
        user_id = data['userId']

        # Validação básica da entrada
        if not post_id or not user_id:
            return jsonify({"error": "postId e userId são obrigatórios"}), 400

        try:
            post = Post.get(Post.id == post_id)
        except Post.DoesNotExist:
            return jsonify({"error": f"Post com ID: {post_id} não encontrado."}), 404

        try:
            usuario = Usuarios.get(Usuarios.id == user_id)
        except Usuarios.DoesNotExist:
            return jsonify({"error": f"Usuário com ID: {user_id} não encontrado."}), 404

        like_existente = PostLikes.get_or_none(
            (PostLikes.post == post) & (PostLikes.usuario == usuario)
        )

        action_message = ""

        if like_existente:
            like_existente.delete_instance()
            
            if post.likes and post.likes > 0:
                post.likes -= 1
            else:
                post.likes = 0 
            
            action_message = "Like removido com sucesso."

        else:
            PostLikes.create(post=post, usuario=usuario)
            
            if post.likes:
                post.likes += 1
            else:
                post.likes = 1
            
            action_message = "Like adicionado com sucesso."

        post.save()

        response = {
            "message": action_message,
            "post_id": str(post.id), 
            "total_likes": post.likes
        }

        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": f"Erro interno no servidor: {str(e)}"}  
        return jsonify(error_message), 500



@post_bp.route('/share', methods=['POST']) # verificado
def sharePost():
    try:
        data = request.get_json()
        post_id = data['postId']

        if not post_id:
            return jsonify({"error": "postId é obrigatório"}), 400

        try:
            post = Post.get(Post.id == post_id)
        except Post.DoesNotExist:
            return jsonify({"error": f"Post com ID: {post_id} não encontrado."}), 404

        if post.share:
            post.share += 1
        else:
            post.share = 1

        post.save()

        response = {
            "message": "Post compartilhado com sucesso.",
            "post_id": str(post.id),
            "total_shares": post.share
        }
        
        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": f"Erro interno no servidor: {str(e)}"}
        print("Erro:", e)
        return jsonify(error_message), 500


@post_bp.route('/<string:post_id>', methods=['GET']) # verificado
def getPostGeral(post_id):
    try:
        
        query_update = Post.update(
            views=peewee.fn.COALESCE(Post.views, 0) + 1
        ).where(
            Post.id == post_id
        )
        
        rows_affected = query_update.execute()

        try:
            postAtualizado = Post.select().where((Post.active == True) & (Post.id == post_id)).get()

            post_dict = model_to_dict(postAtualizado)

            response = {
                "data" : post_dict
            }
            return jsonify(response), 200

        except Post.DoesNotExist:
            return jsonify({"error": f"Post com ID: {post_id} não encontrado ou está inativo."}), 404

    except Exception as e:
        error_message = {"error": f"Erro interno no servidor: {str(e)}"}
        print("Erro:", e)
        return jsonify(error_message), 500
    
