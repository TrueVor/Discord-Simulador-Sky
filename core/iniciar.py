from core.embed import embedding # pylint: disable=import-error

async def iniciando(users, user, farm, ctx):
    users[f'{user.id}'] = {}
    users[f'{user.id}']['nome'] = user.name
    users[f'{user.id}']['velas'] = 0
    users[f'{user.id}']['velas_eden'] = 0
    users[f'{user.id}']['total_luzes'] = 0
    users[f'{user.id}']['nivel'] = 0
    users[f'{user.id}']['farmando'] = 0
    users[f'{user.id}']['farmando_tempo'] = 0
    users[f'{user.id}']['cooldown'] = {}
    users[f'{user.id}']['cooldown']['farmar'] = 0
    users[f'{user.id}']['cooldown']['luzes'] = 0
    users[f'{user.id}']['cooldown']['eden'] = 0
    users[f'{user.id}']['cooldown']['iniciar'] = 0
    users[f'{user.id}']['cooldown']['reiniciar'] = 0
    users[f'{user.id}']['luzes'] = {}
    users[f'{user.id}']['luzes']['ilha'] = 0
    users[f'{user.id}']['luzes']['campina'] = 0
    users[f'{user.id}']['luzes']['floresta'] = 0
    users[f'{user.id}']['luzes']['vale'] = 0
    users[f'{user.id}']['luzes']['sertao'] = 0
    users[f'{user.id}']['luzes']['relicario'] = 0
    farm[f'{user.id}'] = {}
    farm[f'{user.id}']['ilha'] = False
    farm[f'{user.id}']['campina'] = False
    farm[f'{user.id}']['floresta'] = False
    farm[f'{user.id}']['vale'] = False
    farm[f'{user.id}']['sertao'] = False
    farm[f'{user.id}']['relicario'] = False
    embed = await embedding(ctx, user, '**Uma Criança da Luz Nasce**', f'*Uma criança da luz acaba de nascer*\nBem vindo(a) **{user.name}**!', '', user.avatar_url, 'https://s3.amazonaws.com/sensortower-itunes/blog/2019/07/sky-children-of-the-light.jpg')
    embed.set_author(name='', icon_url='')
    await ctx.send(embed=embed)

async def checando_usuario(users, user):
    if not f'{user.id}' in users:
        return False
    return True