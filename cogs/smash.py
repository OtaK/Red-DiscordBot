import discord
from discord.ext import commands
from cogs.utils import checks
from __main__ import set_cog, send_cmd_help, settings
import urllib
import aiohttp
import asyncio
import logging

class Smash:
    """Smash

    Make some salt by calling upon the ranking gods"""

    def __init__(self, bot):
        self.bot = bot

    async def _rankplayer(self, player):
        url = "http://smashstats.otak-arts.com/1.0/melee/player/" + urllib.parse.quote(player);
        try:
            async with aiohttp.get(url) as r:
                return await r.json()
        except:
            return "error"
        return "error"

    async def _rankpvp(self, p1, p2):
        url = "http://smashstats.otak-arts.com/1.0/melee/player/" + urllib.parse.quote(p1) + "/vs/" + urllib.parse.quote(p2);
        try:
            async with aiohttp.get(url) as r:
                return await r.json()
        except:
            return "error"
        return "error"

    @commands.command(pass_context=True, no_pm=False)
    async def rank(self, ctx, *input):
        """Check your ranking details"""
        player = " ".join(input)

        data = await self._rankplayer(player)
        if data is "error":
            await self.bot.say("Player not found!")
        else:
            ranktext = data["info"]["tag"]
            if len(data["info"]["realname"]) > 0:
                ranktext += " AKA " + data["info"]["realname"]
            if len(data["info"]["country"]) > 0:
                ranktext += " [" + data["info"]["country"] + "]"

            if len(data["info"]["mains"]) > 0 and data["info"]["mains"][0] is not None:
                ranktext += "\nPlays" + ', '.join(data["info"]["mains"])
            else:
                ranktext += "\nUnknown main(s)"

            ranktext += "\n" + str(data["skill"]["record"]["tournaments"]) + " [" + str(data["skill"]["record"]["wins"]) + "W / " + str(data["skill"]["record"]["losses"]) + "L - " + str(data["skill"]["win_percentage"]) + "% win] \n"
            rank_parts = []
            if data["skill"]["eu_rank"]:
                rank_parts.append("Ranked " + str(data["skill"]["eu_rank"]) + " EU")
            if data["skill"]["country_rank"]:
                rank_parts.append("Ranked " + str(data["skill"]["country_rank"]) + " " + data["info"]["country"])
            if data["skill"]["character_rank"]:
                rank_parts.append("Ranked " + str(data["skill"]["character_rank"]) + " for " + data["info"]["mains"][0])

            ranktext += '\n'.join(rank_parts)
            await self.bot.say(ranktext)

    @commands.command(pass_context=True, no_pm=False)
    async def pvp(self, ctx, *input):
        """Check the pvp record between two players"""
        player1, player2 = " ".join(input).split(';')

        data = await self._rankpvp(player1, player2)
        if data is "error":
            await self.bot.say("Player(s) not found!")

        pvptext = ""
        if len(data["matches"]) > 0:
            pvptext += player1 + " " + str(data[player1]["wins"]) + " - " + str(data[player2]["wins"]) + " " + player2
            matches_parts = [m["winner"] + " won at " + m["round"] + " of " + m["tournament"] for m in data["matches"]]
            pvptext += "\n" + '\n'.join(matches_parts)
        else:
            pvptext += "Those players never played against each other yet!"

        await self.bot.say(pvptext)

def setup(bot):
    logger = logging.getLogger('aiohttp.client')
    logger.setLevel(50)
    bot.add_cog(Smash(bot))
