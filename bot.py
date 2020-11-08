import discord
import asyncio
import asyncpg
import random
import logging
import schedule
import json
import time
import re
import os
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from itertools import cycle

logging.basicConfig(level=logging.INFO)

prefix = os.environ['COMMAND_PREFIX']
client = commands.Bot(command_prefix = prefix)

# Eventos

@client.event
async def on_ready():
    print('Bot pronto.')

@client.event
async def on_member_join(member):
    print(f'{member} se juntou ao servidor')
        
@client.event
async def on_message(message):
    canal_updates = os.environ['CANAL_UPDATES']
    if message.channel.id == canal_updates:
        #if message.author.id != message.guild.owner_id:
        await message.delete()
        dele = await message.channel.send(f'{message.author.mention} este canal é apenas para atualizações do Simulador de Sky.\nSe deseja utilizar comandos, por favor use o canal #comandos')
        await dele.delete(delay=20)
        return
    await client.process_commands(message)

@client.event
async def on_member_remove(member):
    print(f'{member} saiu do servidor')

# Comandos
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    await ctx.message.delete()
    client.load_extension(f'cogs.{extension}')
    msg = await ctx.send(f'cog {extension} carregada')
    print(f'cog {extension} carregada')
    await msg.delete(delay=3)

@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    await ctx.message.delete()
    client.unload_extension(f'cogs.{extension}')
    msg = await ctx.send(f'cog {extension} descarregada')
    print(f'cog {extension} descarregada')
    await msg.delete(delay=3)

@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    await ctx.message.delete()
    client.reload_extension(f'cogs.{extension}')
    msg = await ctx.send(f'cog {extension} recarregada')
    print(f'cog {extension} recarregada')
    await msg.delete(delay=3)


client.load_extension(f'cogs.sky')

token = os.environ['DISCORD_TOKEN']
client.run(token)
