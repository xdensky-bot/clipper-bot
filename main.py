import os
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Bot online sebagai {client.user}")


@tree.command(
    name="campaigns",
    description="Menampilkan Campaign Radar"
)
async def campaigns(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔥 CAMPAIGN RADAR",
        description="Clipper Bot V0.1",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="#1 🎬 Demo Entertainment",
        value=(
            "**Score:** 94/100\n"
            "💰 Rp5.000 / 1K views\n"
            "👁️ Min: 50K views\n"
            "📱 TikTok\n"
            "💵 Budget: Rp18.000.000"
        ),
        inline=False
    )

    embed.add_field(
        name="#2 🎵 Demo Music",
        value=(
            "**Score:** 88/100\n"
            "💰 Rp2.000 / 1K views\n"
            "👁️ Min: 20K views\n"
            "📱 TikTok\n"
            "💵 Budget: Rp12.000.000"
        ),
        inline=False
    )

    embed.set_footer(
        text="V0.1 • Campaign Radar"
    )

    await interaction.response.send_message(embed=embed)


@tree.command(
    name="detail",
    description="Melihat detail campaign"
)
async def detail(
    interaction: discord.Interaction,
    campaign: str
):

    embed = discord.Embed(
        title=f"🎬 {campaign}",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎯 Opportunity Score",
        value="94/100",
        inline=True
    )

    embed.add_field(
        name="💰 Payment",
        value="Rp5.000 / 1K views",
        inline=True
    )

    embed.add_field(
        name="📱 Platform",
        value="TikTok",
        inline=True
    )

    embed.add_field(
        name="👁️ View Requirement",
        value="50K – 2M",
        inline=True
    )

    embed.add_field(
        name="📦 Resources",
        value="Campaign Brief\nSumber Bahan",
        inline=True
    )

    embed.add_field(
        name="🛡️ Status",
        value="Ready for analysis",
        inline=True
    )

    await interaction.response.send_message(embed=embed)


@tree.command(
    name="score",
    description="Melihat opportunity score campaign"
)
async def score(
    interaction: discord.Interaction,
    campaign: str
):

    await interaction.response.send_message(
        f"🎯 **{campaign}**\n\n"
        f"Opportunity Score: **94/100**\n\n"
        f"💰 Reward: 92/100\n"
        f"💵 Budget: 90/100\n"
        f"📱 Platform Fit: 100/100\n"
        f"🎬 Difficulty: 85/100"
    )


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN belum diatur."
    )

client.run(TOKEN)
