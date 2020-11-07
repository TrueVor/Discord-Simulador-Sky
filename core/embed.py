import discord
import asyncio

# embedding: Autor, Título, Conteúdo{, Footer, Thumbnail, Imagem}
async def embedding(autor, titulo, conteudo, footer='', thumbnail='', imagem='', cor=0xffffff):
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

async def embed_menu(self, ctx, autor, embed):
    embed.set_author(name=autor.name, icon_url=autor.avatar_url)
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    def check(reaction, user):
        return user == autor and str(reaction.emoji) in ["✅", "❌"] # Somente a pessoa da variavel `autor` poderá reagir
    while True:
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)
            if str(reaction.emoji) == "✅":
                await message.delete()
                return True
            elif str(reaction.emoji) == "❌":
                await message.delete()
                return False
            else:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            await message.delete()
            break
    return None