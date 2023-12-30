from asyncio import create_task
from discord import ButtonStyle, Embed, SelectOption
from discord import Interaction as DiscordInteraction
from discord import Message as DiscordMessage
from discord.ext.commands import Context as DiscordContext
from discord.ui import View, Button, Select, Modal, TextInput
from Structures import ProductionFacility
from os import remove
from os.path import join
from Player import Player
from random import randrange
from RealmOfConflict import RealmOfConflict
from Tables import ScavengeTable, MaterialTable, InfantryTable, InfantryToObject
from time import time
from Panels.Panel import Panel
from Panels.Facilities import FacilitiesPanel
from Panels.Avargo import AvargoPanel
from Panels.Sentents import SententPanel
from Panels.Inventory import InventoryPanel
from Panels.Profile import ProfilePanel


class PlayPanel(Panel):
    def __init__(Self, Ether:RealmOfConflict, PlayerContext:DiscordContext):
        super().__init__()
        create_task(Self._Construct_Home(Ether, PlayerContext))


    async def _Determine_Team(Self, InitialContext):
        if "Titan" in str(InitialContext.author.roles):
            Self.ButtonStyle = ButtonStyle.red
        elif "Analis" in str(InitialContext.author.roles):
            Self.ButtonStyle = ButtonStyle.blurple
        else:
            Self.ButtonStyle = ButtonStyle.grey


    async def _Construct_Home(Self, Ether:RealmOfConflict, InitialContext:DiscordContext, Interaction:DiscordInteraction=None):
        Ether:RealmOfConflict = Ether
        Whitelist:[int] = [897410636819083304, # Robert Reynolds, Cavan
        ]
        Self.MaterialChosen = None
        Self.InfantrySelected = None
        Self.ReceiptString = ""
        Self.Receipt:{str:int} = {}
        await Self._Determine_Team(InitialContext)

        if Ether.Data["Players"][InitialContext.author.id].Data["Experience"] >= Ether.Data["Players"][InitialContext.author.id].ExperienceForNextLevel:
            Ether.Data["Players"][InitialContext.author.id].Data["Level"] += 1
            Ether.Data["Players"][InitialContext.author.id].Refresh_Stats()

        Self.BaseViewFrame = View(timeout=144000)
        Self.EmbedFrame = Embed(title=f"{Ether.Data['Players'][InitialContext.author.id].Data['Name']}'s Home Panel")

        await Self._Generate_Info(Ether, InitialContext, )

        Self.ScavengeButton = Button(label="Scavenge", style=Self.ButtonStyle, custom_id="ScavengeButton")
        Self.ScavengeButton.callback = lambda Interaction: Self._Scavenge(Ether, InitialContext, Interaction)
        Self.BaseViewFrame.add_item(Self.ScavengeButton)

        Self.FacilitiesButton = Button(label="Facilities", style=Self.ButtonStyle, custom_id="FacilitiesButton")
        Self.FacilitiesButton.callback = lambda Interaction: Self._Construct_New_Panel(Ether, InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.FacilitiesButton)

        Self.AvargoButton = Button(label="Avargo", style=Self.ButtonStyle, custom_id="AvargoButton")
        Self.AvargoButton.callback = lambda Interaction: Self._Construct_New_Panel(Ether, InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.AvargoButton)

        Self.SententsButton = Button(label="Sentents", style=Self.ButtonStyle, custom_id="SententsButton")
        Self.SententsButton.callback = lambda Interaction: Self._Construct_New_Panel(Ether, InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.SententsButton)

        Self.InventoryButton = Button(label="Inventory", style=Self.ButtonStyle, custom_id="InventoryButton")
        Self.InventoryButton.callback = lambda Interaction: Self._Construct_New_Panel(Ether, InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.InventoryButton)

        Self.ProfileButton = Button(label="Profile", style=Self.ButtonStyle, custom_id="ProfileButton")
        Self.ProfileButton.callback = lambda Interaction: Self._Construct_New_Panel(Ether, InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.ProfileButton)

        if InitialContext.author.id in Whitelist:
            Self.DebugButton = Button(label="Debug", style=ButtonStyle.grey, row=3)
            Self.DebugButton.callback = Self._Construct_Debug_Panel
            Self.BaseViewFrame.add_item(Self.DebugButton)


        if Interaction:
            if Interaction.user != InitialContext.author:
                return
            await Self._Send_New_Panel(Interaction)
        else:
            Self.DashboardMessage:DiscordMessage = await InitialContext.send(embed=Self.EmbedFrame, view=Self.BaseViewFrame)

        
    async def _Construct_New_Panel(Self, Ether:RealmOfConflict, InitialContext:DiscordContext, ButtonStyle, Interaction:DiscordInteraction):
        Mapping:{str:Panel} = {
            "FacilitiesButton":FacilitiesPanel,
            "AvargoButton":AvargoPanel,
            "SententsButton":SententPanel,
            "InventoryButton":InventoryPanel,
            "ProfileButton":ProfilePanel,
        }
        Ether.Data["Panels"][InitialContext.author.id] = Mapping[Interaction.data["custom_id"]](Ether, InitialContext, ButtonStyle, Interaction, Self)


    async def _Construct_Debug_Panel(Self, Ether, InitialContext, Interaction):
        if Interaction.user != Self.InitialContext.author:
            return
        Self.BaseViewFrame = View(timeout=144000)
        Self.EmbedFrame = Embed(title=f"{Ether.Data['Players'][InitialContext.author.id].Data['Name']}'s Debug Panel")

        await Self._Generate_Info()

        Self.ResetPlayer = Button(label="Reset Player", style=Self.ButtonStyle, custom_id="ResetPlayerButton")
        Self.ResetPlayer.callback = lambda Interaction: Interaction.response.send_modal(Self.PlayerUUIDSubmission)
        Self.BaseViewFrame.add_item(Self.ResetPlayer)

        Self.HomepageButton = Button(label="Home", style=ButtonStyle.grey, row=3, custom_id="HomePageButton")
        Self.HomepageButton.callback = lambda Interaction: Self._Construct_Home(Interaction=Interaction)
        Self.BaseViewFrame.add_item(Self.HomepageButton)


        Self.PlayerUUIDSubmission = Modal(title="Submit Player UUID")
        Self.PlayerUUIDSubmission.on_submit = lambda Interaction: Self._Reset_Player(Interaction, int(Self.PlayerSubmittedUUID.value))
        Self.PlayerSubmittedUUID = TextInput(label="Player UUID") 
        Self.PlayerUUIDSubmission.add_item(Self.PlayerSubmittedUUID)


        await Self._Send_New_Panel(Interaction)


    async def _Reset_Player(Self, Ether, InitialContext, Interaction, SubmittedUUID):
        if Interaction.user != Self.InitialContext.author:
            return
        if Ether.Data["Players"][InitialContext.author.id].Data["Team"] == "Analis":
            await Self.Ether.Data["Players"][SubmittedUUID].Data["Member Object"].remove_roles(Self.Ether.Roles["Analis"])
        if Ether.Data["Players"][InitialContext.author.id].Data["Team"] == "Titan":
            await Self.Ether.Data["Players"][SubmittedUUID].Data["Member Object"].remove_roles(Self.Ether.Roles["Titan"])
        Self.Ether.Data["Players"][SubmittedUUID] = None
        Self.Ether.Data["Players"].pop(SubmittedUUID)
        remove(join("Data", "PlayerData", f"{SubmittedUUID}.roc"))
        remove(join("Data", "PlayerInventories", f"{SubmittedUUID}.roc"))
        remove(join("Data", "PlayerProductionFacilities", f"{SubmittedUUID}.roc"))

        await Self._Send_New_Panel(Interaction)
        

    async def _Scavenge(Self, Ether, InitialContext, Interaction:DiscordInteraction):
        if Interaction.user != InitialContext.author:
            return
        SuccessfulRolls:[str] = [Name for Name, Chance in ScavengeTable.items() if randrange(0 , 99) < Chance]
        Self.EmbedFrame.clear_fields()
        ScavengedString = ""
        ExperienceGained:float = round((0.65 * (0.35 * Ether.Data["Players"][InitialContext.author.id].Data["Level"])) * len(SuccessfulRolls), 2)
        ScavengedString += f"Gained {ExperienceGained} experience\n"
        Ether.Data["Players"][InitialContext.author.id].Data["Experience"] = round(Ether.Data["Players"][InitialContext.author.id].Data["Experience"] + ExperienceGained, 2)

        for Roll in SuccessfulRolls:
            if Roll == "Wallet":
                MoneyScavenged = round(2.76 * (0.35 * Ether.Data["Players"][InitialContext.author.id].Data["Level"]), 2)
                Ether.Data["Players"][InitialContext.author.id].Data["Wallet"] = round(Ether.Data["Players"][InitialContext.author.id].Data["Wallet"] + MoneyScavenged, 2)
                ScavengedString += f"Found ${MoneyScavenged}\n"
            if Roll == "Material" or Roll == "Bonus Material":
                MaterialScavenged = list(MaterialTable.keys())[randrange(0, (len(MaterialTable.keys()) - 1))]
                Start, End = MaterialTable[MaterialScavenged][0], MaterialTable[MaterialScavenged][1]
                MaterialScavengedAmount = randrange(Start, End)
                Ether.Data["Players"][InitialContext.author.id].Inventory[MaterialScavenged] = round(Ether.Data["Players"][InitialContext.author.id].Inventory[MaterialScavenged] + MaterialScavengedAmount, 2)
                ScavengedString += f"Found {MaterialScavengedAmount} {MaterialScavenged}\n"

        if Ether.Data["Players"][InitialContext.author.id].Data["Experience"] >= Ether.Data["Players"][InitialContext.author.id].ExperienceForNextLevel:
            Ether.Data["Players"][InitialContext.author.id].Data["Level"] += 1
            Ether.Data["Players"][InitialContext.author.id].Refresh_Stats()
            Self.EmbedFrame.insert_field_at(0, name=f"You leveled up!", value="\u200b", inline=False)
            
        await Self._Generate_Info(Ether, InitialContext)
        Self.EmbedFrame.add_field(name=f"Scavenged", value=ScavengedString, inline=False)
        await Self._Send_New_Panel(Interaction)