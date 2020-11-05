import discord

# embedding: ctx, Autor, Título, Conteúdo{, Footer, Thumbnail, Imagem}
async def embedding(ctx, autor, titulo, conteudo, footer='', thumbnail='', imagem='', cor=0xffffff):
    embed = discord.Embed(
        title = titulo,
        description = conteudo,
        colour = cor
    )

    if footer != '':
        embed.set_footer(text=footer)
    if thumbnail != '':
        embed.set_thumbnail(url=thumbnail)
    if imagem != '':
        embed.set_image(url=imagem)
    embed.set_author(name=autor.name, icon_url=autor.avatar_url)
    #embed.add_field(name="Field1", value="hi", inline=False)
    #embed.add_field(name="Field2", value="hi2", inline=False)

    return embed