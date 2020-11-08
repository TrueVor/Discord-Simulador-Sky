import discord
import json
import asyncio
import asyncpg
import time
import random
import schedule
import psycopg2
import psycopg2.extras
import os
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from core.iniciar import checando_db, iniciando # pylint: disable=import-error
from core.embed import embedding, embed_menu # pylint: disable=import-error
from core.functions import eq_vel # pylint: disable=import-error

tempo_farm = [0, 1800, 5100, 3100, 3500, 3200, 2700]
ceras_farm = [0, 0.14, 4.33, 3.73, 3.85, 4.25, 0.89]
luzes_reinos = [0, 8, 21, 16, 11, 16, 8]
exp_nivel = [0, 1, 2, 5, 10, 20, 35, 55, 75, 100, 120, 150]
nomes_mapas = ['', 'Ilha', 'Campina', 'Floresta', 'Vale', 'Sertão', 'Relicário']
id_mapas = ['', 'ilha', 'campina', 'floresta', 'vale', 'sertao', 'relicario']
canal_updates = 774012109511852034

class Sky(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.update_sky.add_exception_type(asyncpg.PostgresConnectionError) # pylint: disable=no-member
        self.update_sky.start()
        self.schedules.add_exception_type(asyncpg.PostgresConnectionError)
        self.schedules.start()
        # DATABASE_URL = postgres://<username>:<password>@<host>/<dbname>
        # if os.environ.get('DATABASE_URL') != None: # 
        data = os.environ['DATABASE_URL']
        self.db = psycopg2.connect(data, sslmode='require')
        self.db_cursor = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            velas float NOT NULL,
            velas_eden float NOT NULL,
            total_luzes smallint NOT NULL,
            nivel smallint NOT NULL,
            farmando smallint NOT NULL,
            farmando_tempo int NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cooldown (
            id TEXT PRIMARY KEY,
            farmar int NOT NULL,
            luzes int NOT NULL,
            eden int NOT NULL,
            iniciar int NOT NULL,
            reiniciar int NOT NULL
        );
        CREATE TABLE IF NOT EXISTS luzes (
            id TEXT PRIMARY KEY,
            ilha smallint NOT NULL,
            campina smallint NOT NULL,
            floresta smallint NOT NULL,
            vale smallint NOT NULL,
            sertao smallint NOT NULL,
            relicario smallint NOT NULL
        );
        """)
        self.db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS farm (
            id TEXT PRIMARY KEY,
            ilha BOOLEAN NOT NULL,
            campina BOOLEAN NOT NULL,
            floresta BOOLEAN NOT NULL,
            vale BOOLEAN NOT NULL,
            sertao BOOLEAN NOT NULL,
            relicario BOOLEAN NOT NULL
        );
        """)
        self.db.commit()

    def cog_unload(self):
        self.update_sky.cancel()
        self.schedules.cancel()

    # Eventos
    @commands.Cog.listener()
    async def on_ready(self):
        #job(self)
        #channel = self.client.get_channel(canal_updates)
        #await channel.send('Crianças da luz, **Todas as ceras foram resetadas.** Tenham um ótimo farm!')
        schedule.every().day.at("05:00").do(job, self)
        print('Bot Pronto no Cog Sky')

    # Comandos
    @commands.command()
    async def iniciar(self, ctx):
        
        checa = await checando_db(self, ctx)

        if checa == False:
            await iniciando(self, ctx)
        else:
            embed = await embedding(ctx.message.author, 'Comando Iniciar', f'**{ctx.message.author.name}**, você só pode iniciar uma vez')
            await ctx.send(embed=embed)

    @commands.command()
    async def deletar(self, ctx):
        await ctx.message.delete()       
        checa = await checando_db(self, ctx)
        if checa == False:
            await ctx.send(f'{ctx.message.author.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return
        
        self.db_cursor.execute('SELECT * FROM cooldown WHERE id=%s', (str(ctx.message.author.id),))
        cd = self.db_cursor.fetchone()
        epoch = round(time.time())
        if(epoch < cd['reiniciar']):
            restante = cd['reiniciar'] - epoch
            await ctx.send(f'{ctx.message.author.mention}, você só pode usar o comando `?` novamente daqui {display_time(restante)}')
            return
        self.db_cursor.execute('UPDATE cooldown SET reiniciar = %s WHERE id=%s;', ((epoch + 30), str(ctx.message.author.id),))
        thumb = 'https://i.ibb.co/k65YpDg/png-transparent-yellow-and-black-warning-sign-icon-warning-icons-angle-triangle-sign.png'
        img = 'https://i.ibb.co/wBwTdrC/3-forest005.jpg'
        embed = await embedding(ctx.message.author, 'Deletar personagem', 'Triste vê-lo partir... Deseja realmente deletar seu personagem?', footer='\U0001F630', thumbnail=thumb, imagem=img, cor=0x000000)
        resposta = await embed_menu(self, ctx, ctx.message.author, embed)
        if resposta != None:
            if resposta:
                await ctx.send(f'{ctx.message.author.mention} você deletou seu personagem .... Com sucesso... \U0001F622')
                self.db_cursor.execute('DELETE FROM users WHERE id=%s;', (str(ctx.message.author.id),))
                self.db_cursor.execute('DELETE FROM farm WHERE id=%s;', (str(ctx.message.author.id),))
                self.db_cursor.execute('DELETE FROM luzes WHERE id=%s;', (str(ctx.message.author.id),))
                self.db_cursor.execute('DELETE FROM cooldown WHERE id=%s;', (str(ctx.message.author.id),))
            else:
                await ctx.send(f'{ctx.message.author.mention} \U0001F633')

    @commands.command(aliases=['farm'])
    async def farmar(self, ctx):

        checa = await checando_db(self, ctx)
        if checa == False:
            await ctx.send(f'{ctx.message.author.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return
        
        self.db_cursor.execute('SELECT * FROM users WHERE id=%s', (str(ctx.message.author.id),))
        users = self.db_cursor.fetchone()
        self.db_cursor.execute('SELECT * FROM cooldown WHERE id=%s', (str(ctx.message.author.id),))
        cooldown = self.db_cursor.fetchone()
        self.db_cursor.execute('SELECT * FROM luzes WHERE id=%s', (str(ctx.message.author.id),))
        luzes = self.db_cursor.fetchone()
        self.db_cursor.execute('SELECT * FROM farm WHERE id=%s', (str(ctx.message.author.id),))
        farm = self.db_cursor.fetchone()

        # Retirar Futuramente
        checa = await checando_db(self, ctx, 'farm')
        if checa == False:
            self.db_cursor.execute('INSERT INTO farm VALUES (%s, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)', (ctx.author.id,))
            self.db.commit()

        epoch = round(time.time())
        if(epoch <= cooldown['farmar']):
            restante = cooldown['farmar'] - epoch
            await ctx.send(f'{ctx.message.author.mention}, você só pode usar o comando novamente daqui {display_time(restante)}')
        else:
            self.db_cursor.execute('UPDATE cooldown SET farmar=%s WHERE id=%s;', ((epoch+30), str(ctx.message.author.id),))
            self.db.commit()

            imagens = ['',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/d/d0/Isle_thatskygame.jpeg/revision/latest/scale-to-width-down/310?cb=20201019171300',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/3/32/Prairie-Village.png/revision/latest/scale-to-width-down/310?cb=20190614222621',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/b/b5/Forest_Social_Space.png/revision/latest/scale-to-width-down/310?cb=20190614222814',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/8/8a/Valley_ice_rink.png/revision/latest/scale-to-width-down/310?cb=20190624003927',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/8/82/Wasteland_broken_temple.png/revision/latest/scale-to-width-down/310?cb=20190624105808',
            'https://static.wikia.nocookie.net/sky-children-of-the-light/images/1/14/Vault_level_2.png/revision/latest/scale-to-width-down/310?cb=20190624230829'
            ]
            uid = users['farmando']
            if epoch < users['farmando_tempo'] or uid > 0:
                restante = users['farmando_tempo'] - epoch
                if restante > 60:
                    tempo = display_time(restante)
                else:
                    tempo = 'menos de 1 min'
                
                embed = await embedding(ctx.message.author, f'**Farm de ceras [{nomes_mapas[uid]}]**', f'Seu personagem ainda está farmando.\n**{tempo}** para terminar.')
                embed.set_image(url=imagens[uid])
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title = 'Farm de Ceras',
                    description = 'Seu personagem está de frente para os portais de cada reino. Em qual reino você gostaria de farmar?',
                    colour = discord.Colour.blue()
                )

                # Calculo de tempo de farm baseado no Nível do jogador
                i = 0
                tt = [0, 0, 0, 0, 0, 0, 0]
                la = [0, 0, 0, 0, 0, 0, 0]
                farm_comp = ['', '', '', '', '', '', '']
                np = users['nivel']
                la_total = users['total_luzes']
                eq = eq_vel(np)
                while i <= 6:
                    tt[i] = round((tempo_farm[i] - tempo_farm[i]*eq))
                    if i > 0:
                        la[i] = luzes[f'{id_mapas[i]}']
                        if farm[f'{id_mapas[i]}'] == True:
                            farm_comp[i] = '__(Concluido)__'
                    i += 1
                    
                embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                if np > 0:
                    embed.add_field(name='\u200b', value=f'\n**Nível {np}** ({la_total} Luzes Aladas)', inline=False)
                    embed.add_field(name=f'*{round(eq*100, 2)}% mais veloz*', value='\u200b', inline=False)
                embed.add_field(name=f'(1) Ilha {la[1]}/{luzes_reinos[1]} Luzes {farm_comp[1]}', value=display_time(tt[1]), inline=False)
                embed.add_field(name=f'(2) Campina {la[2]}/{luzes_reinos[2]} Luzes {farm_comp[2]}', value=display_time(tt[2]), inline=False)
                embed.add_field(name=f'(3) Floresta {la[3]}/{luzes_reinos[3]} Luzes {farm_comp[3]}', value=display_time(tt[3]), inline=False)
                embed.add_field(name=f'(4) Vale {la[4]}/{luzes_reinos[4]} Luzes {farm_comp[4]}', value=display_time(tt[4]), inline=False)
                embed.add_field(name=f'(5) Sertão {la[5]}/{luzes_reinos[5]} Luzes {farm_comp[5]}', value=display_time(tt[5]), inline=False)
                embed.add_field(name=f'(6) Relicário {la[6]}/{luzes_reinos[6]} Luzes {farm_comp[6]}', value=display_time(tt[6]), inline=False)
                embed.set_image(url='https://static.wikia.nocookie.net/sky-children-of-the-light/images/4/4e/17AE96F9-C16B-48C0-9E18-46F199E41081.jpeg/revision/latest/scale-to-width-down/300?cb=20191109140336')
                message = await ctx.send(embed=embed)

                await message.add_reaction("1️⃣")
                await message.add_reaction("2️⃣")
                await message.add_reaction("3️⃣")
                await message.add_reaction("4️⃣")
                await message.add_reaction("5️⃣")
                await message.add_reaction("6️⃣")
                await message.add_reaction("❌")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❌"]
                    # Isso garante que apenas quem enviou o comando possa interagir com o "menu"
                while True:
                    try:
                        reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)
                        # Esperando por uma reação ser adicionada - Timeout após 30 segundos

                        if str(reaction.emoji) == "1️⃣":
                            if farm['ilha'] == True:
                                await ctx.send(f'Você já farmou Ilha hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (1, (epoch + tt[1]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Ilha', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Ilha', f'O Farm irá durar em torno de {display_time(tt[1])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "2️⃣":
                            if farm['campina'] == True:
                                await ctx.send(f'Você já farmou Campina hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (2, (epoch + tt[2]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Campina', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Campina', f'O Farm irá durar em torno de {display_time(tt[2])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "3️⃣":
                            if farm['floresta'] == True:
                                await ctx.send(f'Você já farmou Floresta hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (3, (epoch + tt[3]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Floresta', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Floresta', f'O Farm irá durar em torno de {display_time(tt[3])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "4️⃣":
                            if farm['vale'] == True:
                                await ctx.send(f'Você já farmou Vale hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (4, (epoch + tt[4]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Vale', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Vale', f'O Farm irá durar em torno de {display_time(tt[4])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "5️⃣":
                            if farm['sertao'] == True:
                                await ctx.send(f'Você já farmou Sertão hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (5, (epoch + tt[5]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Sertão', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Sertão', f'O Farm irá durar em torno de {display_time(tt[5])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "6️⃣":
                            if farm['relicario'] == True:
                                await ctx.send(f'Você já farmou Relicário hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                self.db_cursor.execute('UPDATE users SET farmando=%s, farmando_tempo=%s WHERE id=%s;', (6, (epoch + tt[6]), str(ctx.message.author.id),))
                                self.db.commit()
                                embed = await embedding(user, 'Farm Relicário', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Relicário', f'O Farm irá durar em torno de {display_time(tt[6])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "❌":
                            self.db_cursor.execute('UPDATE cooldown SET farmar=%s WHERE id=%s;', (0, str(ctx.message.author.id),))
                            self.db.commit()
                            await message.delete()
                            break

                        else:
                            await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        await message.delete()
                        break
                        # Terminando o loop se o usuário não reagir após 30 segs
    
    @commands.command()
    async def status(self, ctx, mention: discord.Member=None):
        if not mention:
            mention = ctx.message.author

        self.db_cursor.execute('SELECT * FROM users WHERE id=%s', (str(mention.id),))
        users = self.db_cursor.fetchone()
        
        checa = await checando_db(self, ctx)
        if checa == False:
            await ctx.send(f'{mention.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return
        nivel = users['nivel']
        path = "./images/" + f'{nivel}' + ".png"
        files = discord.File(path, filename="image.png")
        image = 'https://i.ibb.co/JR15W5n/EYp-Yh2k-UYAAd68-B.jpg'
        velas = round(users['velas'], 2)
        velas_eden = round(users['velas_eden'], 2)
        if users['farmando'] > 0:
            epoch = round(time.time())
            restante = users['farmando_tempo'] - epoch
            uid = users['farmando']
            if restante > 60:
                disponibilidade = f'Farmando __**{nomes_mapas[uid]}**__\nFalta **{display_time(restante)}**'
            else:
                disponibilidade = f'Farmando __**{nomes_mapas[uid]}**__\nFalta **menos de 1 minuto**'
        else:
            disponibilidade = '__**Disponível para farmar**__'
        total_luzes = users['total_luzes']
        nome_conta = users['nome']
        vel = eq_vel(nivel, True)
        titulo = f'{nome_conta} - Nível {nivel} ({vel}% mais veloz)'
        conteudo = f'**{total_luzes}/{exp_nivel[nivel]}** Luzes Aladas\n\u200b\n{disponibilidade}\nVelas: **{velas}** | Velas Eden: **{velas_eden}**'
        frases_inspiradoras = [
            'Se chover, procure o Arco-Íris\nSe escurecer, procure as Estrelas',
            'Continue voando!',
            'Você é único neste planeta',
            'A única pessoa que você deveria tentar ser melhor\nÉ a pessoa que você foi ontem.'
            ]
        thumbnail = f'\"{random.choice(frases_inspiradoras)}\"'
        embed = await embedding(ctx.message.author, titulo, conteudo, thumbnail, "attachment://image.png", image, 0x6666ff)
        await ctx.send(file=files, embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ceras(self, ctx):
        if ctx.message.author.id == 127081215256821760:
            job(self)

    @commands.command()
    async def placar(self, ctx, qnt=3):
        self.db_cursor.execute('SELECT * FROM users')
        users = self.db_cursor.fetchall()

        leaderboards = []
        for user in list(users):
            leaderboards.append(LeaderBoardPosition(user['id'], user['velas'], user['nome']))

        top = sorted(leaderboards, key=lambda x: x.velas, reverse=True)

        embed = await embedding(ctx.message.author, 'Leaderboard', f'Um placar de jogadores para ver quem coletou mais velas neste mês.')

        for number, user in enumerate(top):
            if number >= 12:
                break
            embed.add_field(name='{0}. {1}'.format(number + 1, user.nome), value='__{0} Velas__'.format(round(user.velas, 2)), inline=True)
        await ctx.send(embed=embed)

    # Tasks
    @tasks.loop(seconds=15)
    async def update_sky(self):
        await self.client.wait_until_ready()
        
        self.db_cursor.execute('SELECT * FROM users;')
        users = self.db_cursor.fetchall()

        for user in users:
            uid = user['farmando']
            epoch = round(time.time())
            if epoch >= user['farmando_tempo'] and uid > 0:
                await eventos_farm(self, user)
                self.db_cursor.execute('UPDATE farm SET {} = TRUE WHERE id = %s;'.format(id_mapas[uid]), (str(user['id']),))
                self.db_cursor.execute('UPDATE users SET farmando = 0, farmando_tempo = 0 WHERE id = %s;', (str(user['id']),))
                self.db.commit()

    @tasks.loop(seconds=1)
    async def schedules(self):
        schedule.run_pending()

def job(self):
    self.db_cursor.execute('UPDATE farm SET ilha = FALSE, campina = FALSE, floresta = FALSE, vale = FALSE, sertao = FALSE, relicario = FALSE;')

def display_time(seconds, granularity=2):
    result = []

    intervals = (
    ('semanas', 604800),  # 60 * 60 * 24 * 7
    ('dias', 86400),    # 60 * 60 * 24
    ('horas', 3600),    # 60 * 60
    ('minutos', 60),
    ('segundos', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ' '.join(result[:granularity])

async def eventos_farm(self, user):
    channel = self.client.get_channel(canal_updates)

    # Variáveis úteis
    id_farm = user['farmando']
    qnt_ceras = ceras_farm[id_farm]

    embed = discord.Embed(
        title = f'**{nomes_mapas[id_farm]}**',
        description = f'Você concluiu seu farm com sucesso.',
        colour = 0x33dddd
    )
    embed.set_author(name=user['nome'], icon_url='')
    embed.set_footer(text='Utilize o comando `farmar` novamente para farmar outro mapa')
    embed.set_image(url='https://www.tyden.cz/obrazek/201907/5d35f286e3f64/crop-1882887-sky_520x250.jpg')

    self.db_cursor.execute('SELECT * FROM luzes WHERE id=%s', (str(user['id']),))
    luzes = self.db_cursor.fetchone()
    luz_reino = luzes[f'{id_mapas[id_farm]}']
    luzes_falta = luzes_reinos[id_farm] - luzes[f'{id_mapas[id_farm]}']
    print(f'\n{luz_reino} | {luzes_reinos[id_farm]} | {luzes_falta}\n')
    ll = 0
    ni = user['nivel']
    # 100% de chance de acontecer coletas de luzes
    if luzes_falta > 0:
        if luzes_falta == 1:
            ll = 1
        else:
            ll = random.randint(1, luzes_falta)
        
        ni = 1
        while ni <= 11:
            if (user['total_luzes']+ll) < exp_nivel[ni]:
                break
            ni += 1

        embed.add_field(name='Luzes Aladas', value=f'Você obteve êxito em coletar {ll} luzes aladas' , inline=False)
    
    # 5% de chance de encontrar arco-iris (Ilha)
    if id_farm == 1:
        if random.randint(1, 100) <= 5:
            embed.add_field(name='Arco-Íris', value=f'De alguma forma, você encontrou uma Ponte de Arco-Íris. **Que sorte!** (**30x Cera**)' , inline=False)
            qnt_ceras = qnt_ceras*30
    # 20% de chance de encontrar arco-iris (Floresta)
    elif id_farm == 3:
        if random.randint(1, 100) <= 20:
            embed.add_field(name='Arco-Íris', value=f'Durante o voo pela floresta, você se deparou de frente com um Arco-Íris. **Que sorte!** (**4x Cera**)' , inline=False)
            qnt_ceras = qnt_ceras*4

    embed.add_field(name='Ceras Coletadas', value=f'{qnt_ceras} ceras' , inline=False)

    self.db_cursor.execute('UPDATE luzes SET {} = {} + %s WHERE id=%s;'.format(id_mapas[id_farm], id_mapas[id_farm]), (ll, str(user['id']),))
    self.db_cursor.execute('UPDATE users SET velas = velas + %s, total_luzes = total_luzes + %s, nivel = %s WHERE id=%s;', (qnt_ceras, ll, ni-1, str(user['id']),))
    self.db.commit()

    iid = user['id']
    await channel.send(f'<@{iid}>')
    await channel.send(embed=embed)

class LeaderBoardPosition:

    def __init__(self, user, velas, nome):
        self.user = user
        self.velas = velas
        self.nome = nome

def setup(client):
    client.add_cog(Sky(client))