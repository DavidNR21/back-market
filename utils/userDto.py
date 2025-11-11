

def serialize_usuario(user_object):
    """
    Converte manualmente um objeto Peewee 'Usuarios' em um 
    dicionário Python seguro para ser enviado como JSON.
    """


    user_dict = {
        # --- Dados Principais ---
        "id": str(user_object.id),
        "active": user_object.active,
        "nome": user_object.nome,
        "sobrenome": user_object.sobrenome,
        "username": user_object.username,
        "email": user_object.email,
        
        # --- Dados de Perfil ---
        "nascimento": "",
        "cidade_Natal": user_object.cidade_Natal,
        "banner": user_object.banner,
        "foto": user_object.foto,
        "bio": user_object.bio,
        
        # --- Dados de Controle ---
        "isVerified": user_object.isVerified,
        "role": user_object.role,
        "isPrivate": user_object.isPrivate,
        "blocos": user_object.blocos
    }
    
    return user_dict

