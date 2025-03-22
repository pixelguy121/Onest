import discord
from discord.ext import commands
import json
import os

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix="!", intents=intents)

# Define role-based ping limits (lifetime usage)
ping_limits = {
    "basic": {"@everyone": 3, "@here": 2},
    "premium": {"@everyone": 5, "@here": 4},
    "admin": {"@everyone": 999, "@here": 999}  # No limit
}

# Load user ping data from JSON file
PING_DATA_FILE = "pings.json"
if os.path.exists(PING_DATA_FILE):
    with open(PING_DATA_FILE, "r") as f:
        user_pings = json.load(f)
else:
    user_pings = {}

def save_pings():
    with open(PING_DATA_FILE, "w") as f:
        json.dump(user_pings, f, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    user_id = str(message.author.id)  # Store as string for JSON compatibility
    role_names = [role.name.lower() for role in message.author.roles]

    # Check if user has a valid role for pinging
    valid_roles = set(ping_limits.keys())
    user_roles = set(role_names) & valid_roles
    if not user_roles:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, you do not have permission to use @everyone or @here.",
            delete_after=5
        )
        return

    # Determine user's ping limit based on highest role
    user_role = sorted(user_roles, key=lambda r: list(ping_limits.keys()).index(r))[0]
    user_limit = ping_limits[user_role]

    if "@everyone" in message.content or "@here" in message.content:
        mention_type = "@everyone" if "@everyone" in message.content else "@here"

        # Initialize user data if not present
        if user_id not in user_pings:
            user_pings[user_id] = {"@everyone": 0, "@here": 0}

        if user_pings[user_id][mention_type] >= user_limit[mention_type]:
            user_pings[user_id] = {"@everyone": 0, "@here": 0}  # Reset before role removal
            save_pings()
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, you have **used all** your `{mention_type}` pings permanently! Your role will now be removed.",
                delete_after=5
            )
            role_to_remove = discord.utils.get(message.guild.roles, name=user_role)
            if role_to_remove:
                await message.author.remove_roles(role_to_remove)
            return

        user_pings[user_id][mention_type] += 1
        save_pings()
        remaining_pings = user_limit[mention_type] - user_pings[user_id][mention_type]
        await message.channel.send(
            f"{message.author.mention}, you used `{mention_type}`. You have **{remaining_pings} pings left** for a lifetime.",
            delete_after=5
        )

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def resetping(ctx, member: discord.Member):
    user_id = str(member.id)
    role_names = [role.name.lower() for role in member.roles]
    user_roles = set(role_names) & set(ping_limits.keys())
    if not user_roles:
        await ctx.send(f"{member.mention} does not have a role that allows pinging.")
        return

    user_role = sorted(user_roles, key=lambda r: list(ping_limits.keys()).index(r))[0]
    user_pings[user_id] = {"@everyone": 0, "@here": 0}  # Reset their pings
    save_pings()
    await ctx.send(f"{member.mention}'s ping count has been reset.")

if not TOKEN:
    print("ERROR: DISCORD_TOKEN is missing! Set it in Railway environment variables.")
else:
    bot.run(TOKEN)
