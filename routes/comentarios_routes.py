from flask import Blueprint, request, jsonify
from models.models import *
import json
import peewee
from playhouse.shortcuts import model_to_dict


comentarios_bp = Blueprint('comentarios',__name__)



@comentarios_bp.route('/<string:postId>', methods=['GET']) # verificado
def getPostComent(postId):
    try:
        # Busca os comentários
        query_completa = Comentarios.select().where(Comentarios.post == postId)

        lista_comentarios = []
        
        for comentario in query_completa:
            c_dict = model_to_dict(comentario)
            
            c_dict['id'] = str(c_dict['id'])
            c_dict['post'] = str(c_dict['post'])
            c_dict['usuario']['id'] = str(c_dict['usuario']['id'])
            c_dict['criadoEm'] = str(c_dict['criadoEm'])

            lista_comentarios.append(c_dict)

        response = {
            "data": lista_comentarios
        }

        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": str(e)}
        return jsonify(error_message), 400


@comentarios_bp.route('/add', methods=['POST']) # verificado
def criarComentario():
    try:
        data = request.get_json()
        
        post_id = data.get('post_id')

        try:
            post_obj = Post.get(Post.id == post_id)
            usuario_obj = Usuarios.get(Usuarios.id == data['usuario_id'])
        except Exception as e:
            return jsonify({"error": "Erro ao buscar post ou usuário"}), 404

        # 1. Cria o comentário
        novo_comentario = Comentarios.create(
            content = data['content'],
            midia = data.get('midia', ''),
            likes = 0,
            type = data['type'],
            usuario = usuario_obj,
            post = post_obj
        )

        
        qtd_atual = post_obj.comentarios if post_obj.comentarios is not None else 0
        
        
        nova_qtd = qtd_atual + 1

        
        Post.update(comentarios=nova_qtd).where(Post.id == post_id).execute()

        
        post_obj.comentarios = nova_qtd 

        response = {
            "message": "Comentário criado com sucesso",
            "comentario_id": str(novo_comentario.id),
            "total_comentarios_post": nova_qtd 
        }

        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@comentarios_bp.route('/like', methods=['POST']) # verificado
def likeComentario():
    try:
        data = request.get_json()
        comentario_id = data['comentarioId']
        user_id = data['userId']

        if not comentario_id or not user_id:
            return jsonify({"error": "comentarioId e userId são obrigatórios"}), 400

        try:
            comentario = Comentarios.get(Comentarios.id == comentario_id)
        except Comentarios.DoesNotExist:
            return jsonify({"error": f"Comentário com ID: {comentario_id} não encontrado."}), 404


        try:
            usuario = Usuarios.get(Usuarios.id == user_id)
        except Usuarios.DoesNotExist:
            return jsonify({"error": f"Usuário com ID: {user_id} não encontrado."}), 404

        like_existente = LikesComentarios.get_or_none(
            (LikesComentarios.comentario == comentario) & (LikesComentarios.usuario == usuario)
        )

        action_message = ""

        if like_existente:
            like_existente.delete_instance()
            
            if comentario.likes and comentario.likes > 0:
                comentario.likes -= 1
            else:
                comentario.likes = 0
            
            action_message = "Like no comentário removido com sucesso."

        else:
            LikesComentarios.create(comentario=comentario, usuario=usuario)
            
            if comentario.likes:
                comentario.likes += 1
            else:
                comentario.likes = 1
            
            action_message = "Like no comentário adicionado com sucesso."

        
        comentario.save()

        response = {
            "message": action_message,
            "comentario_id": str(comentario.id),
            "total_likes": comentario.likes
        }

        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": f"Erro interno no servidor: {str(e)}"}  
        return jsonify(error_message), 500