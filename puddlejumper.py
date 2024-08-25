from optparse import Option
import discord, discord.ui, os, json
from discord import app_commands
from discord.ext import commands
from typing import Optional
from random import choice


data_dir = "data"
assets_dir = "Assets"
config_filename = os.path.join(data_dir, "config.json")
titlePhrases = [
        "Is this even randomized???",
        "I put in an order at burger king",
        "y'all want burger king?",
        "CESA Submerible launched! Godspeed",
        "Pack a back we're going to [insert archipelago here]!",
        "Increasing the entropy of the universe, please wait...",
        "..-. .. ... ....  ... --- ..- -. -.. ...",
        "win.exe.tiff.bin.tor.zip.com.tar.gz at the ready!",
        "I put your games on punchcards and shuffled them",
        "I don't think the logic is rigerous have fun!",
        "I think I dropped your item in the water...",
        "A fish ran away with your item!",
        "[Hint]: Your item was eaten by Tilemuncher (found)"
    ]

def config():
    if not os.path.exists(os.path.dirname(config_filename)):
        os.makedirs(os.path.dirname(config_filename))

    if not os.path.exists(config_filename):
        #generate default config
        config_dic = {
                "token" : "",
                "owners" : [
                    0000
                    ],
                "prefix" : ["p;", "p!"],
                "command_servers" : []
            }
        with open(config_filename, "w") as config_file:
            json.dump(config_dic, config_file, indent=4)
            print("please fill in bot token and any bot admin discord ids to the new config.json file!")
            quit()
    else:
        with open(config_filename) as config_file:
            return json.load(config_file)

class newClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        for guild_id in config()["command_servers"]:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

client = newClient(intents = discord.Intents.all())

@client.event
async def on_ready():
    print(f"logged in as {client.user} with token {config()['token']} to {len(client.guilds)} servers")
    
class GameUI(discord.ui.View):
    def __init__(self, initUserName, timeout, parentInteraction):
        super().__init__(timeout=timeout)
        
        self.players = []
        self.yaml = []
        self.message = None
        self.parentInteraction = parentInteraction
        self.owner = parentInteraction.user 
        
    @discord.ui.button(style=discord.ButtonStyle.success, label="Sign me up!")
    async def joinGame(self, interact : discord.Interaction, button : discord.ui.Button):
        user = interact.user
        if user not in self.players:
            self.players.append(user)
            await interact.response.send_message("Prepare to be randomized!", ephemeral=True)
        else:
            await interact.response.send_message("Already randomized! If I randomize you again you'll be scrongled!", ephemeral=True)
        await self.rebuildMessage()

    @discord.ui.button(style=discord.ButtonStyle.success, label="My yaml is in!")
    async def yamlCheckIn(self, interact : discord.Interaction, button : discord.ui.Button):
        user = interact.user
        if user in self.players:
            if user not in self.yaml:
                self.yaml.append(user)
                await interact.response.send_message("NYAml recorded! :3", ephemeral=True)
            else:
                await interact.response.send_message("You're already on the list!", ephemeral=True)
        else:
            await interact.response.send_message("Please sign up before you check in your yaml!", ephemeral=True)
        await self.rebuildMessage()
        
    @discord.ui.button(style=discord.ButtonStyle.red, label="I'm out!")
    async def leaveGame(self, interact : discord.Interaction, button : discord.ui.Button):
        user = interact.user
        removed = False
        if user in self.players:
            removed = True
            self.players.remove(user)
        if user in self.yaml:
            removed = True
            self.yaml.remove(user)
        if removed:
            await interact.response.send_message("You're out!", ephemeral=True)
        else:
            await interact.response.send_message("You weren't in!", ephemeral=True)
        await self.rebuildMessage()


    @discord.ui.button(style=discord.ButtonStyle.blurple, label="LETS GO!")
    async def startGame(self, interact : discord.Interaction, button : discord.ui.Button):
        user = interact.user
        if user == self.owner:
            notifString = "Game is starting! \n"
            for player in self.players:
                notifString += f"{player.mention} "
            await interact.response.send_message(notifString)
        else:
            await interact.response.send_message("Only the owner of this game can start it!", ephemeral=True)


    async def rebuildMessage(self):
        if self.message is None:
            temp = await self.parentInteraction.original_response()
            self.message = await temp.fetch()
        originalTitle = self.message.embeds[0].title
        
        yamlstring = ""
        playerString = ""

        for player in self.players:
            playerNick = player.display_name
            playerString += f"{playerNick}\n"
            if player not in self.yaml:
                yamlstring += f"{playerNick}\n"

        embedDic = {
            "title" : originalTitle,
            "color" : 5763719,
            "fields" : [
                    {
                        "name" : "Signed up:",
                        "value" : playerString
                        },
                    {
                        "name" : "Has not checked in yaml:",
                        "value" : yamlstring
                        }
                ]
        }

        await self.message.edit(embed=discord.Embed.from_dict(embedDic))
                
@client.tree.command()
@app_commands.describe(timeout="Timeout in hours. Default: 48")
async def new_archi(interaction: discord.Interaction, timeout: Optional[int] = 48):
    """Start a new game signup!"""
    #build the initial embed
    timeout = timeout * 3600
    embedDic = {
            "title" : choice(titlePhrases),
            "color" : 5763719,
            "fields" : [
                    {
                        "name" : "Signed up:",
                        "value" : ""
                        },
                    {
                        "name" : "Checked in yaml:",
                        "value" : ""
                        }
                ]
        }
    

    await interaction.response.send_message(embed=discord.Embed.from_dict(embedDic), view=GameUI(interaction.user.display_name, timeout, interaction))
    
if __name__ == "__main__":
    client.run(config()["token"])
