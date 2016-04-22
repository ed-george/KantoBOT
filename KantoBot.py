import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from time import ctime, time
import os
import random
import asyncio

"""------------------------------------------------------------------------------------------------------------------
                                                          ||Store Data||
---------------------------------------------------------------------------------------------------------------------"""

DATA_FILE_PATH = "data/kantobot/"
PC_FILE = "pc.json"
POKEMON_FILE = "pokemon.json"
BASE_ROLE_NAME = "Trainer"
LOOT_COOL_OFF_HRS = 24

# Constants
HOUR_MILI = 3600

"""------------------------------------------------------------------------------------------------------------------
                                              || Start Creating Commands for the Bot ||
---------------------------------------------------------------------------------------------------------------------"""

class Kanto:

    """
    Lets you catch random pokemon utilizing the economy cog.
    Goal is to complete the PokeDex
    You can purchase Pokeballs
    """
  
    def __init__(self, bot):
        print("-- Starting kanto @ " + ctime() + " --")
        self.bot = bot
        self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")
        self.pokemon = fileIO(DATA_FILE_PATH + POKEMON_FILE, "load")

    @commands.command()
    async def isalive(self):
        """Test bot is alive!"""
        await self.bot.say("Hello World!")

    @commands.command(pass_context=True, no_pm=False)
    async def pokedex(self, ctx):
        """Pokedex"""
        user = ctx.message.author
        dex_user = get_dex_user(self, user)

        if dex_user is not None:
            poke_list = ""
            for pokemon in dex_user["pokemon"]:
                poke_list += get_pokemon(self, pokemon)["name"]
                poke_list += " "
            await self.bot.say(user.mention + " is travelling with " + poke_list)
            return

        print("No Pokedex found for " + user.name)
        await create_user(self, ctx)

    @commands.command(pass_context=True, no_pm=False)
    async def pokeloot(self, ctx):
        """Pokeloot"""
        user = ctx.message.author
        if not is_user_base_role(user):
            await self.bot.say(user.mention + " you don't seem to be a Trainer yet!")
            return
        dex_user = get_dex_user(self, user)
        if can_claim_loot(dex_user):
            # claim_loot(dex_user)
            print(user.name + " can claim loot")
        else:
            await self.bot.say(user.mention + " you cannot claim your loot yet!")

"""------------------------------------------------------------------------------------------------------------------
                                                      || End of Commands ||
                                                || Start of Background Check ||
---------------------------------------------------------------------------------------------------------------------"""

async def create_user(self, ctx):
    """
    Creates a user record in the user information, assigning them the base role.
    Also assigns this new user a starter pokemon
    :param ctx: Context of call
    :return:
    """
    server = ctx.message.server
    user = ctx.message.author

    print("Creating kantobot info for user " + user.name)

    # Create the base trainer role iff it doesn't exist
    if BASE_ROLE_NAME not in [role.name for role in server.roles]:
        print("No base role found. Creating channel wide role - " + BASE_ROLE_NAME)
        try:
            # Create role - No permissions required
            perms = discord.Permissions.none()
            await self.bot.create_role(server, name=BASE_ROLE_NAME, permissions=perms)
            print(BASE_ROLE_NAME + " role created")
            await asyncio.sleep(1)
        except discord.Forbidden as e:
            # This exception can occur when the bot account does not have the relevant permissions
            print("Bot could not create " + BASE_ROLE_NAME + " role - Have you checked bot permissions?")
            print(e)
            await self.bot.say("Something went wrong " + user.mention + " please seek admin help.")
            return

    if is_user_base_role(user):
        # User already has role
        print(BASE_ROLE_NAME + " role is already assigned to " + user.name)
    else:
        # Add role to user
        # Gives user the Trainer role. Checks to see if they already have role.
        timeout_role = discord.utils.get(ctx.message.server.roles, name=BASE_ROLE_NAME)
        await self.bot.add_roles(user, timeout_role)
        print("Gave " + BASE_ROLE_NAME + " role to " + user.name)

    # Gives user random starter Pokemon
    starter = receive_starter(self, user)
    await self.bot.say("Your new journey starts here! " + user.mention +
                       " is now a Trainer with their first trusty partner " + starter + "!")


