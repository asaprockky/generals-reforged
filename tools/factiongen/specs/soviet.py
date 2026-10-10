"""Soviet Union (WWII Red Army). Placeholder art: cloned from China.

This is the minimal pipeline test (core economy and two units); the full roster is added on top.
"""

SIDE = "Soviet"

# Retail names used inside cloned blocks -> our names (prerequisites, spawned objects ...).
TOKENS = {
    "ChinaCommandCenter": "Sov_CommandCenter",
    "ChinaVehicleDozer": "Sov_Dozer",
    "ChinaPowerPlant": "Sov_PowerPlant",
    "ChinaBarracks": "Sov_Barracks",
    "ChinaSupplyCenter": "Sov_SupplyCenter",
    "ChinaWarFactory": "Sov_WarFactory",
    "ChinaVehicleSupplyTruck": "Sov_SupplyTruck",
}

FACTION = dict(
    display="Soviet Union",
    template_clone="FactionChina",
    base_side="China",
    color="R:180 G:0 B:0",
    command_center="Sov_CommandCenter",
    dozer="Sov_Dozer",
)

BLOCKS = [
    # ---------------------------------------------------------------- buildings
    dict(name="Sov_CommandCenter", clone="ChinaCommandCenter", display="Soviet Headquarters",
         command_set="Sov_CommandCenterCommandSet",
         button=dict(type="DOZER_CONSTRUCT", label="&Headquarters", tooltip="Command center. Builds construction vehicles.")),
    dict(name="Sov_PowerPlant", clone="ChinaPowerPlant", display="Power Station",
         command_set="Sov_PowerPlantCommandSet",
         button=dict(type="DOZER_CONSTRUCT", label="&Power Station", tooltip="Provides power to the base.")),
    dict(name="Sov_Barracks", clone="ChinaBarracks", display="Barracks",
         command_set="Sov_BarracksCommandSet",
         button=dict(type="DOZER_CONSTRUCT", label="&Barracks", tooltip="Trains Red Army infantry.")),
    dict(name="Sov_SupplyCenter", clone="ChinaSupplyCenter", display="Supply Depot",
         command_set="Sov_SupplyCenterCommandSet",
         button=dict(type="DOZER_CONSTRUCT", label="&Supply Depot", tooltip="Receives supplies. Builds supply trucks.")),
    dict(name="Sov_WarFactory", clone="ChinaWarFactory", display="Tank Factory",
         command_set="Sov_WarFactoryCommandSet",
         button=dict(type="DOZER_CONSTRUCT", label="&Tank Factory", tooltip="Builds Soviet armour.")),
    # ---------------------------------------------------------------- units
    dict(name="Sov_Dozer", clone="ChinaVehicleDozer", display="Construction Truck",
         command_set="Sov_DozerCommandSet",
         button=dict(type="UNIT_BUILD", label="&Construction Truck", tooltip="Builds and repairs structures.")),
    dict(name="Sov_SupplyTruck", clone="ChinaVehicleSupplyTruck", display="Supply Truck",
         button=dict(type="UNIT_BUILD", label="Supply &Truck", tooltip="Gathers supplies.")),
    dict(name="Sov_Conscript", clone="ChinaInfantryRedguard", display="Conscript",
         set=dict(BuildCost=200),
         prerequisites=["Object = Sov_Barracks"],
         button=dict(type="UNIT_BUILD", label="&Conscript", tooltip="Cheap rifle infantry. Strength in numbers.")),
    dict(name="Sov_T34", clone="ChinaTankBattleMaster", display="T-34/85",
         set=dict(BuildCost=700),
         prerequisites=["Object = Sov_WarFactory"],
         button=dict(type="UNIT_BUILD", label="T-&34", tooltip="Reliable medium tank.")),
]

COMMAND_SETS = {
    "Sov_DozerCommandSet": {1: "Command_ConstructSov_PowerPlant", 3: "Command_ConstructSov_Barracks",
                            5: "Command_ConstructSov_SupplyCenter", 11: "Command_ConstructSov_WarFactory",
                            12: "Command_ConstructSov_CommandCenter", 14: "Command_DisarmMinesAtPosition"},
    "Sov_CommandCenterCommandSet": {1: "Command_ConstructSov_Dozer", 13: "Command_SetRallyPoint", 14: "Command_Sell"},
    "Sov_PowerPlantCommandSet": {14: "Command_Sell"},
    "Sov_BarracksCommandSet": {1: "Command_ConstructSov_Conscript", 13: "Command_SetRallyPoint", 14: "Command_Sell"},
    "Sov_SupplyCenterCommandSet": {1: "Command_ConstructSov_SupplyTruck", 13: "Command_SetRallyPoint", 14: "Command_Sell"},
    "Sov_WarFactoryCommandSet": {1: "Command_ConstructSov_T34", 13: "Command_SetRallyPoint", 14: "Command_Sell"},
}
