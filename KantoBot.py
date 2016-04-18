import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os

"""-----------------------------------------------------------------------------------------------------------------------------------
                                                          ||Store Data||
-----------------------------------------------------------------------------------------------------------------------------------"""

DATA_FILE_PATH = "data/kantobot/"
PC_FILE = "pc.json"

"""-----------------------------------------------------------------------------------------------------------------------------------
                                              || Start Creating Commands for the Bot ||
-----------------------------------------------------------------------------------------------------------------------------------"""

class Kanto:
    """
    Lets you catch random pokemon utilizing the economy cog.
    Goal is to complete the PokeDex
    You can purchase Pokeballs
    """
  
    def __init__(self, bot):
        self.bot = bot
        self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")

    @commands.command()
    async def isAlive(self):
        """Test bot is alive!"""
        await self.bot.say("Hello World!")

    @commands.command(pass_context=True)
    async def pokedex(self, ctx):
        """Pokedex"""
        author = ctx.message.author

        for result in self.dex:
            if result["id"] == author.name:
                print("Pokedex found for " + author.name)
                await self.bot.say(author.mention + " already has the Pokemon " + result["pokemon"])
                return

        print("No Pokedex found for " + author.name)
        give_pokemon(self, author)
        await self.bot.say("Your new journey starts here! " + author.mention + " is now a Trainer!")


    

"""-----------------------------------------------------------------------------------------------------------------------------------
                                                      || End of Commands ||
                                                || Start of Background Check ||
-----------------------------------------------------------------------------------------------------------------------------------"""

def give_pokemon(self, author):
    self.dex.append({"id" : author.name, "pokemon" : "derp"})
    fileIO(DATA_FILE_PATH + PC_FILE, "save", self.dex)
    self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")

def check_folders():
    if not os.path.exists(DATA_FILE_PATH):
        print("Creating " + DATA_FILE_PATH + " folder...")
        os.makedirs(DATA_FILE_PATH)

def check_files():
    f = DATA_FILE_PATH + PC_FILE
    if not fileIO(f, "check"):
        print("Creating empty " + PC_FILE + "...")
        fileIO(f, "save", [])

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Kanto(bot))
