#Don't touch
import discord
from discord import app_commands
from database import *
from utils import weighted_choice
from config import LOG_CHANNEL_ID
import time

WHEEL_PRIZES = [
    ("حظ اوفر", 75),  # المحاولة من جديد
    ("اعلان عن طريق البوت مجانا", 5),
    ("اعلان عن طريق everyone", 5),
    ("اعلان بالاتنين", 5),
    ("رتبه عاليه", 5),
]

async def register_commands(bot):

    @bot.tree.command(name="bonus", description="Check your bonus balance")
    async def bonus_cmd(interaction: discord.Interaction):
        bal = get_bonus(str(interaction.user.id))
        await interaction.response.send_message(f"💰 You have **{bal} bonus**.", ephemeral=True)


    @bot.tree.command(name="leaderboard", description="Top users with bonus")
    async def leaderboard(interaction: discord.Interaction):
        cursor.execute("SELECT user_id, bonus FROM users ORDER BY bonus DESC LIMIT 10")
        rows = cursor.fetchall()

        embed = discord.Embed(title="🏆 Bonus Leaderboard", color=discord.Color.gold())

        i = 1
        for user_id, bonus in rows:
            user = interaction.guild.get_member(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            embed.add_field(name=f"#{i} — {name}", value=f"Bonus: {bonus}", inline=False)
            i += 1

        await interaction.response.send_message(embed=embed)


    @bot.tree.command(name="wheel", description="Spin the wheel using 1 bonus")
    async def wheel(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        bonus = get_bonus(user_id)

        if bonus < 1:
            await interaction.response.send_message("❌ You need at least 1 bonus to spin the wheel.", ephemeral=True)
            return

        cooldown = 300  # هنا الوقت بتقدر تعدله 
        last_time = get_wheel_time(user_id)
        now = int(time.time())

        if now - last_time < cooldown:
            remaining = cooldown - (now - last_time)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await interaction.response.send_message(
                f"⏳ You must wait **{hours}h {minutes}m** before spinning again.",
                ephemeral=True
            )
            return

        # عدد البونصات
        set_bonus(user_id, bonus - 1)

        prize = weighted_choice(WHEEL_PRIZES)
        set_wheel_time(user_id)

        if prize == "حظ اوفر":
            await interaction.response.send_message("🎡 حظ اوفر! حاول مرة أخرى.", ephemeral=False)
            return

        
        add_bonus(user_id, 1)

        await interaction.response.send_message(f"🎉 مبروك! لقد ربحت: **{prize}** 🎉")

        
        guild = interaction.guild
        win_role_id = get_win_role(str(guild.id))

        if win_role_id:
            role = guild.get_role(win_role_id)
            if role:
                log_channel = guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"{role.mention} 🎉 {interaction.user.mention} فاز بـ **{prize}**!")


    @bot.tree.command(name="set-role", description="Set the role to mention when someone wins in the log channel")
    @app_commands.describe(role="Role to mention")
    async def set_role(interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permission to use this command.", ephemeral=True)
            return

        set_win_role(str(interaction.guild.id), role.id)
        await interaction.response.send_message(f"✔ تم تعيين {role.mention} كالدور للمنشن في سجل الفوز.")


    @bot.tree.command(name="addbonus", description="Admin: Add bonus to a user")
    @app_commands.describe(user="User", amount="Amount")
    async def addbonus(interaction: discord.Interaction, user: discord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

        add_bonus(str(user.id), amount)
        await interaction.response.send_message(f"✔ Added **{amount} bonus** to {user.mention}")


    @bot.tree.command(name="setbonus", description="Admin: Set bonus for a user")
    @app_commands.describe(user="User", amount="Amount")
    async def setbonus(interaction: discord.Interaction, user: discord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

        set_bonus(str(user.id), amount)
        await interaction.response.send_message(f"✔ Set {user.mention} bonus to **{amount}**")


    @bot.tree.command(name="resetbonus", description="Admin: Reset user's bonus")
    @app_commands.describe(user="User")
    async def resetbonus(interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Admin only.", ephemeral=True)

        set_bonus(str(user.id), 0)

        await interaction.response.send_message(f"✔ Reset {user.mention}'s bonus.")
