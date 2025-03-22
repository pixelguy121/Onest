import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Role-based ping limits
PING_LIMITS = {
    "basic_store": {"@everyone": 3, "@here": 2},
    "premium_store": {"@everyone": 5, "@here": 4}
}

# Dictionary to store user ping usage and reset time
user_pings = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    reset_ping_usage.start()  # Start the reset task

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    user_id = message.author.id
    role_names = [role.name.lower() for role in message.author.roles]

    # Determine user's ping limit based on roles
    user_limit = PING_LIMITS.get("basic")  # Default role limit
    for role, limits in PING_LIMITS.items():
        if role in role_names:
            user_limit = limits
            break

    if "@everyone" in message.content or "@here" in message.content:
        if user_id not in user_pings:
            user_pings[user_id] = {"@everyone": 0, "@here": 0, "reset_time": datetime.utcnow() + timedelta(days=1)}

        mention_type = "@everyone" if "@everyone" in message.content else "@here"

        # Check if user has remaining pings
        if user_pings[user_id][mention_type] < user_limit[mention_type]:
            user_pings[user_id][mention_type] += 1
            remaining_pings = user_limit[mention_type] - user_pings[user_id][mention_type]
            await message.channel.send(
                f"{message.author.mention}, you used `{mention_type}`. "
                f"You have `{remaining_pings}` pings left for today."
            )
        else:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, you have **reached the limit** for `{mention_type}` pings! "
                "Your ping limit will **reset in 24 hours**."
            )

    await bot.process_commands(message)

@tasks.loop(hours=24)
async def reset_ping_usage():
    """Resets user ping limits every 24 hours."""
    current_time = datetime.utcnow()
    to_reset = [user for user, data in user_pings.items() if data["reset_time"] <= current_time]

    for user in to_reset:
        user_pings[user]["@everyone"] = 0
        user_pings[user]["@here"] = 0
        user_pings[user]["reset_time"] = datetime.utcnow() + timedelta(days=1)

bot.run("MTM1MjkwNjA5NzgzMjQ5NzI0Nw.GZ39Q0.rhzfOvkQYj1VIrOwH2nBkLD5u2NKSf19Zlqwp4")