def get_pokemon(self, number):
    """
    Get pokemon by dex number string identifier
    :param number: String representing pokemon id e.g. "151"
    :return: Pokemon dict object
    """
    # Check if Pokemon exists in dex
    if number in self.pokemon:
        return self.pokemon[number]
    else:
        # Something went wrong - assign user a 'MissingNo.'
        print("ERROR: No Pokemon found for number: " + number)
        return self.pokemon["000"]


def receive_starter(self, user):
    """
    Assigns a user one of 4 starter Pokemon
    The Gen I default starters are ids 001, 004, 007 and 025
    :param user: The user to receive the starter
    :return: The starter's name
    """
    # Get random choice from the starters
    starter = random.choice(["001", "004", "007", "025"])
    pokemon = get_pokemon(self, starter)
    # Save starter to file
    self.dex.append({"id": user.name,
                     "pokemon": [starter],
                     "inventory": create_inventory(),
                     "loot": create_loot()}
    )
    fileIO(DATA_FILE_PATH + PC_FILE, "save", self.dex)
    # Reload new dex to memory
    self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")
    # Return the starter name for prompt
    name = pokemon["name"]
    print("Assigned " + name + " as " + user.name + "'s starter")
    return name


def create_inventory():
    """
    Create inventory
    :return: Default inventory for users
    """
    return {"pokeball": 0, "greatball": 0, "ultraball": 0}

def create_loot():
    """
    Create loot collection information
    :return: Default loot status for users
    """
    return {"loot_count": 0, "last_collected": 0}

def get_dex_user(self, user):
    """
    Retrieves user information from info stored in memory
    :param user: User to get information on
    :return: The user's information if available, None otherwise
    """
    for dex_user in self.dex:
        if dex_user["id"] == user.name:
            return dex_user
    return None

def is_user_base_role(user):
    """
    Determins if a user has the base roll assigned to them
    :param user: User to test for role
    :return: true if role is assigned to user, false otherwise
    """
    return BASE_ROLE_NAME in [role.name for role in user.roles]

def give_pokemon(self, user, number):
    """
    Adds a Pokemon to a user's party
    :param user: The user to add the Pokemon too
    :param number: The string dex identifier of the Pokemon to add
    :return:
    """
    # Get user info
    dex_user = get_dex_user(self, user)
    # Printing for debug purposes - TODO Remove
    print("Giving pokemon to " + user.name)
    print(get_pokemon(self, number))
    # Add Pokemon to user
    dex_user["pokemon"].append(number)
    # Save user information
    print("Saving pokemon to user")
    fileIO(DATA_FILE_PATH + PC_FILE, "save", self.dex)
    # Reload information to memory
    self.dex = fileIO(DATA_FILE_PATH + PC_FILE, "load")

def can_claim_loot(dex_user):
    """
    Check if loot can be claimed by user
    :param dex_user: The user stored in memory
    :return: true if claim is made after cool off period, false otherwise
    """
    now = int(time())
    return (now - dex_user["loot"]["last_collected"]) >= int(LOOT_COOL_OFF_HRS * HOUR_MILI)

def check_folders():
    """
    Checks if data folders are created.
    If not, the folder is created
    :return:
    """
    if not os.path.exists(DATA_FILE_PATH):
        print("Creating " + DATA_FILE_PATH + " folder...")
        os.makedirs(DATA_FILE_PATH)

def check_files():
    """
    Checks if data file are created.
    If not, the files are created and populated with relevant base data
    :return:
    """
    # Check User storage file
    f = DATA_FILE_PATH + PC_FILE
    if not fileIO(f, "check"):
        print("Creating empty " + PC_FILE)
        fileIO(f, "save", [])
    # Check Pokemon JSON
    f = DATA_FILE_PATH + POKEMON_FILE
    if not fileIO(f, "check"):
        print("WARNING: Empty " + f)
        print("WARNING: Please download a relevant Pokemon JSON file")
        fileIO(f, "save", [])

def setup(bot):
    """
    Set up of bot
    :param bot: Red Bot instance
    :return:
    """
    check_folders()
    check_files()
    bot.add_cog(Kanto(bot))
