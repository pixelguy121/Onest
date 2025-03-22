import discord
from discord.ext import commands
import json
import os

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


bot.run("MTM1MjkwNjA5NzgzMjQ5NzI0Nw.GBcBJM.jcjkICzwzSFpL51GfSHqYVCrhE6Qn7zkB_lqBM")
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
@bot.event
async def on_message(message):
    print(f"Message received: {message.content}")  # Debugging line
