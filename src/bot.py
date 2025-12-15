#Don't touch
import discord
from discord.ext import commands
from config import TOKEN, LOG_CHANNEL_ID
from database import *
from commands import register_commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

invite_cache = {}

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    for guild in bot.guilds:
        invite_cache[guild.id] = await guild.invites()
    await register_commands(bot)
    await bot.tree.sync()
    print("Slash commands synced.")


@bot.event
async def on_member_join(member):
    guild = member.guild
    before = invite_cache.get(guild.id, [])
    after = await guild.invites()

    used_invite = None

    for old in before:
        for new in after:
            if old.code == new.code and old.uses < new.uses:
                used_invite = new
                break

    invite_cache[guild.id] = after

    if used_invite is None:
        print(f"Invite not found for {member} in {guild.name}")
        return

    inviter = used_invite.inviter
    invited_id = str(member.id)
    inviter_id = str(inviter.id)

    if already_invited(invited_id):
        print(f"No bonus: {member} already joined before.")
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"⚠ {inviter} did NOT get bonus. {member} already joined before.")
        return

    record_invite(invited_id, inviter_id)
    add_bonus(inviter_id, 1)
    set_wheel_time(inviter_id)

    try:
        await inviter.send(f"🎉 Someone NEW joined using your invite! You earned **+1 bonus**.")
    except:
        pass

    log_channel = guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"➕ {inviter} earned +1 bonus for inviting NEW user {member}!")
    print(f"Bonus added: {inviter} invited {member}")


bot.run(TOKEN)