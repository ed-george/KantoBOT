import discord
from discord.ext import commands
from .utils.dataIO import fileIO
import os
import random

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
        print("-- Starting bot --")
        self.bot = bot
        self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")

    @commands.command()
    async def isAlive(self):
        """Test bot is alive!"""
        await self.bot.say("Hello World!")

    @commands.command(pass_context=True, no_pm=True)
    async def pokedex(self, ctx):
        """Pokedex"""
        user = ctx.message.author

        for result in self.dex:
            if result["id"] == user.name:
                print("Pokedex found for " + user.name)
                # TODO print pokemon
                await self.bot.say(user.mention + " already has Pokemon")
                return

        print("No Pokedex found for " + user.name)
        await create_user(self, ctx)



"""-----------------------------------------------------------------------------------------------------------------------------------
                                                      || End of Commands ||
                                                || Start of Background Check ||
-----------------------------------------------------------------------------------------------------------------------------------"""

async def create_user(self, ctx):
    print("create user")
    server = ctx.message.server
    user = ctx.message.author

    print("user " + user.name)

    # Builders the @Trainer role.
    if 'Trainer' not in [role.name for role in server.roles]:
        print("Creating Trainer role")
        try:
            perms = discord.Permissions.none()
            await self.bot.create_role(server, name="Trainer", permissions=perms)
            print("create role")
        except discord.Forbidden as e:
            print("Bot could not create Trainer role - Please check bot permissions")
            print(e)
            await self.bot.say("Something went wrong " + user.mention + " please seek admin help.")
            return

    # Gives user the trainer role. Checks to see if they already have role.
    role = discord.utils.get(ctx.message.server.roles, name="Trainer")
    if 'Trainer' not in [role.name for role in user.roles]:
        await self.bot.add_roles(user, role)
        print("add role to " + user.name)
    else:
        print("Trainer role is already assigned to " + user.name)

    # replace with give starter
    give_pokemon(self, user)
    await self.bot.say("Your new journey starts here! " + user.mention + " is now a Trainer!")


def give_starter(self, author):
    # STUB
    starter = random.choice(["1","4","7"])


def give_pokemon(self, author):
    self.dex.append({"id" : author.name, "pokemon" : dict()})
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
