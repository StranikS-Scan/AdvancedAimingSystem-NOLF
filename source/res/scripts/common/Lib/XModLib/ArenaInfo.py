# Authors: Vladislav Ignatenko <gpcracker@mail.ru>

# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ------------------- #
#    X-Mod Library    #
# ------------------- #
# nothing

# -------------------- #
#    Module Content    #
# -------------------- #
def isSquadMan(vehicleID):
	return BigWorld.player().guiSessionProvider.getCtx().isSquadMan(vehicleID)

def isTeamKiller(vehicleID):
	return BigWorld.player().guiSessionProvider.getCtx().isTeamKiller(vehicleID)

def isObserver(vehicleID):
	return BigWorld.player().guiSessionProvider.getCtx().isObserver(vehicleID)

def isAlly(vehicleID):
	return BigWorld.player().guiSessionProvider.getCtx().isAlly(vehicleID)

def isEnemy(vehicleID):
	return BigWorld.player().guiSessionProvider.getCtx().isEnemy(vehicleID)

def isAlive(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).isAlive()

def isReady(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).isReady()

def getTeam(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).team

def getPlayerName(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).player.name

def getVehicleName(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.name

def getLevel(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.level

def getClass(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.classTag

def getShortName(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleInfo(vehicleID).vehicleType.shortName

def getFrags(vehicleID):
	return BigWorld.player().guiSessionProvider.getArenaDP().getVehicleStats(vehicleID).frags

def getPlayerVehicleID():
	return BigWorld.player().guiSessionProvider.getArenaDP().getPlayerVehicleID()
