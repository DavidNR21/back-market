from peewee import *
import uuid


db = PostgresqlDatabase('market',port=5432,user='postgres',password='123456')
# coloque seu database já criado, user e senha

class BaseModel(Model):
    class Meta:
        database = db



class Usuarios(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()
    nome = TextField()
    sobrenome = TextField()
    username = TextField()
    email = TextField()
    senha = TextField()
    nascimento = DateField()
    cidade_Natal = TextField()
    isVerified = BooleanField()
    token = TextField()
    role = TextField()
    isPrivate = BooleanField()
    banner = TextField()
    foto = TextField()
    bio = TextField()
    blocos = TextField()
    ipAddress = TextField()
    criadoEm = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Cidades(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()
    nome = TextField()
    sufixo = TextField()
    username = TextField()
    membros = IntegerField()
    status = TextField()
    limite = IntegerField()
    logo = TextField()
    banner = TextField()
    bio = TextField()
    prefeito = TextField()
    vereadores = TextField()
    url = TextField()
    criadoEm = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Seguidores(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    seguidor = ForeignKeyField(Usuarios, backref='seguidores', on_delete='CASCADE')
    seguido = ForeignKeyField(Usuarios, backref='seguidores', on_delete='CASCADE')
    criadoEm = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    # usuario A (quer seguir o B)--> A = seguidor e B = seguido / se for o contrario é so inverter


class CidadesSeguidas(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    seguidor = ForeignKeyField(Usuarios, backref='cidadesseguidas', on_delete='CASCADE')
    cidade_seguida = ForeignKeyField(Cidades, backref='cidadesseguidas', on_delete='CASCADE')
    criadoEm = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Post(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    active = BooleanField()
    content = TextField()
    midia = TextField()
    likes = IntegerField()
    comentarios = IntegerField()
    share = IntegerField()
    views = IntegerField()
    tag = TextField()
    isVisible = BooleanField()
    roles = TextField()
    link = TextField()
    usuario = ForeignKeyField(Usuarios, backref='post', on_delete='CASCADE')
    cidade = ForeignKeyField(Cidades, backref='post', on_delete='CASCADE', null=True)
    

class PostLikes(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    usuario = ForeignKeyField(Usuarios, backref='post_like', on_delete='CASCADE')
    post = ForeignKeyField(Post, backref='post_like', on_delete='CASCADE')
    criadoEm = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])



db.create_tables([Usuarios, Cidades, Seguidores, CidadesSeguidas, Post, PostLikes])
