from RealmOfConflict import RealmOfConflict
from discord.ext.commands import Context as DiscordContext
from discord import Interaction as DiscordInteraction
from discord import ButtonStyle as DiscordButtonStyle
from discord import SelectOption, Embed
from discord.ui import Button, Select, View, Modal, TextInput
from Panels.Panel import Panel
from Structures import ManufacturingFacility

class EditManufacturingFacilitiesPanel(Panel):
    def __init__(Self, Ether:RealmOfConflict, InitialContext:DiscordContext, ButtonStyle, Interaction:DiscordInteraction, PlayPanel, ManufacturingFacilitiesPanel, FacilitySelected):
        super().__init__(Ether, InitialContext,
                         PlayPanel, "Manufacturing Facilities",
                         Interaction=Interaction, ButtonStyle=ButtonStyle)
        Self.ManufacturingFacilitiesPanel = ManufacturingFacilitiesPanel
        Self.FacilitySelected = FacilitySelected

    async def _Construct_Panel(Self, Interaction=None):
        if type(Interaction) == tuple:
            if len(Interaction) == 2:
                Data = Interaction
                Interaction = Data[0]

        if Self.Interaction.user != Self.InitialContext.author: return

        if Interaction is not None:
            Self.BaseViewFrame = View(timeout=144000)
            Self.EmbedFrame = Embed(title=f"{Self.Player.Data['Name']}'s Manufacturing Facilities Panel")
            Self.Interaction = Interaction

        await Self._Generate_Info(Self.Ether, Self.InitialContext)
        Self.CollectButton = Button(label="Collect from Facilities", style=Self.ButtonStyle, row=0, custom_id="CollectButton")
        Self.CollectButton.callback = lambda Interaction: Self._Construct_Panel(Interaction)
        Self.BaseViewFrame.add_item(Self.CollectButton)

        Self.EmbedFrame.description += f"**{Self.Player.ManufacturingFacilities[Self.FacilitySelected].Data['Name']}**\n"
        Self.EmbedFrame.description += f"**Level:** {Self.Player.ManufacturingFacilities[Self.FacilitySelected].Data['Level']}\n"
        Self.EmbedFrame.description += f"**Recipe:** {Self.Player.ManufacturingFacilities[Self.FacilitySelected].Data['Recipe']}\n"
        
        Self.FacilityRecipeChoices = [SelectOption(label="Lorem Ipsum")]
        Self.FacilityRecipeSelection = Select(placeholder="Select a Recipe", options=Self.FacilityRecipeChoices, row=1, custom_id=f"FacilityRecipeSelection")
        if hasattr(Self, "GroupSelected"):
            Self.FacilityRecipeSelection.callback = lambda SelectInteraction: Self._Change_Recipe(SelectInteraction, FacilitySelected=SelectInteraction.data["values"][0], GroupSelected=Self.GroupSelected)
        else:
            Self.FacilityRecipeSelection.callback = lambda SelectInteraction: Self._Change_Recipe(SelectInteraction, FacilitySelected=SelectInteraction.data["values"][0])
        Self.BaseViewFrame.add_item(Self.FacilityRecipeSelection)

        Self.ChangeFacilityNameButton = Button(label="Change Facility Name", style=Self.ButtonStyle, row=0, custom_id="ChangeFacilityNameButton")
        if hasattr(Self, "GroupSelected"):
            Self.ChangeFacilityNameButton.callback = lambda Interaction: Self._Send_Change_Name_Modal((Interaction, Self.FacilitySelected, Self.GroupSelected))
        else:
            Self.ChangeFacilityNameButton.callback = lambda Interaction: Self._Send_Change_Name_Modal((Interaction, Self.FacilitySelected))
        Self.BaseViewFrame.add_item(Self.ChangeFacilityNameButton)

        Self.UpgradeFacilityButton = Button(label=f"Upgrade Facility for {Self.Player.ManufacturingFacilities[Self.FacilitySelected].Data['Upgrade Cost']:,}", style=Self.ButtonStyle, row=0, custom_id="UpgradeFacilityButton")
        Self.UpgradeFacilityButton.callback = lambda Interaction: Self._Construct_Panel(Interaction)
        Self.BaseViewFrame.add_item(Self.UpgradeFacilityButton)

        Self.ManufacturingFacilitiesButton = Button(label="Manufacturing Facilities", style=Self.ButtonStyle, row=4, custom_id="ManufacturingFacilitiesButton")
        Self.ManufacturingFacilitiesButton.callback = lambda Interaction: Self._Construct_New_Panel(Self.Ether, Self.InitialContext, Self.ButtonStyle, Interaction)
        Self.BaseViewFrame.add_item(Self.ManufacturingFacilitiesButton)

        Self.HomepageButton = Button(label="Home", style=DiscordButtonStyle.grey, row=4, custom_id="HomePageButton")
        Self.HomepageButton.callback = lambda Interaction: Self.PlayPanel._Construct_Home(Self.Ether, Self.InitialContext, Interaction)
        Self.BaseViewFrame.add_item(Self.HomepageButton)

        Self.Ether.Logger.info(f"Sent Manufacturing Facilities panel to {Self.Player.Data['Name']}")
        await Self._Send_New_Panel(Self.Interaction)


    async def _Send_Change_Name_Modal(Self, Data):
        Interaction = Data[0]
        if Interaction.user != Self.InitialContext.author:
            return
        Self.ChangeFacilityNameModal = Modal(title="Change Facility Name")
        Self.ChangeFacilityNameModal.on_submit = lambda ButtonInteraction: Self._Change_Facility_Name((ButtonInteraction,) + Data[1::])

        Self.FacilityName = TextInput(label="Enter new facility name:")
        Self.ChangeFacilityNameModal.add_item(Self.FacilityName)
        await Interaction.response.send_modal(Self.ChangeFacilityNameModal)

    
    async def _Change_Facility_Name(Self, Data):
        Interaction, FacilitySelected = Data[0], Data[1]
        if len(Data) == 3: GroupSelected = Data[2]
        Self.Player.ManufacturingFacilities[Self.FacilityName.value] = Self.Player.ManufacturingFacilities[FacilitySelected]
        Self.Player.ManufacturingFacilities.pop(FacilitySelected)
        FacilitySelected = Self.FacilityName.value
        Self.Player.ManufacturingFacilities[FacilitySelected].Data["Name"] = FacilitySelected

        if len(Data) == 2:
            await Self._Construct_Panel(Interaction=Interaction, FacilitySelected=FacilitySelected)
        else:
            await Self._Construct_Panel(Interaction=Interaction, FacilitySelected=FacilitySelected, GroupSelected=GroupSelected)


    async def _Change_Recipe(Self, Data):
        ...