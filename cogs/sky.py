import discord
import json
import asyncio
import asyncpg
import time
import random
import schedule
import os
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from core.iniciar import iniciando, checando_usuario # pylint: disable=import-error
from core.embed import embedding # pylint: disable=import-error

tempo_farm = [0, 900, 4500, 2700, 3000, 2700, 1500]
ceras_farm = [0, 0.14, 4.33, 3.73, 3.85, 4.25, 0.89]
luzes_reinos = [0, 8, 21, 16, 11, 16, 8]
exp_nivel = [0, 1, 2, 5, 10, 20, 35, 55, 75, 100, 120, 150]
nomes_mapas = ['', 'Ilha', 'Campina', 'Floresta', 'Vale', 'Sertão', 'Relicário']
id_mapas = ['', 'ilha', 'campina', 'floresta', 'vale', 'sertao', 'relicario']
canal_updates = 774012109511852034

class Sky(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.update_sky.add_exception_type(asyncpg.PostgresConnectionError)
        self.update_sky.start()
        self.schedules.add_exception_type(asyncpg.PostgresConnectionError)
        self.schedules.start()

    def cog_unload(self):
        self.update_sky.cancel()
        self.schedules.cancel()

    # Eventos
    #@commands.Cog.listener()
    #async def on_ready(self):
        #job()
        #channel = self.client.get_channel(canal_updates)
        #await channel.send('Crianças da luz, **Todas as ceras foram resetadas.** Tenham um ótimo farm!')

    # Comandos
    @commands.command()
    async def iniciar(self, ctx):
        with open('sky.json', 'r') as f:
            users = json.load(f)
        with open('farm.json', 'r') as f:
            farm = json.load(f)
        
        checa = await checando_usuario(users, ctx.message.author)

        if checa == False:
            await iniciando(users, ctx.message.author, farm, ctx)

            with open('sky.json', 'w') as f:
                json.dump(users, f)
            with open('farm.json', 'w') as f:
                json.dump(farm, f)
        else:
            embed = await embedding(ctx, ctx.message.author, 'Comando Iniciar', f'**{ctx.message.author.name}**, você só pode iniciar uma vez', 'Caso desejas deletar seu personagem e iniciar novamente, digite o comando `reiniciar`')
            await ctx.send(embed=embed)

    @commands.command()
    async def reiniciar(self, ctx):
        with open('sky.json', 'r') as f:
            users = json.load(f)
        with open('farm.json', 'r') as f:
            farm = json.load(f)
        
        checa = await checando_usuario(users, ctx.message.author)
        if checa == False:
            await ctx.send(f'{ctx.message.author.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return

        epoch = round(time.time())
        if(epoch < users[f'{ctx.author.id}']['cooldown']['reiniciar']):
            restante = users[f'{ctx.author.id}']['cooldown']['reiniciar'] - epoch
            await ctx.send(f'Você só pode usar o comando `reiniciar` novamente daqui {display_time(restante)}')
        else:
            embed = discord.Embed(
                    title = 'Deletar personagem',
                    description = 'Deseja realmente deletar seu personagem e iniciar do zero?',
                    colour = 0x000000
                )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            message = await ctx.send(embed=embed)

            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

                    if str(reaction.emoji) == "✅":
                        await message.delete()
                        del users[f'{user.id}']
                        await iniciando(users, user, farm, ctx)
                        users[f'{user.id}']['cooldown']['reiniciar'] = epoch + 604800

                        with open('sky.json', 'w') as f:
                            json.dump(users, f)
                        with open('farm.json', 'w') as f:
                            json.dump(farm, f)
                        break
                    elif str(reaction.emoji) == "❌":
                        await message.delete()
                        break
                    else:
                        await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    await message.delete()
                    break

    @commands.command(aliases=['farm'])
    async def farmar(self, ctx):
        with open('sky.json', 'r') as f:
            users = json.load(f)
        with open('farm.json', 'r') as f:
            farm = json.load(f)

        checa = await checando_usuario(users, ctx.message.author)
        if checa == False:
            await ctx.send(f'{ctx.message.author.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return

        checa = await checando_usuario(farm, ctx.message.author)
        if checa == False:
            farm[f'{ctx.message.author.id}'] = {}
            farm[f'{ctx.message.author.id}']['ilha'] = False
            farm[f'{ctx.message.author.id}']['campina'] = False
            farm[f'{ctx.message.author.id}']['floresta'] = False
            farm[f'{ctx.message.author.id}']['vale'] = False
            farm[f'{ctx.message.author.id}']['sertao'] = False
            farm[f'{ctx.message.author.id}']['relicario'] = False

        epoch = round(time.time())
        if(epoch <= users[f'{ctx.message.author.id}']['cooldown']['farmar']):
            restante = users[f'{ctx.message.author.id}']['cooldown']['farmar'] - epoch
            await ctx.send(f'{ctx.message.author.mention}, você só pode usar o comando novamente daqui {display_time(restante)}')
        else:
            users[f'{ctx.message.author.id}']['cooldown']['farmar'] = epoch + 30
            with open('sky.json', 'w') as f:
                json.dump(users, f)
            imagens = ['', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/d/d0/Isle_thatskygame.jpeg/revision/latest/scale-to-width-down/310?cb=20201019171300', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/3/32/Prairie-Village.png/revision/latest/scale-to-width-down/310?cb=20190614222621', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/b/b5/Forest_Social_Space.png/revision/latest/scale-to-width-down/310?cb=20190614222814', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/8/8a/Valley_ice_rink.png/revision/latest/scale-to-width-down/310?cb=20190624003927', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/8/82/Wasteland_broken_temple.png/revision/latest/scale-to-width-down/310?cb=20190624105808', 'https://static.wikia.nocookie.net/sky-children-of-the-light/images/1/14/Vault_level_2.png/revision/latest/scale-to-width-down/310?cb=20190624230829']
            uid = users[f'{ctx.message.author.id}']['farmando']
            if epoch < users[f'{ctx.message.author.id}']['farmando_tempo'] or uid > 0:
                restante = users[f'{ctx.message.author.id}']['farmando_tempo'] - epoch
                if restante > 60:
                    tempo = display_time(restante)
                else:
                    tempo = 'menos de 1 min'
                
                embed = await embedding(ctx, ctx.message.author, f'**Farm de ceras [{nomes_mapas[uid]}]**', f'Seu personagem ainda está farmando.\n**{tempo}** para terminar.')
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
                np = users[f'{ctx.message.author.id}']['nivel']
                la_total = users[f'{ctx.message.author.id}']['total_luzes']
                while i <= 6:
                    tt[i] = round(tempo_farm[i] - ( tempo_farm[i]*(np*0.05) ))
                    if i > 0:
                        la[i] = users[f'{ctx.message.author.id}']['luzes'][f'{id_mapas[i]}']
                        if farm[f'{ctx.message.author.id}'][f'{id_mapas[i]}'] == True:
                            farm_comp[i] = '__(Concluido)__'
                    i += 1
                    
                embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
                if np > 0:
                    embed.add_field(name='\u200b', value=f'\n**Nível {np}** ({la_total} Luzes Aladas)', inline=False)
                    embed.add_field(name=f'*{np*5}% mais veloz*', value='\u200b', inline=False)
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
                            if farm[f'{user.id}']['ilha'] == True:
                                await ctx.send(f'Você já farmou Ilha hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 1
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[1]
                                embed = await embedding(ctx, user, 'Farm Ilha', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Ilha', f'O Farm irá durar em torno de {display_time(tt[1])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "2️⃣":
                            if farm[f'{user.id}']['campina'] == True:
                                await ctx.send(f'Você já farmou Campina hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 2
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[2]
                                embed = await embedding(ctx, user, 'Farm Campina', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Campina', f'O Farm irá durar em torno de {display_time(tt[2])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "3️⃣":
                            if farm[f'{user.id}']['floresta'] == True:
                                await ctx.send(f'Você já farmou Floresta hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 3
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[3]
                                embed = await embedding(ctx, user, 'Farm Floresta', f'**{ctx.message.author.name}**, seu personagem iniciou Farm na Floresta', f'O Farm irá durar em torno de {display_time(tt[3])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "4️⃣":
                            if farm[f'{user.id}']['vale'] == True:
                                await ctx.send(f'Você já farmou Vale hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 4
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[4]
                                embed = await embedding(ctx, user, 'Farm Vale', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Vale', f'O Farm irá durar em torno de {display_time(tt[4])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "5️⃣":
                            if farm[f'{user.id}']['sertao'] == True:
                                await ctx.send(f'Você já farmou Sertão hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 5
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[5]
                                embed = await embedding(ctx, user, 'Farm Sertão', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Sertão', f'O Farm irá durar em torno de {display_time(tt[5])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "6️⃣":
                            if farm[f'{user.id}']['relicario'] == True:
                                await ctx.send(f'Você já farmou Relicário hoje, {user.mention}')
                            else:
                                epoch = round(time.time())
                                users[f'{user.id}']['farmando'] = 6
                                users[f'{user.id}']['farmando_tempo'] = epoch + tt[6]
                                embed = await embedding(ctx, user, 'Farm Relicário', f'**{ctx.message.author.name}**, seu personagem iniciou Farm no Relicário', f'O Farm irá durar em torno de {display_time(tt[6])}.\nVocê será notificado aqui quando seu personagem terminar', user.avatar_url)
                                await ctx.send(embed=embed)
                            await message.delete()
                            break
                        elif str(reaction.emoji) == "❌":
                            users[f'{ctx.message.author.id}']['cooldown']['farmar'] = 0
                            await message.delete()
                            break

                        else:
                            await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        await message.delete()
                        break
                        # Terminando o loop se o usuário não reagir após 30 segs
        
        with open('sky.json', 'w') as f:
            json.dump(users, f)
    
    @commands.command()
    async def status(self, ctx):
        with open('sky.json', 'r') as f:
            sky = json.load(f)
        checa = await checando_usuario(sky, ctx.message.author)
        if checa == False:
            await ctx.send(f'{ctx.message.author.mention}, você ainda não criou seu personagem utilizando o comando `iniciar`')
            return
        nivel = sky[f'{ctx.message.author.id}']['nivel']
        path = "./images/" + f'{nivel}' + ".png"
        files = discord.File(path, filename="image.png")
        image = 'https://i.ibb.co/JR15W5n/EYp-Yh2k-UYAAd68-B.jpg'
        velas = round(sky[f'{ctx.message.author.id}']['velas'], 2)
        velas_eden = round(sky[f'{ctx.message.author.id}']['velas_eden'], 2)
        if sky[f'{ctx.message.author.id}']['farmando'] > 0:
            epoch = round(time.time())
            restante = sky[f'{ctx.message.author.id}']['farmando_tempo'] - epoch
            uid = sky[f'{ctx.message.author.id}']['farmando']
            if restante > 60:
                disponibilidade = f'Farmando __**{nomes_mapas[uid]}**__\nFalta **{display_time(restante)}**'
            else:
                disponibilidade = f'Farmando __**{nomes_mapas[uid]}**__\nFalta **menos de 1 minuto**'
        else:
            disponibilidade = '__**Disponível para farmar**__'
        total_luzes = sky[f'{ctx.message.author.id}']['total_luzes']
        titulo = f'Nível {nivel}'
        conteudo = f'**{total_luzes}/{exp_nivel[nivel]}** Luzes Aladas\n\u200b\n{disponibilidade}\nVelas: **{velas}** | Velas Eden: **{velas_eden}**'
        frases_inspiradoras = [
            'Quando chover, procure pelo Arco-Íris!\nQuando estiver escuro, procure pelas Estrelas!',
            'Continue voando!',
            'Você é único neste planeta',
            'A única pessoa que você deveria tentar ser melhor\nÉ a pessoa que você foi ontem.'
            ]
        thumbnail = f'\"{random.choice(frases_inspiradoras)}\"'
        embed = await embedding(ctx, ctx.message.author, titulo, conteudo, thumbnail, "attachment://image.png", image, 0x6666ff)
        await ctx.send(file=files, embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ceras(self, ctx):
        if ctx.message.author.id == 127081215256821760:
            job()

    # Tasks
    @tasks.loop(seconds=15)
    async def update_sky(self):
        await self.client.wait_until_ready()
        with open('sky.json', 'r') as f:
            sky = json.load(f)
        with open('farm.json', 'r') as f:
            farm = json.load(f)

        dump = False
        for id in sky:
            uid = sky[id]['farmando']
            epoch = round(time.time())
            if epoch >= sky[id]['farmando_tempo'] and uid > 0:
                await eventos_farm(self, sky, id)

                if not id in farm:
                    farm[id] = {}
                    farm[id]['ilha'] = False
                    farm[id]['campina'] = False
                    farm[id]['floresta'] = False
                    farm[id]['vale'] = False
                    farm[id]['sertao'] = False
                    farm[id]['relicario'] = False
                farm[id][f'{id_mapas[uid]}'] = True
                sky[id]['farmando'] = 0
                dump = True
        if dump == True:
            with open('sky.json', 'w') as f:
                json.dump(sky, f)
            with open('farm.json', 'w') as f:
                json.dump(farm, f)

    @tasks.loop(seconds=1)
    async def schedules(self):
        schedule.run_pending()

def job():
    with open('farm.json', 'r') as f:
        farm = json.load(f)
    for id in list(farm):
        del farm[id]
    with open('farm.json', 'w') as f:
        json.dump(farm, f)

schedule.every().day.at("05:00").do(job)

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

async def eventos_farm(self, users, id):
    channel = self.client.get_channel(canal_updates)

    # Variáveis úteis
    id_farm = users[id]['farmando']
    qnt_ceras = ceras_farm[id_farm]

    embed = discord.Embed(
        title = f'**{nomes_mapas[id_farm]}**',
        description = f'Você concluiu seu farm com sucesso.',
        colour = 0x33dddd
    )
    embed.set_author(name=users[id]['nome'], icon_url='')
    embed.set_footer(text='Utilize o comando `farmar` novamente para farmar outro mapa')
    embed.set_image(url='https://www.tyden.cz/obrazek/201907/5d35f286e3f64/crop-1882887-sky_520x250.jpg')

    luzes_falta = luzes_reinos[id_farm] - users[id]['luzes'][f'{id_mapas[id_farm]}']

    # 100% de chance de acontecer coletas de luzes
    if luzes_falta > 0:
        if luzes_falta == 1:
            luzes = 1
        else:
            luzes = random.randint(1, luzes_falta)
        
        embed.add_field(name='Luzes Aladas', value=f'Você obteve êxito em coletar {luzes} luzes aladas' , inline=False)
        users[id]['luzes'][f'{id_mapas[id_farm]}'] += luzes
        users[id]['total_luzes'] += luzes

        i = 1
        while i <= 11:
            if users[id]['total_luzes'] <= exp_nivel[i]:
                users[id]['nivel'] = i
                break
            i += 1
    
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

    users[id]['velas'] += qnt_ceras
    await channel.send(f'<@{id}>, seu personagem terminou o Farm.')
    await channel.send(embed=embed)

def setup(client):
    client.add_cog(Sky(client))