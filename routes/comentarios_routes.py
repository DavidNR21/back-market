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
        usuario_id = data.get('usuario_id')
        content = data.get('content')
        type_comentario = data.get('type')
        midia = data.get('midia', None) 
        comentario_pai_id_str = data.get('comentario_pai_id')
        
        if not all([post_id, usuario_id, content, type_comentario]):
            return jsonify({"error": "post_id, usuario_id, content e type são obrigatórios."}), 400

        try:
            post_obj = Post.get(Post.id == post_id)
            usuario_obj = Usuarios.get(Usuarios.id == usuario_id)
        except DoesNotExist:
            return jsonify({"error": "Erro ao buscar post ou usuário"}), 404
        except Exception as e:
            return jsonify({"error": f"Erro inesperado na busca: {str(e)}"}), 500

        comentario_pai_uuid = None
        is_reply = False
        action_message = "Comentário criado com sucesso."
        
        if comentario_pai_id_str:
            is_reply = True
            try:
                comentario_pai_uuid = uuid.UUID(comentario_pai_id_str)
                action_message = "Resposta (sub-comentário) criada com sucesso."
                
            except ValueError:
                return jsonify({"error": "Formato de comentario_pai_id inválido."}), 400


        novo_comentario = Comentarios.create(
            content = content,
            midia = midia,
            likes = 0,
            type = type_comentario,
            usuario = usuario_obj,
            post = post_obj,
            comentario_pai = comentario_pai_uuid
        )

        nova_qtd = post_obj.comentarios_count if post_obj.comentarios_count is not None else 0
        
        if not is_reply:
            nova_qtd += 1

            Post.update(comentarios_count=nova_qtd).where(Post.id == post_id).execute()

            post_obj.comentarios_count = nova_qtd
        else:
            nova_qtd = post_obj.comentarios_count if post_obj.comentarios_count is not None else 0


        response = {
            "message": action_message,
            "comentario_id": str(novo_comentario.id),
            "comentario_pai_id": comentario_pai_id_str,
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


@comentarios_bp.route('/deletar', methods=['DELETE']) # verificado
def deletarComentario():
    try:
        data = request.get_json()
        comentario_id_str = data['comentarioId']
        
        try:
            comentario_id = uuid.UUID(comentario_id_str)
        except ValueError:
            return jsonify({"error": "Formato de ID inválido"}), 400

        try:
            comentario = Comentarios.get(Comentarios.id == comentario_id)
            post = comentario.post
        except DoesNotExist:
            return jsonify({"error": f"Comentário com ID: {comentario_id_str} não encontrado."}), 404
        
        is_top_level_comment = comentario.comentario_pai is None 
        
        Comentarios.delete().where(Comentarios.comentario_pai == comentario_id).execute()
        
        comentario.delete_instance()
        
        if is_top_level_comment:
            Post.update(comentarios_count=fn.GREATEST(0, Post.comentarios_count - 1)).where(Post.id == post.id).execute()
            
        response = {
            "message": "Comentário e todas as suas respostas deletados com sucesso.",
            "comentario_id": str(comentario_id),
            "is_top_level": is_top_level_comment
        }

        return jsonify(response), 200

    except Exception as e:
        error_message = {"error": f"Erro interno no servidor: {str(e)}"}  
        return jsonify(error_message), 500

