import discord
from redbot.core import commands, Config, checks
import aiohttp
import asyncio
from urllib.parse import urlencode
from redbot.core.utils.menus import menu, commands, DEFAULT_CONTROLS
from aiocache import cached, SimpleMemoryCache

cache = SimpleMemoryCache()
BaseCog = getattr(commands, "Cog", object)

class Gamesearch(BaseCog):
    """Search Rawg.io for games"""

    @commands.command()
    @cached(ttl=86400, cache=SimpleMemoryCache)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def gamesearch(self, ctx, *, game):
        """Search Rawg.io for games"""

        url = "https://api.rawg.io/api/games?"+urlencode({
            "search": game,
        })

        # Queries api for a game
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                games = await response.json()
                if games == []:
                    await ctx.send("No results.")
                    return

        results = games["results"]
        embeds = []
        for game in results:
          # Build Embed
            async with aiohttp.ClientSession() as session:
               async with session.get(f"https://api.rawg.io/api/games/{game['id']}") as response:
                  game_details = await response.json()
            embed = discord.Embed()
            embed.title=f"{game['name']}"
            embed.url=f"https://rawg.io/games/{game['slug']}"
            embed.add_field(name="Release date", value=game.get('released', 'TBA'))
            if game['rating']:
               embed.add_field(name="Metacritic rating", value=game_details.get('metacritic', 'N/A'))
            if game_details['description_raw']:
               embed.description="{}".format(game_details['description_raw'][:500])
            if game['background_image'] != "N/A":
               embed.set_image(url=game['background_image'])
            embed.set_footer(text="Powered by Rawg")
            embeds.append(embed)

        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=20)
