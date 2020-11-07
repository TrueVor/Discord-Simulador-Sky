import psycopg2
from core.embed import embedding # pylint: disable=import-error

async def iniciando(self, ctx):
    # ID, nome, Velas, Velas Eden, Total Luzes, Nível, Var. Farmando e Var. Farmando_Tempo
    self.db_cursor.execute('INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
    (ctx.author.id, ctx.author.name, 0.0, 0.0, 0, 0, 0, 0,))
    # ID, Farmar, Luzes, Eden, Iniciar e Reiniciar
    self.db_cursor.execute('INSERT INTO cooldown VALUES (%s,%s,%s,%s,%s,%s)',
    (ctx.author.id, 0, 0, 0, 0, 0,))
    # ID, Ilha, Campina, Floresta, Vale, Sertão e Relicário
    self.db_cursor.execute('INSERT INTO luzes VALUES (%s,%s,%s,%s,%s,%s,%s)',
    (ctx.author.id, 0, 0, 0, 0, 0, 0,))
    # ID, Ilha, Campina, Floresta, Vale, Sertão e Relicário
    self.db_cursor.execute('INSERT INTO farm VALUES (%s, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)',
    (ctx.author.id,))
    self.db.commit()
    titulo = '**Uma Criança da Luz Nasce**'
    conteudo = f'*Uma criança da luz acaba de nascer*\nBem vindo(a) **{ctx.author.name}**!'
    imagem = 'https://s3.amazonaws.com/sensortower-itunes/blog/2019/07/sky-children-of-the-light.jpg'
    embed = await embedding(ctx.message.author, titulo, conteudo, '', ctx.message.author.avatar_url, imagem)
    embed.set_author(name='', icon_url='')
    await ctx.send(embed=embed)

async def checando_usuario(users, user):
    if not f'{user.id}' in users:
        return False
    return True

async def checando_db(self, ctx, db='users'):
    self.db_cursor.execute('SELECT * FROM {} WHERE id=%s'.format(db), (str(ctx.message.author.id),))
    response = self.db_cursor.fetchone()
    if not response:
        return False
    return True