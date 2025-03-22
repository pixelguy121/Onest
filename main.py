import discord
from discord.ext import commands
import json
import os

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")  # Debugging line

bot.run(os.environ['DISCORD_TOKEN'])