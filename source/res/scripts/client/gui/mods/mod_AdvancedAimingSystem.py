__application__ = ('Advanced Aiming System Mod [NOLF]', 'AdvancedAimingSystem_NOLF', 'GPCracker.AdvancedAimingSystem.NOLF')
__official_topic__ = 'http://www.koreanrandom.com/forum/topic/16559-/'
__authors__ = ('GPCracker', )
__bugfixes__ = ('Tempora', )
__version__ = ('v0.2.18', None)
__xmodlib__ = ('v0.1.18', None)
__client__ = (('ru', ), '1.6.0.0')

# ---------------------- #
#    Application info    #
# ---------------------- #
if __name__ == '__main__':
	appinfo = '{appname} ({appid}) {version} ({client} {clusters}) by {authors}'.format(
		appname = __application__[0],
		appid = __application__[2],
		version = __version__[0],
		client = __client__[1],
		clusters = ', '.join(__client__[0]).upper(),
		authors = ', '.join(__authors__)
	)
	import sys, time
	print >> sys.stdout, appinfo
	time.sleep(len(appinfo) * 0.05)
	sys.exit(0)

# -------------------------------------- #
#    X-Mod Library compatibility test    #
# -------------------------------------- #
import XModLib
if not XModLib.isCompatibleLibVersion(__xmodlib__):
	raise ImportError('XModLib version does not suit this version of application')
# ------------ #
#    Python    #
# ------------ #
import os
import sys
import enum
import math
import time
import marshal
import weakref
import zipfile
import operator
import functools
import itertools
import collections

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import constants
import aih_constants
import gui.shared.personality
import AvatarInputHandler.cameras
import AvatarInputHandler.aih_global_binding

# -------------------- #
#    WoT Client GUI    #
# -------------------- #
import gui.shared
import gui.shared.events
import gui.app_loader.settings
import gui.Scaleform.framework.package_layout

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import Avatar
import Account
import Vehicle
import AvatarInputHandler
import AvatarInputHandler.control_modes
import AvatarInputHandler.DynamicCameras.StrategicCamera
import AvatarInputHandler.AimingSystems.StrategicAimingSystem

# -------------------------- #
#    WoT Client GUI Hooks    #
# -------------------------- #
import gui.Scaleform.battle_entry
import gui.Scaleform.daapi.view.battle.shared
import gameplay.delegator

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.ArenaInfo
import XModLib.HookUtils
import XModLib.MathUtils
import XModLib.TextUtils
import XModLib.ClientUtils
import XModLib.EngineUtils
import XModLib.VehicleInfo
import XModLib.VehicleMath
import XModLib.VehicleBounds
import XModLib.CallbackUtils
import XModLib.KeyboardUtils
import XModLib.BallisticsMath
import XModLib.ClientMessages
import XModLib.CollisionUtils
import XModLib.IngameSettings
import XModLib.TargetScanners
import XModLib.XMLConfigReader

# ----------------------- #
#    X-Mod GUI Library    #
# ----------------------- #
import XModLib.pygui.battle.library
import XModLib.pygui.battle.views.handlers.ContextMenuHandler
import XModLib.pygui.battle.views.components.panels.TextPanel
# ---------------------- #
#    Global variables    #
# ---------------------- #
g_globals = {
	'appConfigFile': None,
	'appConfigReader': None,
	'appDefaultConfig': None,
	'appLoadingMessage': None
}
# -------------------------------------- #
#    Application configuration reader    #
# -------------------------------------- #
g_globals['appConfigReader'] = XModLib.XMLConfigReader.XMLConfigReader((
	('SimpleShortcut', XModLib.XMLConfigReader.DataObjectXMLReaderMeta.construct(
		'SimpleShortcutXMLReader',
		constructor=lambda shortcut, **kwargs: XModLib.KeyboardUtils.Shortcut(shortcut, **kwargs),
		sectionType='String'
	)),
	('AdvancedShortcut', XModLib.XMLConfigReader.DataObjectXMLReaderMeta.construct(
		'AdvancedShortcutXMLReader',
		constructor=lambda shortcut: XModLib.KeyboardUtils.Shortcut(**shortcut),
		sectionType='Dict'
	)),
	('CorrectionPanelSettings', XModLib.XMLConfigReader.OptionalDictXMLReaderMeta.construct(
		'PanelSettingsXMLReader',
		requiredKeys=('visible', ),
		defaultKeys=('visible', )
	)),
	('TargetPanelSettings', XModLib.XMLConfigReader.OptionalDictXMLReaderMeta.construct(
		'PanelSettingsXMLReader',
		requiredKeys=('visible', ),
		defaultKeys=('visible', )
	)),
	('AimingPanelSettings', XModLib.XMLConfigReader.OptionalDictXMLReaderMeta.construct(
		'PanelSettingsXMLReader',
		requiredKeys=('visible', ),
		defaultKeys=('visible', 'template', 'position')
	)),
	('InfoPanelsIngameSettings', XModLib.IngameSettings.IngameSettingsXMLReaderMeta.construct(
		'InfoPanelsIngameSettingsXMLReader',
		constructor=XModLib.IngameSettings.IngameSettingsDictDataObject.loader('mods/GPCracker.AdvancedAimingSystem/gui/panels/ingame', True)
	))
))

# --------------------------------------- #
#    Application default configuration    #
# --------------------------------------- #
g_globals['appDefaultConfig'] = {
	'applicationEnabled': ('Bool', True),
	'ignoreClientVersion': ('Bool', False),
	'appSuccessMessage': ('LocalizedWideString', u'<a href="event:AdvancedAimingSystem.official_topic"><font color="#0080FF">"Advanced&nbsp;Aiming&nbsp;System&nbsp;NOLF"</font></a> <font color="#008000">was successfully loaded.</font>'),
	'appWarningMessage': ('LocalizedWideString', u'<a href="event:AdvancedAimingSystem.official_topic"><font color="#0080FF">"Advanced&nbsp;Aiming&nbsp;System&nbsp;NOLF"</font></a> <font color="#E00000">was not tested with current client version.</font>'),
	'modules': {
		'aimingInfo': {
			'enabled': ('Bool', True),
			'aimingThreshold': ('Float', 1.05)
		},
		'targetScanner': {
			'enabled': ('Bool', True),
			'scanMode': {
				'useStandardMode': ('Bool', True),
				'useXRayMode': ('Bool', False),
				'useBBoxMode': ('Bool', False),
				'useBEpsMode': ('Bool', False),
				'maxDistance': ('Float', 720.0),
				'boundsScalar': ('Float', 2.5),
				'autoScanInterval': ('Float', 0.04),
				'autoScanExpiryTimeout': ('Float', 10.0),
				'autoScanRelockTimeout': ('Float', 0.16)
			},
			'autoScan': {
				'enabled': ('Bool', True),
				'activated': ('Bool', True),
				'shortcut': ('AdvancedShortcut', {
					'sequence': ('String', 'KEY_LCONTROL+KEY_N'),
					'switch': ('Bool', True),
					'invert': ('Bool', False)
				}),
				'message': {
					'onActivate': ('LocalizedWideString', u'[TargetScanner] AutoMode ENABLED.'),
					'onDeactivate': ('LocalizedWideString', u'[TargetScanner] AutoMode DISABLED.')
				}
			},
			'manualOverride': {
				'enabled': ('Bool', False),
				'shortcut': ('SimpleShortcut', 'KEY_NONE', {'switch': True, 'invert': False})
			}
		},
		'aimCorrection': {
			'arcade': {
				'enabled': ('Bool', False),
				'fixGunMarker': ('Bool', True),
				'manualMode': {
					'enabled': ('Bool', True),
					'shortcut': ('SimpleShortcut', 'KEY_LALT', {'switch': False, 'invert': False})
				},
				'targetMode': {
					'enabled': ('Bool', True),
					'activated': ('Bool', True),
					'shortcut': ('AdvancedShortcut', {
						'sequence': ('String', 'KEY_LCONTROL+KEY_K'),
						'switch': ('Bool', True),
						'invert': ('Bool', False)
					}),
					'message': {
						'onActivate': ('LocalizedWideString', u'[ArcadeAimCorrection] TargetMode ENABLED.'),
						'onDeactivate': ('LocalizedWideString', u'[ArcadeAimCorrection] TargetMode DISABLED.')
					},
					'distance': ('Vector2AsTuple', (50.0, 720.0))
				}
			},
			'sniper': {
				'enabled': ('Bool', True),
				'fixGunMarker': ('Bool', True),
				'manualMode': {
					'enabled': ('Bool', True),
					'shortcut': ('SimpleShortcut', 'KEY_LALT', {'switch': False, 'invert': False})
				},
				'targetMode': {
					'enabled': ('Bool', True),
					'activated': ('Bool', True),
					'shortcut': ('AdvancedShortcut', {
						'sequence': ('String', 'KEY_LCONTROL+KEY_K'),
						'switch': ('Bool', True),
						'invert': ('Bool', False)
					}),
					'message': {
						'onActivate': ('LocalizedWideString', u'[SniperAimCorrection] TargetMode ENABLED.'),
						'onDeactivate': ('LocalizedWideString', u'[SniperAimCorrection] TargetMode DISABLED.')
					},
					'distance': ('Vector2AsTuple', (10.0, 720.0))
				}
			},
			'strategic': {
				'enabled': ('Bool', True),
				'fixGunMarker': ('Bool', False),
				'manualMode': {
					'enabled': ('Bool', True),
					'shortcut': ('SimpleShortcut', 'KEY_LALT', {'switch': False, 'invert': False})
				},
				'targetMode': {
					'enabled': ('Bool', True),
					'activated': ('Bool', False),
					'shortcut': ('AdvancedShortcut', {
						'sequence': ('String', 'KEY_LCONTROL+KEY_K'),
						'switch': ('Bool', True),
						'invert': ('Bool', False)
					}),
					'message': {
						'onActivate': ('LocalizedWideString', u'[StrategicAimCorrection] TargetMode ENABLED.'),
						'onDeactivate': ('LocalizedWideString', u'[StrategicAimCorrection] TargetMode DISABLED.')
					},
					'heightMultiplier': ('Float', 0.5)
				},
				'ignoreVehicles': ('Bool', False)
			},
			'arty': {
				'enabled': ('Bool', False),
				'fixGunMarker': ('Bool', False),
				'manualMode': {
					'enabled': ('Bool', True),
					'shortcut': ('SimpleShortcut', 'KEY_LALT', {'switch': False, 'invert': False})
				},
				'targetMode': {
					'enabled': ('Bool', True),
					'activated': ('Bool', True),
					'shortcut': ('AdvancedShortcut', {
						'sequence': ('String', 'KEY_LCONTROL+KEY_K'),
						'switch': ('Bool', True),
						'invert': ('Bool', False)
					}),
					'message': {
						'onActivate': ('LocalizedWideString', u'[ArtyAimCorrection] TargetMode ENABLED.'),
						'onDeactivate': ('LocalizedWideString', u'[ArtyAimCorrection] TargetMode DISABLED.')
					}
				}
			}
		}
	},
	'plugins': {},
	'gui': {
		'enabled': ('Bool', True),
		'updateInterval': ('Float', 0.04),
		'panels': {
			'context': {
				'hideInfoPanel': ('LocalizedWideString', u'Hide this panel'),
				'resetInfoPanel': ('LocalizedWideString', u'Reset ingame settings')
			},
			'static': {
				'AdvancedAimingSystemCorrectionPanel': {
					'default': {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', False),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Aim correction info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="#00FF00" size="20" face="$UniversCondC">Distance locked: {manualInfo:.1f}m.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.3)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					},
					'arcade': ('CorrectionPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Aim correction info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="#00FF00" size="20" face="$UniversCondC">Distance locked: {manualInfo:.1f}m.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.3)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'sniper': ('CorrectionPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Aim correction info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="#00FF00" size="20" face="$UniversCondC">Distance locked: {manualInfo:.1f}m.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.3)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'strategic': ('CorrectionPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Aim correction info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="#00FF00" size="20" face="$UniversCondC">Altitude locked: {manualInfo:.1f}m.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.3)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'arty': ('CorrectionPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Aim correction info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="#00FF00" size="20" face="$UniversCondC">Unknown parameter locked: {manualInfo:.1f}m.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.3)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					})
				},
				'AdvancedAimingSystemTargetPanel': {
					'default': {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', False),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Target scanner info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="{if|{insight}:#FF3F00:#FF7F00}" size="20" face="$UniversCondC">Target: {shortName}; Distance: {distance:.1f}m; Speed: {speedMS:.1f}m/s.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.4)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					},
					'arcade': ('TargetPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Target scanner info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="{if|{insight}:#FF3F00:#FF7F00}" size="20" face="$UniversCondC">Target: {shortName}; Distance: {distance:.1f}m; Speed: {speedMS:.1f}m/s.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.4)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'sniper': ('TargetPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Target scanner info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="{if|{insight}:#FF3F00:#FF7F00}" size="20" face="$UniversCondC">Target: {shortName}; Distance: {distance:.1f}m; Speed: {speedMS:.1f}m/s.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.4)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'strategic': ('TargetPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Target scanner info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="{if|{insight}:#FF3F00:#FF7F00}" size="20" face="$UniversCondC">Target: {shortName}; Distance: {distance:.1f}m; Speed: {speedMS:.1f}m/s.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.4)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					}),
					'arty': ('TargetPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', ''),
						'tooltip': ('LocalizedWideString', u'Target scanner info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<p align="center"><font color="{if|{insight}:#FF3F00:#FF7F00}" size="20" face="$UniversCondC">Target: {shortName}; Distance: {distance:.1f}m; Speed: {speedMS:.1f}m/s.</font></p>'),
						'position': ('Vector2AsTuple', (0.0, 0.4)),
						'size': ('Vector2AsTuple', (450.0, 25.0))
					})
				},
				'AdvancedAimingSystemAimingPanel': {
					'default': {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', False),
						'background': ('String', 'img://mods/GPCracker.AdvancedAimingSystem/icons/AimingInfoBackground.png'),
						'tooltip': ('LocalizedWideString', u'Aiming info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<textformat leftmargin="20" rightmargin="20" tabstops="[0,70]"><font color="#64F0B4" size="20" face="$UniversCondC">\tRemains:\t{remainingAimingTime:.2f}s;\n\tDistance:\t{aimingDistance:.1f}m;\n\tDeviation:\t{deviation:.2f}m;\n\tFly time:\t{flyTime:.2f}s;\n\tHit angle:\t{hitAngleDeg:+.1f}dg;</font></textformat>'),
						'position': ('Vector2AsTuple', (0.4, -0.1)),
						'size': ('Vector2AsTuple', (175.0, 130.0))
					},
					'arcade': ('AimingPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', 'img://mods/GPCracker.AdvancedAimingSystem/icons/AimingInfoBackground.png'),
						'tooltip': ('LocalizedWideString', u'Aiming info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<textformat leftmargin="20" rightmargin="20" tabstops="[0,70]"><font color="#64F0B4" size="20" face="$UniversCondC">\tRemains:\t{remainingAimingTime:.2f}s;\n\tDistance:\t{aimingDistance:.1f}m;\n\tDeviation:\t{deviation:.2f}m;\n\tFly time:\t{flyTime:.2f}s;\n\tHit angle:\t{hitAngleDeg:+.1f}dg;</font></textformat>'),
						'position': ('Vector2AsTuple', (0.4, -0.1)),
						'size': ('Vector2AsTuple', (175.0, 130.0))
					}),
					'sniper': ('AimingPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', 'img://mods/GPCracker.AdvancedAimingSystem/icons/AimingInfoBackground.png'),
						'tooltip': ('LocalizedWideString', u'Aiming info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<textformat leftmargin="20" rightmargin="20" tabstops="[0,70]"><font color="#64B4F0" size="20" face="$UniversCondC">\tRemains:\t{remainingAimingTime:.2f}s;\n\tDistance:\t{aimingDistance:.1f}m;\n\tDeviation:\t{deviation:.2f}m;\n\tFly time:\t{flyTime:.2f}s;\n\tHit angle:\t{hitAngleDeg:+.1f}dg;</font></textformat>'),
						'position': ('Vector2AsTuple', (0.4, -0.25)),
						'size': ('Vector2AsTuple', (175.0, 130.0))
					}),
					'strategic': ('AimingPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', 'img://mods/GPCracker.AdvancedAimingSystem/icons/AimingInfoBackground.png'),
						'tooltip': ('LocalizedWideString', u'Aiming info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<textformat leftmargin="20" rightmargin="20" tabstops="[0,70]"><font color="#B46464" size="20" face="$UniversCondC">\tRemains:\t{remainingAimingTime:.2f}s;\n\tDistance:\t{aimingDistance:.1f}m;\n\tDeviation:\t{deviation:.2f}m;\n\tFly time:\t{flyTime:.2f}s;\n\tHit angle:\t{hitAngleDeg:+.1f}dg;</font></textformat>'),
						'position': ('Vector2AsTuple', (-0.3, -0.4)),
						'size': ('Vector2AsTuple', (175.0, 130.0))
					}),
					'arty': ('AimingPanelSettings', {
						'alpha': ('Float', 1.0),
						'visible': ('Bool', True),
						'background': ('String', 'img://mods/GPCracker.AdvancedAimingSystem/icons/AimingInfoBackground.png'),
						'tooltip': ('LocalizedWideString', u'Aiming info panel.'),
						'template': ('LocalizedExtendedTemplate', u'<textformat leftmargin="20" rightmargin="20" tabstops="[0,70]"><font color="#B46464" size="20" face="$UniversCondC">\tRemains:\t{remainingAimingTime:.2f}s;\n\tDistance:\t{aimingDistance:.1f}m;\n\tDeviation:\t{deviation:.2f}m;\n\tFly time:\t{flyTime:.2f}s;\n\tHit angle:\t{hitAngleDeg:+.1f}dg;</font></textformat>'),
						'position': ('Vector2AsTuple', (-0.3, -0.4)),
						'size': ('Vector2AsTuple', (175.0, 130.0))
					})
				}
			},
			'ingame': ('InfoPanelsIngameSettings', 'KGRwMQou')
		}
	}
}

# ----------------------------------------- #
#    Application configuration root file    #
# ----------------------------------------- #
g_globals['appConfigFile'] = os.path.splitext(__file__)[0] + '.xml'

# --------------------------------------------- #
#    Application configuration reading stage    #
# --------------------------------------------- #
g_config = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.openSection(g_globals['appConfigFile']),
	g_globals['appDefaultConfig']
)
# ------------------------ #
#    AimingInfo Classes    #
# ------------------------ #
class AimingInfo(object):
	__slots__ = ('__weakref__', 'aimingThreshold')

	def __init__(self, aimingThreshold=1.05):
		super(AimingInfo, self).__init__()
		self.aimingThreshold = aimingThreshold
		return

	def getMacroData(self):
		playerAimingInfo = XModLib.BallisticsMath.getPlayerAimingInfo()
		if playerAimingInfo is not None:
			staticDispersionAngle, aimingStartTime, aimingStartFactor, dispersionFactor, expAimingTime = playerAimingInfo
			aimingFactor = XModLib.BallisticsMath.getAimingFactor(
				aimingStartTime, aimingStartFactor, dispersionFactor, expAimingTime,
				aimingThreshold=self.aimingThreshold
			)
			fullAimingTime = XModLib.BallisticsMath.getFullAimingTime(aimingStartFactor, dispersionFactor, expAimingTime)
			remainingAimingTime = XModLib.BallisticsMath.getRemainingAimingTime(aimingStartTime, fullAimingTime)
			realDispersionAngle = XModLib.BallisticsMath.getDispersionAngle(staticDispersionAngle, aimingFactor)
			aimingDistance, flyTime, shotAngleRad, hitAngleRad = XModLib.BallisticsMath.getPlayerBallisticsInfo()
			deviation = XModLib.BallisticsMath.getDeviation(realDispersionAngle, aimingDistance)
			shotAngleDeg = math.degrees(shotAngleRad)
			hitAngleDeg = math.degrees(hitAngleRad)
			return {
				'expAimingTime': expAimingTime,
				'fullAimingTime': fullAimingTime,
				'remainingAimingTime': remainingAimingTime,
				'staticDispersionAngle': staticDispersionAngle,
				'realDispersionAngle': realDispersionAngle,
				'dispersionFactor': dispersionFactor,
				'aimingDistance': aimingDistance,
				'aimingFactor': aimingFactor,
				'shotAngleRad': shotAngleRad,
				'shotAngleDeg': shotAngleDeg,
				'hitAngleRad': hitAngleRad,
				'hitAngleDeg': hitAngleDeg,
				'deviation': deviation,
				'flyTime': flyTime
			}
		return None

	def enable(self):
		# nothing
		return

	def disable(self):
		# nothing
		return

	def __repr__(self):
		return '{!s}(aimingThreshold={!r})'.format(self.__class__.__name__, self.aimingThreshold)

	def __del__(self):
		return
# ------------------------ #
#    TargetInfo Classes    #
# ------------------------ #
class TargetInfo(int):
	__slots__ = ('__weakref__', 'lastLockTime', 'expiryTimeout', 'relockTimeout', 'shortName', '_height', '_lastHeightVector', '_lastPosition')

	def __new__(cls, target, *args, **kwargs):
		return super(TargetInfo, cls).__new__(cls, target.id) if XModLib.VehicleInfo.isVehicle(target) else None

	def __init__(self, target, lastLockTime=None, expiryTimeout=10.0, relockTimeout=0.16):
		super(TargetInfo, self).__init__(target.id)
		self.lastLockTime = lastLockTime
		self.expiryTimeout = expiryTimeout
		self.relockTimeout = relockTimeout
		self.shortName = XModLib.ArenaInfo.getShortName(target.id)
		self._height = XModLib.VehicleMath.getVehicleHeight(target)
		self._lastHeightVector = XModLib.VehicleMath.getVehicleHeightVector(target, self._height)
		self._lastPosition = target.position
		return

	@property
	def isAutoLocked(self):
		return self.lastLockTime is not None

	@property
	def isExpired(self):
		return self.lastLockTime is not None and self.lastLockTime + self.expiryTimeout <= BigWorld.time()

	@property
	def isInsight(self):
		return self.lastLockTime is None or self.lastLockTime + self.relockTimeout >= BigWorld.time()

	def getMacroData(self):
		speed = self.getSpeed() or 0.0
		return {
			'insight': self.isInsight,
			'shortName': self.shortName,
			'distance': self.getDistance() or 0.0,
			'speedMS': speed,
			'speedMH': speed * 2.24,
			'speedKMH': speed * 3.6
		} if not self.isExpired else None

	def getVehicle(self):
		return BigWorld.entity(self)

	def getSpeed(self):
		vehicle = self.getVehicle()
		return abs(vehicle.filter.speedInfo.value[0]) if vehicle is not None else None

	def getVelocity(self):
		# This method is obsolete and can not longer be used.
		# New vehicle filter does not provide velocity vector value.
		vehicle = self.getVehicle()
		return vehicle.velocity if vehicle is not None else None

	def getPosition(self, actualOnly=False):
		vehicle = self.getVehicle()
		if vehicle is not None:
			self._lastPosition = vehicle.position
			return self._lastPosition
		return self._lastPosition if not actualOnly else None

	def getDistance(self, actualOnly=False):
		position = self.getPosition(actualOnly)
		return position.distTo(BigWorld.player().getOwnVehiclePosition()) if position is not None else None

	def getHeightVector(self, actualOnly=False):
		vehicle = self.getVehicle()
		if vehicle is not None:
			self._lastHeightVector = XModLib.VehicleMath.getVehicleHeightVector(vehicle, self._height)
			return self._lastHeightVector
		return self._lastHeightVector if not actualOnly else None

	def __repr__(self):
		return '{!s}(target=BigWorld.entity({!s}), lastLockTime={!r}, expiryTimeout={!r}, relockTimeout={!r})'.format(
			self.__class__.__name__,
			int.__repr__(self), self.lastLockTime, self.expiryTimeout, self.relockTimeout
		)

	def __del__(self):
		return
# --------------------------- #
#    TargetScanner Classes    #
# --------------------------- #
class TargetScanMode(tuple):
	__slots__ = ()

	_fields, _defaults = zip(
		('useStandardMode', True),
		('useXRayMode', False),
		('useBBoxMode', False),
		('useBEpsMode', False),
		('maxDistance', 720.0),
		('boundsScalar', 2.5),
		('autoScanInterval', 0.04),
		('autoScanExpiryTimeout', 10.0),
		('autoScanRelockTimeout', 0.16)
	)

	@staticmethod
	def filterID(vehicleID):
		return XModLib.ArenaInfo.isEnemy(vehicleID)

	@staticmethod
	def filterVehicle(vehicle):
		return XModLib.VehicleInfo.isAlive(vehicle)

	def __new__(cls, **kwargs):
		return super(TargetScanMode, cls).__new__(cls, itertools.imap(kwargs.get, cls._fields, cls._defaults))

	def __getattr__(self, name):
		if name not in self._fields:
			raise AttributeError('{!r} object has no attribute {!r}'.format(self.__class__.__name__, name))
		return operator.getitem(self, self._fields.index(name))

	def __repr__(self):
		args = itertools.imap('{!s}={!r}'.format, self._fields, self)
		return '{!s}({!s})'.format(self.__class__.__name__, ', '.join(args))

class TargetScanResultCategory(enum.Enum):
	NOTHING = 'nothing'
	PRIMARY = 'primary'
	SECONDARY = 'secondary'
	AMBIGUOUS = 'ambiguous'

class TargetScanResult(collections.namedtuple('TargetScanResult', ('category', 'target'))):
	__slots__ = ()

	@property
	def isNothing(self):
		return self.category == TargetScanResultCategory.NOTHING

	@property
	def isPrimary(self):
		return self.category == TargetScanResultCategory.PRIMARY

	@property
	def isSecondary(self):
		return self.category == TargetScanResultCategory.SECONDARY

	@property
	def isAmbiguous(self):
		return self.category == TargetScanResultCategory.AMBIGUOUS

class TargetScanner(object):
	__slots__ = ('__weakref__', 'autoScanActivated', '_targetScanMode', '_standardScanner', '_xrayScanner', '_bboxScanner', '_bepsScanner', '_updateCallbackLoop')

	@property
	def targetInfo(self):
		return getattr(BigWorld.player().inputHandler, 'XTargetInfo', None)

	@targetInfo.setter
	def targetInfo(self, value):
		setattr(BigWorld.player().inputHandler, 'XTargetInfo', value)
		return

	@property
	def targetScanMode(self):
		return self._targetScanMode

	@targetScanMode.setter
	def targetScanMode(self, value):
		if self.isUpdateActive:
			raise RuntimeError('target scan mode could not be changed while scanner is running')
		self._targetScanMode = value
		# Recreate target scanners and callback loop.
		self._initInternalComponents()
		return

	def __init__(self, targetScanMode=TargetScanMode(), autoScanActivated=True):
		super(TargetScanner, self).__init__()
		self._targetScanMode = targetScanMode
		self.autoScanActivated = autoScanActivated
		# Initialize target scanners and callback loop.
		self._initInternalComponents()
		return

	def _initInternalComponents(self):
		self._standardScanner = XModLib.TargetScanners.StandardScanner(
			self._targetScanMode.filterID,
			self._targetScanMode.filterVehicle
		)
		self._xrayScanner = XModLib.TargetScanners.XRayScanner(
			self._targetScanMode.filterID,
			self._targetScanMode.filterVehicle,
			self._targetScanMode.maxDistance
		)
		self._bboxScanner = XModLib.TargetScanners.BBoxScanner(
			self._targetScanMode.filterID,
			self._targetScanMode.filterVehicle,
			self._targetScanMode.maxDistance,
			self._targetScanMode.boundsScalar
		)
		self._bepsScanner = XModLib.TargetScanners.BEllipseScanner(
			self._targetScanMode.filterID,
			self._targetScanMode.filterVehicle,
			self._targetScanMode.maxDistance,
			self._targetScanMode.boundsScalar
		)
		self._updateCallbackLoop = XModLib.CallbackUtils.CallbackLoop(
			self._targetScanMode.autoScanInterval,
			XModLib.CallbackUtils.getMethodProxy(self._updateTargetInfo)
		)
		return

	def enable(self):
		# nothing
		return

	def disable(self):
		# nothing
		return

	def _performScanningProcedure(self):
		collidableEntities = XModLib.TargetScanners.getCollidableEntities(
			self._targetScanMode.filterID,
			self._targetScanMode.filterVehicle
		)
		primaryTarget = (
			self._standardScanner.getTarget() if self._targetScanMode.useStandardMode else None
		) or (
			self._xrayScanner.getTarget(collidableEntities) if self._targetScanMode.useXRayMode else None
		)
		secondaryTargets = set(
			self._bboxScanner.getTargets(collidableEntities) if self._targetScanMode.useBBoxMode else []
		) | set(
			self._bepsScanner.getTargets(collidableEntities) if self._targetScanMode.useBEpsMode else []
		) if primaryTarget is None else set([])
		return primaryTarget, secondaryTargets

	def scanTarget(self):
		primaryTarget, secondaryTargets = self._performScanningProcedure()
		if primaryTarget is not None:
			return TargetScanResult(TargetScanResultCategory.PRIMARY, primaryTarget)
		if len(secondaryTargets) == 1:
			return TargetScanResult(TargetScanResultCategory.SECONDARY, secondaryTargets.pop())
		if secondaryTargets:
			return TargetScanResult(TargetScanResultCategory.AMBIGUOUS, None)
		return TargetScanResult(TargetScanResultCategory.NOTHING, None)

	def _updateTargetInfo(self):
		if self.isManualOverrideInEffect or not self.autoScanActivated:
			return
		primaryTarget, secondaryTargets = self._performScanningProcedure()
		if primaryTarget is not None:
			if self.targetInfo is not None and self.targetInfo.isAutoLocked and primaryTarget.id == self.targetInfo:
				self.targetInfo.lastLockTime = BigWorld.time()
			elif self.targetInfo is None or self.targetInfo.isAutoLocked:
				self.targetInfo = TargetInfo(
					primaryTarget,
					lastLockTime=BigWorld.time(),
					expiryTimeout=self._targetScanMode.autoScanExpiryTimeout,
					relockTimeout=self._targetScanMode.autoScanRelockTimeout
				)
		elif len(secondaryTargets) == 1 and (self.targetInfo is None or self.targetInfo.isExpired):
			self.targetInfo = TargetInfo(
				secondaryTargets.pop(),
				lastLockTime=BigWorld.time(),
				expiryTimeout=self._targetScanMode.autoScanExpiryTimeout,
				relockTimeout=self._targetScanMode.autoScanRelockTimeout
			)
		elif self.targetInfo is not None and self.targetInfo.isAutoLocked and not self.targetInfo.isExpired and self.targetInfo.getVehicle() in secondaryTargets:
			self.targetInfo.lastLockTime = BigWorld.time()
		return

	def handleVehicleDeath(self, vehicle):
		if vehicle.id == self.targetInfo:
			self.targetInfo = None
		return

	@property
	def isManualOverrideInEffect(self):
		return self.targetInfo is not None and not self.targetInfo.isAutoLocked

	def engageManualOverride(self):
		primaryTarget, secondaryTargets = self._performScanningProcedure()
		if primaryTarget is not None:
			self.targetInfo = TargetInfo(primaryTarget)
		elif len(secondaryTargets) == 1:
			self.targetInfo = TargetInfo(secondaryTargets.pop())
		elif not secondaryTargets:
			self.targetInfo = None
		return

	def disengageManualOverride(self):
		self.targetInfo = None
		return

	@property
	def isUpdateActive(self):
		return self._updateCallbackLoop.isActive

	def start(self, delay=None):
		self._updateCallbackLoop.start(delay)
		return

	def stop(self):
		self._updateCallbackLoop.stop()
		return

	def __repr__(self):
		return '{!s}(targetScanMode={!r}, autoScanActivated={!r})'.format(
			self.__class__.__name__,
			self._targetScanMode, self.autoScanActivated
		)

	def __del__(self):
		self._updateCallbackLoop = None
		return
# --------------------------- #
#    AimCorrection Classes    #
# --------------------------- #
class BaseAimCorrection(object):
	__slots__ = ('__weakref__', '_aihc', 'manualEnabled', 'targetEnabled', 'fixGunMarker', 'manualInfo')

	def __init__(self, avatarInputHandlerCtrl, manualEnabled=False, targetEnabled=False, fixGunMarker=False):
		super(BaseAimCorrection, self).__init__()
		self._aihc = weakref.proxy(avatarInputHandlerCtrl)
		self.manualEnabled = manualEnabled
		self.targetEnabled = targetEnabled
		self.fixGunMarker = fixGunMarker
		self.manualInfo = None
		return

	@property
	def targetInfo(self):
		return getattr(BigWorld.player().inputHandler, 'XTargetInfo', None)

	def getMacroData(self):
		return {
			'manualInfo': self.manualInfo
		} if self.manualEnabled and self.manualInfo is not None else None

	def setManualInfo(self):
		if self.manualEnabled:
			self.manualInfo = None
		return

	def resetManualInfo(self):
		if self.manualEnabled:
			self.manualInfo = None
		return

	def updateManualInfo(self, setRequired=True, resetRequired=True):
		if resetRequired:
			self.resetManualInfo()
		if setRequired:
			self.setManualInfo()
		return

	def enable(self):
		self.manualInfo = None
		return

	def disable(self):
		self.manualInfo = None
		return

	def _getManualDesiredShotPoint(self, shotPoint):
		return None

	def _getTargetDesiredShotPoint(self, shotPoint):
		return None

	def getDesiredShotPoint(self, shotPoint):
		return self._getManualDesiredShotPoint(shotPoint) or self._getTargetDesiredShotPoint(shotPoint) or shotPoint

	def getGunMarkerCollisionPoint(self, start, end):
		return None

	def __repr__(self):
		return '{!s}(avatarInputHandlerCtrl={!r}, manualEnabled={!r}, targetEnabled={!r})'.format(
			self.__class__.__name__,
			self._aihc, self.manualEnabled, self.targetEnabled
		)

	def __del__(self):
		return

class ArcadeAimCorrection(BaseAimCorrection):
	__slots__ = ('minDistance', 'maxDistance')

	def __init__(self, avatarInputHandlerCtrl, manualEnabled=False, targetEnabled=False, fixGunMarker=True, minDistance=50.0, maxDistance=720.0):
		super(ArcadeAimCorrection, self).__init__(avatarInputHandlerCtrl, manualEnabled, targetEnabled, fixGunMarker)
		self.minDistance = minDistance
		self.maxDistance = maxDistance
		return

	def _getScanRayAndPoint(self):
		aimingSystemMatrix = self._aihc.camera.aimingSystem.matrix
		return aimingSystemMatrix.applyToAxis(2), aimingSystemMatrix.applyToOrigin()

	def _getPositionAboveVehicle(self):
		return self._aihc.camera.aimingSystem.positionAboveVehicleProv.value[0:3]

	def setManualInfo(self):
		if self.manualEnabled:
			shotPoint = self._aihc.getDesiredShotPoint()
			if shotPoint is not None:
				self.manualInfo = self._getPositionAboveVehicle().flatDistTo(shotPoint)
		return

	def _getManualDesiredShotPoint(self, shotPoint):
		if self.manualEnabled and shotPoint is not None:
			if self.manualInfo is not None:
				scanRay, scanPoint = self._getScanRayAndPoint()
				flatDistance = scanPoint.flatDistTo(self._getPositionAboveVehicle()) + self.manualInfo
				flatScanRayLength = scanRay.flatDistTo(Math.Vector3(0.0, 0.0, 0.0))
				return scanPoint + scanRay.scale(flatDistance / flatScanRayLength)
		return None

	def _getTargetDesiredShotPoint(self, shotPoint):
		if self.targetEnabled and shotPoint is not None:
			if self.targetInfo is not None and not self.targetInfo.isExpired:
				target = BigWorld.target()
				if target is None or target.id != self.targetInfo:
					scanRay, scanPoint = self._getScanRayAndPoint()
					if self.minDistance <= self.targetInfo.getDistance() <= self.maxDistance:
						flatDistance = scanPoint.flatDistTo(self.targetInfo.getPosition())
						flatScanRayLength = scanRay.flatDistTo(Math.Vector3(0.0, 0.0, 0.0))
						return scanPoint + scanRay.scale(flatDistance / flatScanRayLength)
		return None

	def getGunMarkerCollisionPoint(self, start, end):
		if self.fixGunMarker:
			flatDistance = None
			positionAboveVehicle = self._getPositionAboveVehicle()
			if self.manualEnabled and self.manualInfo is not None:
				flatDistance = self.manualInfo
			elif self.targetEnabled and self.targetInfo is not None and not self.targetInfo.isExpired:
				flatDistance = positionAboveVehicle.flatDistTo(self.targetInfo.getPosition())
			if flatDistance is not None:
				if positionAboveVehicle.flatDistSqrTo(start) <= flatDistance * flatDistance <= positionAboveVehicle.flatDistSqrTo(end):
					return start + (end - start).scale((flatDistance - positionAboveVehicle.flatDistTo(start)) / start.flatDistTo(end))
		return None

	def __repr__(self):
		return '{!s}(avatarInputHandlerCtrl={!r}, manualEnabled={!r}, targetEnabled={!r}, minDistance={!r}, maxDistance={!r})'.format(
			self.__class__.__name__,
			self._aihc, self.manualEnabled, self.targetEnabled, self.minDistance, self.maxDistance
		)

class SniperAimCorrection(BaseAimCorrection):
	__slots__ = ('minDistance', 'maxDistance')

	def __init__(self, avatarInputHandlerCtrl, manualEnabled=False, targetEnabled=False, fixGunMarker=True, minDistance=10.0, maxDistance=720.0):
		super(SniperAimCorrection, self).__init__(avatarInputHandlerCtrl, manualEnabled, targetEnabled, fixGunMarker)
		self.minDistance = minDistance
		self.maxDistance = maxDistance
		return

	def _getScanRayAndPoint(self):
		aimingSystemMatrix = self._aihc.camera.aimingSystem.matrix
		return aimingSystemMatrix.applyToAxis(2), aimingSystemMatrix.applyToOrigin()

	def setManualInfo(self):
		if self.manualEnabled:
			shotPoint = self._aihc.getDesiredShotPoint()
			if shotPoint is not None:
				scanRay, scanPoint = self._getScanRayAndPoint()
				self.manualInfo = (shotPoint - scanPoint).length
		return

	def _getManualDesiredShotPoint(self, shotPoint):
		if self.manualEnabled and shotPoint is not None:
			if self.manualInfo is not None:
				scanRay, scanPoint = self._getScanRayAndPoint()
				return scanPoint + scanRay.scale(self.manualInfo)
		return None

	def _getTargetDesiredShotPoint(self, shotPoint):
		if self.targetEnabled and shotPoint is not None:
			if self.targetInfo is not None and not self.targetInfo.isExpired:
				target = BigWorld.target()
				if target is None or target.id != self.targetInfo:
					scanRay, scanPoint = self._getScanRayAndPoint()
					if self.minDistance <= self.targetInfo.getDistance() <= self.maxDistance:
						return scanPoint + scanRay.scale(scanPoint.distTo(self.targetInfo.getPosition()))
		return None

	def getGunMarkerCollisionPoint(self, start, end):
		if self.fixGunMarker:
			distance = None
			scanRay, scanPoint = self._getScanRayAndPoint()
			if self.manualEnabled and self.manualInfo is not None:
				distance = self.manualInfo
			elif self.targetEnabled and self.targetInfo is not None and not self.targetInfo.isExpired:
				distance = scanPoint.distTo(self.targetInfo.getPosition())
			if distance is not None:
				if scanPoint.distSqrTo(start) <= distance * distance <= scanPoint.distSqrTo(end):
					# Scan point is generally far from small segment of collision test.
					# In that case we can consider that vectors from scan point to start and end is parallel.
					# So we can use linear algorithm instead of square one to get some calculation speed.
					baseDistance = scanPoint.distTo(start)
					return start + (end - start).scale((distance - baseDistance) / (scanPoint.distTo(end) - baseDistance))
		return None

	def __repr__(self):
		return '{!s}(avatarInputHandlerCtrl={!r}, manualEnabled={!r}, targetEnabled={!r}, minDistance={!r}, maxDistance={!r})'.format(
			self.__class__.__name__,
			self._aihc, self.manualEnabled, self.targetEnabled, self.minDistance, self.maxDistance
		)

class StrategicAimCorrection(BaseAimCorrection):
	__slots__ = ('ignoreVehicles', 'heightMultiplier')

	def __init__(self, avatarInputHandlerCtrl, manualEnabled=False, targetEnabled=False, fixGunMarker=False, ignoreVehicles=False, heightMultiplier=0.5):
		super(StrategicAimCorrection, self).__init__(avatarInputHandlerCtrl, manualEnabled, targetEnabled, fixGunMarker)
		self.ignoreVehicles = ignoreVehicles
		self.heightMultiplier = heightMultiplier
		return

	def _getScanRayAndPoint(self):
		aimingSystemMatrix = self._aihc.camera.aimingSystem.matrix
		return Math.Vector3(0.0, -1.0, 0.0), aimingSystemMatrix.applyToOrigin()

	def setManualInfo(self):
		if self.manualEnabled:
			shotPoint = self._aihc.getDesiredShotPoint()
			if shotPoint is not None:
				self.manualInfo = shotPoint.y
		return

	def _getManualDesiredShotPoint(self, shotPoint):
		if self.manualEnabled and shotPoint is not None:
			if self.manualInfo is not None:
				result = Math.Vector3(shotPoint)
				result.y = self.manualInfo
				return result
		return None

	def _getTargetDesiredShotPoint(self, shotPoint):
		if self.targetEnabled and shotPoint is not None:
			if self.targetInfo is not None and not self.targetInfo.isExpired:
				target = BigWorld.target()
				if target is None or target.id != self.targetInfo or self.ignoreVehicles:
					return shotPoint + self.targetInfo.getHeightVector().scale(self.heightMultiplier)
		return None

	def _getGroundDesiredShotPoint(self, shotPoint):
		if self.ignoreVehicles and shotPoint is not None:
			scanRay, scanPoint = self._getScanRayAndPoint()
			result = XModLib.CollisionUtils.collideStatic(scanPoint, scanPoint + scanRay.scale(10000.0))
			return result.closestPoint if result is not None else None
		return None

	def getDesiredShotPoint(self, shotPoint):
		return super(StrategicAimCorrection, self).getDesiredShotPoint(self._getGroundDesiredShotPoint(shotPoint) or shotPoint)

	def getGunMarkerCollisionPoint(self, start, end):
		# This is not required in strategic mode - gun marker is always on ground.
		return None

	def __repr__(self):
		return '{!s}(avatarInputHandlerCtrl={!r}, manualEnabled={!r}, targetEnabled={!r}, ignoreVehicles={!r}, heightMultiplier={!r})'.format(
			self.__class__.__name__,
			self._aihc, self.manualEnabled, self.targetEnabled, self.ignoreVehicles, self.heightMultiplier
		)

class ArtyAimCorrection(BaseAimCorrection):
	__slots__ = ()
# ----------------- #
#    Gui Classes    #
# ----------------- #
class GuiInfoPanelContextMenuHandler(XModLib.pygui.battle.views.handlers.ContextMenuHandler.ContextMenuHandler):
	OPTIONS = (
		('hideInfoPanel', '_hideInfoPanel', g_config['gui']['panels']['context']['hideInfoPanel'], '', True, None),
		('resetInfoPanel', '_resetInfoPanel', g_config['gui']['panels']['context']['resetInfoPanel'], '', True, None)
	)

	@classmethod
	def _getOptionsHandlers(cls):
		def _getOptionsHandlersGenerator(options):
			for idx, handler, label, icon, enabled, submenu in options:
				if submenu is not None:
					for entry in _getOptionsHandlersGenerator(submenu):
						yield entry
				else:
					yield idx, handler
			return
		return dict(_getOptionsHandlersGenerator(cls.OPTIONS))

	@classmethod
	def _getOptionsItems(cls):
		def _makeOptionsItems(options):
			return [cls._makeItem(idx, label, optInitData={'enabled': enabled, 'iconType': icon}, optSubMenu=_makeOptionsItems(submenu) if submenu is not None else submenu) for idx, handler, label, icon, enabled, submenu in options]
		return _makeOptionsItems(cls.OPTIONS)

	def __init__(self, cmProxy, ctx=None):
		super(GuiInfoPanelContextMenuHandler, self).__init__(cmProxy, ctx=ctx, handlers=self._getOptionsHandlers())
		return

	def fini(self):
		super(GuiInfoPanelContextMenuHandler, self).fini()
		return

	def _initFlashValues(self, ctx):
		super(GuiInfoPanelContextMenuHandler, self)._initFlashValues(ctx)
		self._alias = ctx.alias
		return

	def _clearFlashValues(self):
		super(GuiInfoPanelContextMenuHandler, self)._clearFlashValues()
		self._alias = None
		return

	def _hideInfoPanel(self):
		gui.shared.g_eventBus.handleEvent(GuiEvent(GuiEvent.INFO_PANEL_INGAME_CONFIG, {'alias': self._alias, 'config': {'visible': False}}), gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return

	def _resetInfoPanel(self):
		gui.shared.g_eventBus.handleEvent(GuiEvent(GuiEvent.INFO_PANEL_INGAME_RESET, {'alias': self._alias}), gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return

	def _generateOptions(self, ctx=None):
		return self._getOptionsItems()

class GuiCorrectionPanelContextMenuHandler(GuiInfoPanelContextMenuHandler):
	pass

class GuiTargetPanelContextMenuHandler(GuiInfoPanelContextMenuHandler):
	pass

class GuiAimingPanelContextMenuHandler(GuiInfoPanelContextMenuHandler):
	pass

class GuiInfoPanel(XModLib.pygui.battle.views.components.panels.TextPanel.TextPanel):
	def __init__(self, *args, **kwargs):
		super(GuiInfoPanel, self).__init__(*args, **kwargs)
		self.__config = {
			'template': ''
		}
		return

	def py_onPanelDrag(self, x, y):
		super(GuiInfoPanel, self).py_onPanelDrag(x, y)
		self.fireEvent(GuiEvent(GuiEvent.INFO_PANEL_DRAG, {'alias': self.getAlias(), 'position': (x, y)}), gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return

	def py_onPanelDrop(self, x, y):
		super(GuiInfoPanel, self).py_onPanelDrop(x, y)
		self.fireEvent(GuiEvent(GuiEvent.INFO_PANEL_DROP, {'alias': self.getAlias(), 'position': (x, y)}), gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return

	def _populate(self):
		super(GuiInfoPanel, self)._populate()
		self.addListener(GuiEvent.INFO_PANEL_CONFIG, self._handlePanelConfigEvent, gui.shared.EVENT_BUS_SCOPE.BATTLE)
		self.addListener(GuiEvent.INFO_PANEL_UPDATE, self._handlePanelUpdateEvent, gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return

	def _dispose(self):
		self.removeListener(GuiEvent.INFO_PANEL_CONFIG, self._handlePanelConfigEvent, gui.shared.EVENT_BUS_SCOPE.BATTLE)
		self.removeListener(GuiEvent.INFO_PANEL_UPDATE, self._handlePanelUpdateEvent, gui.shared.EVENT_BUS_SCOPE.BATTLE)
		super(GuiInfoPanel, self)._dispose()
		return

	def _handlePanelConfigEvent(self, event):
		if event.ctx['alias'] == self.getAlias():
			self.updateConfig(event.ctx['config'])
		return

	def _handlePanelUpdateEvent(self, event):
		if event.ctx['alias'] == self.getAlias():
			self.updateMacroData(event.ctx['macrodata'])
		return

	def getConfig(self):
		config = super(GuiInfoPanel, self).getConfig()
		config.update(self.__config)
		return config

	def updateConfig(self, config):
		super(GuiInfoPanel, self).updateConfig(config)
		self.__config.update(self._computeConfigPatch(config, self.__config))
		return

	def updateMacroData(self, macrodata):
		self.updateText(self.__config['template'](**macrodata) if macrodata is not None else '')
		return

class GuiCorrectionPanel(GuiInfoPanel):
	pass

class GuiTargetPanel(GuiInfoPanel):
	pass

class GuiAimingPanel(GuiInfoPanel):
	pass

class GuiSettings(object):
	CORRECTION_PANEL_ALIAS = 'AdvancedAimingSystemCorrectionPanel'
	TARGET_PANEL_ALIAS = 'AdvancedAimingSystemTargetPanel'
	AIMING_PANEL_ALIAS = 'AdvancedAimingSystemAimingPanel'

	@staticmethod
	def getContextMenuHandlers():
		return (
			GuiCorrectionPanelContextMenuHandler.getHandler(GuiSettings.CORRECTION_PANEL_ALIAS),
			GuiTargetPanelContextMenuHandler.getHandler(GuiSettings.TARGET_PANEL_ALIAS),
			GuiAimingPanelContextMenuHandler.getHandler(GuiSettings.AIMING_PANEL_ALIAS)
		)

	@staticmethod
	def getViewSettings():
		return (
			GuiCorrectionPanel.getSettings(GuiSettings.CORRECTION_PANEL_ALIAS),
			GuiTargetPanel.getSettings(GuiSettings.TARGET_PANEL_ALIAS),
			GuiAimingPanel.getSettings(GuiSettings.AIMING_PANEL_ALIAS)
		)

class GuiEvent(gui.shared.events.GameEvent):
	INFO_PANEL_INGAME_CONFIG = 'game/AdvancedAimingSystem/InfoPanelIngameConfig'
	INFO_PANEL_INGAME_RESET = 'game/AdvancedAimingSystem/InfoPanelIngameReset'
	INFO_PANEL_CONFIG = 'game/AdvancedAimingSystem/InfoPanelConfig'
	INFO_PANEL_UPDATE = 'game/AdvancedAimingSystem/InfoPanelUpdate'
	INFO_PANEL_DRAG = 'game/AdvancedAimingSystem/InfoPanelDrag'
	INFO_PANEL_DROP = 'game/AdvancedAimingSystem/InfoPanelDrop'
	AVATAR_CTRL_MODE = 'game/AdvancedAimingSystem/AvatarCtrlMode'

class GuiBaseBusinessHandler(gui.Scaleform.framework.package_layout.PackageBusinessHandler):
	@staticmethod
	def _updatePanelConfig(alias, config):
		gui.shared.g_eventBus.handleEvent(GuiEvent(GuiEvent.INFO_PANEL_CONFIG, {'alias': alias, 'config': config}), gui.shared.EVENT_BUS_SCOPE.BATTLE)
		return
	
	def init(self):
		for eventType, listener in self._listeners:
			gui.shared.g_eventBus.addListener(eventType, listener, self._scope)

	def fini(self):
		self._app = None
		for eventType, listener in self._listeners:
			gui.shared.g_eventBus.removeListener(eventType, listener, self._scope)
		self._listeners = ()	

class GuiBattleBusinessHandler(GuiBaseBusinessHandler):
	def __init__(self, staticConfigs, ingameConfigs):
		self._ctrlModeName = 'default'
		self._staticConfigs = staticConfigs
		self._ingameConfigs = ingameConfigs
		super(GuiBattleBusinessHandler, self).__init__(
			(
				(GuiEvent.INFO_PANEL_INGAME_CONFIG, self._handleInfoPanelIngameConfigEvent),
				(GuiEvent.INFO_PANEL_INGAME_RESET, self._handleInfoPanelIngameResetEvent),
				(GuiEvent.INFO_PANEL_DRAG, self._handleInfoPanelDragEvent),
				(GuiEvent.INFO_PANEL_DROP, self._handleInfoPanelDropEvent),
				(GuiEvent.AVATAR_CTRL_MODE, self._handleAvatarCtrlModeEvent)
			),
			gui.app_loader.settings.APP_NAME_SPACE.SF_BATTLE,
			gui.shared.EVENT_BUS_SCOPE.BATTLE
		)
		return

	def _reconfigureInfoPanel(self, alias):
		config = self._staticConfigs.get(alias, {}).get('default', {}).copy()
		config.update(self._ingameConfigs.get(alias, {}).get('default', {}))
		if self._ctrlModeName != 'default':
			config.update(self._staticConfigs.get(alias, {}).get(self._ctrlModeName, {}))
			config.update(self._ingameConfigs.get(alias, {}).get(self._ctrlModeName, {}))
		self._updatePanelConfig(alias, config)
		return

	def _handleInfoPanelIngameConfigEvent(self, event):
		if self._ctrlModeName != 'default':
			self._ingameConfigs.setdefault(event.ctx['alias'], {}).setdefault(self._ctrlModeName, {}).update(event.ctx['config'])
			self._reconfigureInfoPanel(event.ctx['alias'])
			self._ingameConfigs.save()
		return

	def _handleInfoPanelIngameResetEvent(self, event):
		if self._ctrlModeName != 'default':
			self._ingameConfigs.setdefault(event.ctx['alias'], {}).setdefault(self._ctrlModeName, {}).clear()
			self._reconfigureInfoPanel(event.ctx['alias'])
			self._ingameConfigs.save()
		return

	def _handleInfoPanelDragEvent(self, event):
		if self._ctrlModeName != 'default':
			self._ingameConfigs.setdefault(event.ctx['alias'], {}).setdefault(self._ctrlModeName, {})['position'] = event.ctx['position']
			self._ingameConfigs.save()
		return

	def _handleInfoPanelDropEvent(self, event):
		if self._ctrlModeName != 'default':
			self._ingameConfigs.setdefault(event.ctx['alias'], {}).setdefault(self._ctrlModeName, {})['position'] = event.ctx['position']
			self._ingameConfigs.save()
		return

	def _handleAvatarCtrlModeEvent(self, event):
		ctrlMode = event.ctx['ctrlMode']
		if ctrlMode == aih_constants.CTRL_MODE_NAME.ARCADE:
			ctrlModeName = 'arcade'
		elif ctrlMode == aih_constants.CTRL_MODE_NAME.SNIPER or ctrlMode == aih_constants.CTRL_MODE_NAME.DUAL_GUN:
			ctrlModeName = 'sniper'
		elif ctrlMode == aih_constants.CTRL_MODE_NAME.STRATEGIC:
			ctrlModeName = 'strategic'
		elif ctrlMode == aih_constants.CTRL_MODE_NAME.ARTY:
			ctrlModeName = 'arty'
		else:
			ctrlModeName = 'default'
		self._ctrlModeName = ctrlModeName
		for alias in (GuiSettings.CORRECTION_PANEL_ALIAS, GuiSettings.TARGET_PANEL_ALIAS, GuiSettings.AIMING_PANEL_ALIAS):
			config = self._staticConfigs.get(alias, {}).get(ctrlModeName, {}).copy()
			config.update(self._ingameConfigs.get(alias, {}).get(ctrlModeName, {}))
			self._updatePanelConfig(alias, config)
		return

class GuiGlobalBusinessHandler(GuiBaseBusinessHandler):
	def __init__(self, staticConfigs, ingameConfigs):
		self._staticConfigs = staticConfigs
		self._ingameConfigs = ingameConfigs
		super(GuiGlobalBusinessHandler, self).__init__(
			(
				(gui.shared.events.ComponentEvent.COMPONENT_REGISTERED, self._handleComponentRegistrationEvent),
			),
			gui.app_loader.settings.APP_NAME_SPACE.SF_BATTLE,
			gui.shared.EVENT_BUS_SCOPE.GLOBAL
		)
		return

	def _handleComponentRegistrationEvent(self, event):
		if event.alias in (GuiSettings.CORRECTION_PANEL_ALIAS, GuiSettings.TARGET_PANEL_ALIAS, GuiSettings.AIMING_PANEL_ALIAS):
			config = self._staticConfigs.get(event.alias, {}).get('default', {}).copy()
			config.update(self._ingameConfigs.get(event.alias, {}).get('default', {}))
			self._updatePanelConfig(event.alias, config)
		return
# --------------------------- #
#    GuiController Classes    #
# --------------------------- #
class GuiController(object):
	__slots__ = ('__weakref__', '_updateInterval', '_updateCallbackLoop')

	avatarCtrlMode = AvatarInputHandler.aih_global_binding.bindRO(AvatarInputHandler.aih_global_binding.BINDING_ID.CTRL_MODE_NAME)

	@staticmethod
	def dispatchEvent(eventType, ctx=None, scope=gui.shared.EVENT_BUS_SCOPE.BATTLE):
		gui.shared.g_eventBus.handleEvent(GuiEvent(eventType, ctx), scope)
		return

	@property
	def updateInterval(self):
		return self._updateInterval

	@updateInterval.setter
	def updateInterval(self, value):
		if self.isUpdateActive:
			raise RuntimeError('update interval could not be changed while controller is running')
		self._updateInterval = value
		# Recreate internal components.
		self._initInternalComponents()
		return

	def __init__(self, updateInterval=0.04):
		super(GuiController, self).__init__()
		self._updateInterval = updateInterval
		# Initialize internal components.
		self._initInternalComponents()
		return

	def _initInternalComponents(self):
		self._updateCallbackLoop = XModLib.CallbackUtils.CallbackLoop(
			self._updateInterval, XModLib.CallbackUtils.getMethodProxy(self._updateInfoPanels)
		)
		return

	def enable(self):
		aihGlobalBinding = AvatarInputHandler.aih_global_binding
		aihGlobalBinding.subscribe(aihGlobalBinding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
		self.dispatchEvent(GuiEvent.AVATAR_CTRL_MODE, {'ctrlMode': self.avatarCtrlMode})
		return

	def disable(self):
		aihGlobalBinding = AvatarInputHandler.aih_global_binding
		aihGlobalBinding.unsubscribe(aihGlobalBinding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarControlModeChanged)
		return

	def __onAvatarControlModeChanged(self, ctrlMode):
		self.dispatchEvent(GuiEvent.AVATAR_CTRL_MODE, {'ctrlMode': ctrlMode})
		return

	def _getAimCorrectionMacroData(self):
		aimCorrection = getattr(BigWorld.player().inputHandler.ctrl, 'XAimCorrection', None)
		return aimCorrection.getMacroData() if aimCorrection is not None else None

	def _getTargetInfoMacroData(self):
		targetInfo = getattr(BigWorld.player().inputHandler, 'XTargetInfo', None)
		return targetInfo.getMacroData() if targetInfo is not None else None

	def _getAimingInfoMacroData(self):
		aimingInfo = getattr(BigWorld.player().inputHandler, 'XAimingInfo', None)
		return aimingInfo.getMacroData() if aimingInfo is not None else None

	def _updateInfoPanelMacroData(self, alias, macrodata):
		self.dispatchEvent(GuiEvent.INFO_PANEL_UPDATE, {'alias': alias, 'macrodata': macrodata})
		return

	def _updateInfoPanels(self):
		self._updateInfoPanelMacroData(GuiSettings.CORRECTION_PANEL_ALIAS, self._getAimCorrectionMacroData())
		self._updateInfoPanelMacroData(GuiSettings.TARGET_PANEL_ALIAS, self._getTargetInfoMacroData())
		self._updateInfoPanelMacroData(GuiSettings.AIMING_PANEL_ALIAS, self._getAimingInfoMacroData())
		return

	@property
	def isUpdateActive(self):
		return self._updateCallbackLoop.isActive

	def start(self, delay=None):
		self._updateCallbackLoop.start(delay)
		return

	def stop(self):
		self._updateCallbackLoop.stop()
		return

	def __repr__(self):
		return '{!s}(updateInterval={!r})'.format(self.__class__.__name__, self._updateInterval)

	def __del__(self):
		self._updateCallbackLoop = None
		return
# ---------------------------- #
#    Hooks injection events    #
# ---------------------------- #
g_inject_loads = XModLib.HookUtils.HookEvent()
g_inject_basis = XModLib.HookUtils.HookEvent()
g_inject_hooks = XModLib.HookUtils.HookEvent()
g_inject_ovrds = XModLib.HookUtils.HookEvent()

# ---------------------------- #
#    Hooks injection chains    #
# ---------------------------- #
g_inject_stage_init = XModLib.HookUtils.HookChain()
g_inject_stage_main = XModLib.HookUtils.HookChain()
p_inject_stage_init = XModLib.HookUtils.HookChain()
p_inject_stage_main = XModLib.HookUtils.HookChain()

# -------------------------------- #
#    Hooks injection main stage    #
# -------------------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_loads, gameplay.delegator.GameplayLogic, 'start', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_GameplayLogic_start(*args, **kwargs):
	g_inject_stage_main()
	p_inject_stage_main()
	return
# ------------------------ #
#    BattleShared Hooks    #
# ------------------------ #
@XModLib.HookUtils.staticMethodHookExt(g_inject_hooks, gui.Scaleform.daapi.view.battle.shared, 'getContextMenuHandlers', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_BattleShared_getContextMenuHandlers(old_BattleShared_getContextMenuHandlers, *args, **kwargs):
	result = old_BattleShared_getContextMenuHandlers(*args, **kwargs)
	if g_config['gui']['enabled']:
		result += GuiSettings.getContextMenuHandlers()
	return result

@XModLib.HookUtils.staticMethodHookExt(g_inject_hooks, gui.Scaleform.daapi.view.battle.shared, 'getViewSettings', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_BattleShared_getViewSettings(old_BattleShared_getViewSettings, *args, **kwargs):
	result = old_BattleShared_getViewSettings(*args, **kwargs)
	if g_config['gui']['enabled']:
		result += GuiSettings.getViewSettings()
	return result

@XModLib.HookUtils.staticMethodHookExt(g_inject_hooks, gui.Scaleform.daapi.view.battle.shared, 'getBusinessHandlers', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_BattleShared_getBusinessHandlers(old_BattleShared_getBusinessHandlers, *args, **kwargs):
	result = old_BattleShared_getBusinessHandlers(*args, **kwargs)
	config = g_config['gui']
	if config['enabled']:
		result += (
			GuiBattleBusinessHandler(config['panels']['static'], config['panels']['ingame']),
			GuiGlobalBusinessHandler(config['panels']['static'], config['panels']['ingame'])
		)
	return result

# ---------------------- #
#    SharedPage Hooks    #
# ---------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_hooks, gui.Scaleform.daapi.view.battle.shared.SharedPage, '_populate', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_SharedPage_populate(self, *args, **kwargs):
	if g_config['gui']['enabled']:
		self.as_createBattlePagePanelS(GuiSettings.CORRECTION_PANEL_ALIAS, 'TextPanel', 0)
		self.as_createBattlePagePanelS(GuiSettings.TARGET_PANEL_ALIAS, 'TextPanel', 1)
		self.as_createBattlePagePanelS(GuiSettings.AIMING_PANEL_ALIAS, 'TextPanel', 2)
	return
# ----------------------- #
#    BattleEntry Hooks    #
# ----------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_hooks, gui.Scaleform.battle_entry.BattleEntry, '_getRequiredLibraries', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_BattleEntry_getRequiredLibraries(old_BattleEntry_getRequiredLibraries, self, *args, **kwargs):
	return old_BattleEntry_getRequiredLibraries(self, *args, **kwargs) + ('{0[1]}.swf'.format(__application__), )
# ------------------- #
#    Account Hooks    #
# ------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_basis, Account.Account, 'onBecomePlayer')
def new_Account_onBecomePlayer(self, *args, **kwargs):
	if g_globals['appLoadingMessage']:
		XModLib.ClientMessages.SystemMessageFormatter().install(__application__[1])
		def handler(model, entityID, action):
			if action == '{0[1]}.official_topic'.format(__application__):
				BigWorld.wg_openWebBrowser(__official_topic__)
			return
		XModLib.ClientMessages.SystemMessageActionHandler(handler).install()
		XModLib.ClientMessages.pushSystemMessage(
			{
				'message': g_globals['appLoadingMessage'],
				'timestamp': time.time(),
				'icon': 'img://gui/maps/icons/library/InformationIcon-1.png',
			},
			__application__[1],
			auxData=['Information']
		)
		g_globals['appLoadingMessage'] = None
	return
# ------------------- #
#    Vehicle Hooks    #
# ------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_hooks, Vehicle.Vehicle, 'startVisual', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_Vehicle_startVisual(self, *args, **kwargs):
	if not hasattr(self, 'collisionBounds'):
		setattr(self, 'collisionBounds', XModLib.VehicleBounds.getVehicleBoundsMatrixProvider(self))
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, Vehicle.Vehicle, 'stopVisual', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_Vehicle_stopVisual(self, *args, **kwargs):
	if hasattr(self, 'collisionBounds'):
		delattr(self, 'collisionBounds')
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, Vehicle.Vehicle, '_Vehicle__onVehicleDeath')
def new_Vehicle_onVehicleDeath(self, isDeadStarted=False):
	targetScanner = getattr(BigWorld.player().inputHandler, 'XTargetScanner', None)
	if targetScanner is not None:
		targetScanner.handleVehicleDeath(self)
	return
# ------------------------------ #
#    AvatarInputHandler Hooks    #
# ------------------------------ #
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.AvatarInputHandler, '__init__', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_AvatarInputHandler_init(self, *args, **kwargs):
	config = g_config['modules']['targetScanner']
	self.XTargetScanner = TargetScanner(
		targetScanMode=TargetScanMode(**config['scanMode']),
		autoScanActivated=config['autoScan']['enabled'] and config['autoScan']['activated']
	) if config['enabled'] else None
	config = g_config['modules']['aimingInfo']
	self.XAimingInfo = AimingInfo(
		aimingThreshold=config['aimingThreshold']
	) if config['enabled'] else None
	config = g_config['gui']
	self.XGuiController = GuiController(
		updateInterval=config['updateInterval']
	) if config['enabled'] else None
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.AvatarInputHandler, 'start', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_AvatarInputHandler_start(self, *args, **kwargs):
	targetScanner = getattr(self, 'XTargetScanner', None)
	if targetScanner is not None:
		targetScanner.enable()
	aimingInfo = getattr(self, 'XAimingInfo', None)
	if aimingInfo is not None:
		aimingInfo.enable()
	guiController = getattr(self, 'XGuiController', None)
	if guiController is not None:
		guiController.enable()
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.AvatarInputHandler, 'stop', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_AvatarInputHandler_stop(self, *args, **kwargs):
	targetScanner = getattr(self, 'XTargetScanner', None)
	if targetScanner is not None:
		targetScanner.disable()
	aimingInfo = getattr(self, 'XAimingInfo', None)
	if aimingInfo is not None:
		aimingInfo.disable()
	guiController = getattr(self, 'XGuiController', None)
	if guiController is not None:
		guiController.disable()
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.AvatarInputHandler, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_AvatarInputHandler_handleKeyEvent(old_AvatarInputHandler_handleKeyEvent, self, event):
	result = old_AvatarInputHandler_handleKeyEvent(self, event)
	## Keyboard event parsing
	kbevent = XModLib.KeyboardUtils.KeyboardEvent(event)
	## Operating control modes
	operatingControlModes = (
		aih_constants.CTRL_MODE_NAME.ARCADE,
		aih_constants.CTRL_MODE_NAME.SNIPER,
		aih_constants.CTRL_MODE_NAME.STRATEGIC,
		aih_constants.CTRL_MODE_NAME.ARTY
	)
	## AvatarInputHandler started, control mode supported, event not handled by game (for AvatarInputHandler switches)
	if self._AvatarInputHandler__isStarted and self.ctrlModeName in operatingControlModes and not result:
		## HotKeys - TargetScanner
		mconfig = g_config['modules']['targetScanner']
		if mconfig['enabled']:
			## HotKeys - TargetScanner - AutoScan
			fconfig = mconfig['autoScan']
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				fconfig['activated'] = shortcutHandle(fconfig['activated'])
				if shortcutHandle.switch and fconfig['activated']:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onActivate'],
						'green'
					)
				elif shortcutHandle.switch:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onDeactivate'],
						'red'
					)
				targetScanner = getattr(self, 'XTargetScanner', None)
				if targetScanner is not None:
					targetScanner.autoScanActivated = fconfig['activated']
			## HotKeys - TargetScanner - ManualOverride
			fconfig = mconfig['manualOverride']
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and shortcutHandle.pushed:
				targetScanner = getattr(self, 'XTargetScanner', None)
				if targetScanner is not None:
					targetScanner.engageManualOverride()
		## HotKeys - AimCorrection
		mconfig = g_config['modules']['aimCorrection'][self.ctrlModeName]
		if mconfig['enabled']:
			## HotKeys - AimCorrection - Target Mode
			fconfig = mconfig['targetMode']
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				fconfig['activated'] = shortcutHandle(fconfig['activated'])
				if shortcutHandle.switch and fconfig['activated']:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onActivate'],
						'green'
					)
				elif shortcutHandle.switch:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onDeactivate'],
						'red'
					)
				aimCorrection = getattr(self.ctrl, 'XAimCorrection', None)
				if aimCorrection is not None:
					aimCorrection.targetEnabled = fconfig['activated']
	## AvatarInputHandler started, not detached, control mode supported (for AvatarInputHandler shortcuts)
	if self._AvatarInputHandler__isStarted and not self.isDetached and self.ctrlModeName in operatingControlModes:
		## HotKeys - AimCorrection
		mconfig = g_config['modules']['aimCorrection'][self.ctrlModeName]
		if mconfig['enabled']:
			## HotKeys - AimCorrection - ManualMode
			fconfig = mconfig['manualMode']
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle:
				aimCorrection = getattr(self.ctrl, 'XAimCorrection', None)
				if aimCorrection is not None:
					aimCorrection.updateManualInfo(shortcutHandle.pushed)
	## AvatarInputHandler started, event not handled by game (for avatar switches)
	if self._AvatarInputHandler__isStarted and not result:
		pass
	## AvatarInputHandler started (for avatar shortcuts)
	if self._AvatarInputHandler__isStarted:
		pass
	return result
# -------------------------------- #
#    OperatingControlMode Hooks    #
# -------------------------------- #
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, '__init__')
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, '__init__')
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.StrategicControlMode, '__init__')
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArtyControlMode, '__init__')
def new_OperatingControlMode_init(self, *args, **kwargs):
	# These strict type checks ensure hooks will work only in original classes themselves, but not in their subclasses.
	if type(self) is AvatarInputHandler.control_modes.ArcadeControlMode:
		config = g_config['modules']['aimCorrection'][aih_constants.CTRL_MODE_NAME.ARCADE]
		self.XAimCorrection = ArcadeAimCorrection(
			self,
			fixGunMarker=config['fixGunMarker'],
			manualEnabled=config['manualMode']['enabled'],
			targetEnabled=config['targetMode']['enabled'] and config['targetMode']['activated'],
			minDistance=config['targetMode']['distance'][0],
			maxDistance=config['targetMode']['distance'][1]
		) if config['enabled'] else None
	elif type(self) is AvatarInputHandler.control_modes.SniperControlMode:
		config = g_config['modules']['aimCorrection'][aih_constants.CTRL_MODE_NAME.SNIPER]
		self.XAimCorrection = SniperAimCorrection(
			self,
			fixGunMarker=config['fixGunMarker'],
			manualEnabled=config['manualMode']['enabled'],
			targetEnabled=config['targetMode']['enabled'] and config['targetMode']['activated'],
			minDistance=config['targetMode']['distance'][0],
			maxDistance=config['targetMode']['distance'][1]
		) if config['enabled'] else None
	elif type(self) is AvatarInputHandler.control_modes.StrategicControlMode:
		config = g_config['modules']['aimCorrection'][aih_constants.CTRL_MODE_NAME.STRATEGIC]
		self.XAimCorrection = StrategicAimCorrection(
			self,
			fixGunMarker=config['fixGunMarker'],
			manualEnabled=config['manualMode']['enabled'],
			targetEnabled=config['targetMode']['enabled'] and config['targetMode']['activated'],
			ignoreVehicles=config['ignoreVehicles'],
			heightMultiplier=config['targetMode']['heightMultiplier']
		) if config['enabled'] else None
	elif type(self) is AvatarInputHandler.control_modes.ArtyControlMode:
		config = g_config['modules']['aimCorrection'][aih_constants.CTRL_MODE_NAME.ARTY]
		self.XAimCorrection = ArtyAimCorrection(
			self,
			fixGunMarker=config['fixGunMarker'],
			manualEnabled=config['manualMode']['enabled'],
			targetEnabled=config['targetMode']['enabled'] and config['targetMode']['activated']
		) if config['enabled'] else None
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'enable', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'enable', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.StrategicControlMode, 'enable', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArtyControlMode, 'enable', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_OperatingControlMode_enable(self, *args, **kwargs):
	# These strict type checks ensure hooks will work only in original classes themselves, but not in their subclasses.
	if type(self) in (AvatarInputHandler.control_modes.ArcadeControlMode, AvatarInputHandler.control_modes.SniperControlMode, AvatarInputHandler.control_modes.StrategicControlMode, AvatarInputHandler.control_modes.ArtyControlMode):
		aimCorrection = getattr(self, 'XAimCorrection', None)
		if aimCorrection is not None:
			aimCorrection.enable()
		targetScanner = getattr(self._aih, 'XTargetScanner', None)
		if targetScanner is not None and not targetScanner.isUpdateActive:
			targetScanner.start()
		guiController = getattr(self._aih, 'XGuiController', None)
		if guiController is not None and not guiController.isUpdateActive:
			guiController.start()
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'disable', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'disable', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.StrategicControlMode, 'disable', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArtyControlMode, 'disable', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_OperatingControlMode_disable(self, *args, **kwargs):
	# These strict type checks ensure hooks will work only in original classes themselves, but not in their subclasses.
	if type(self) in (AvatarInputHandler.control_modes.ArcadeControlMode, AvatarInputHandler.control_modes.SniperControlMode, AvatarInputHandler.control_modes.StrategicControlMode, AvatarInputHandler.control_modes.ArtyControlMode):
		aimCorrection = getattr(self, 'XAimCorrection', None)
		if aimCorrection is not None:
			aimCorrection.disable()
		targetScanner = getattr(self._aih, 'XTargetScanner', None)
		if targetScanner is not None and targetScanner.isUpdateActive:
			targetScanner.stop()
		guiController = getattr(self._aih, 'XGuiController', None)
		if guiController is not None and guiController.isUpdateActive:
			guiController.stop()
	return

@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'getDesiredShotPoint', invoke=XModLib.HookUtils.HookInvoke.MASTER)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'getDesiredShotPoint', invoke=XModLib.HookUtils.HookInvoke.MASTER)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.StrategicControlMode, 'getDesiredShotPoint', invoke=XModLib.HookUtils.HookInvoke.MASTER)
@XModLib.HookUtils.methodHookExt(g_inject_hooks, AvatarInputHandler.control_modes.ArtyControlMode, 'getDesiredShotPoint', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_OperatingControlMode_getDesiredShotPoint(old_OperatingControlMode_getDesiredShotPoint, self, *args, **kwargs):
	shotPoint = old_OperatingControlMode_getDesiredShotPoint(self, *args, **kwargs)
	# These strict type checks ensure hooks will work only in original classes themselves, but not in their subclasses.
	if type(self) in (AvatarInputHandler.control_modes.ArcadeControlMode, AvatarInputHandler.control_modes.SniperControlMode, AvatarInputHandler.control_modes.StrategicControlMode, AvatarInputHandler.control_modes.ArtyControlMode):
		aimCorrection = getattr(self, 'XAimCorrection', None)
		if aimCorrection is not None:
			return aimCorrection.getDesiredShotPoint(shotPoint)
	return shotPoint
# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import BattleReplay
import ProjectileMover

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import VehicleGunRotator

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils
import XModLib.MathUtils
import XModLib.CollisionUtils

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
# nothing

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
# nothing

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled']:
	sections = g_config['modules']['aimCorrection'].viewvalues()
	if any(section['fixGunMarker'] for section in sections if section['enabled']):
		p_inject_stage_main += p_inject_hooks
		p_inject_stage_init += p_inject_ovrds
	del sections

# ----------------------------- #
#    VehicleGunRotator Hooks    #
# ----------------------------- #
@XModLib.HookUtils.methodAddExt(p_inject_ovrds, VehicleGunRotator.VehicleGunRotator, '_VehicleGunRotator__getGunMarkerPosition')
def new_VehicleGunRotator_getGunMarkerPosition(self, shotPoint, shotVector, dispersionAngles):
	aimCorrection = getattr(self._avatar.inputHandler.ctrl, 'XAimCorrection', None)
	def colliderCorrection(collisionTestStart, collisionTestStop):
		if aimCorrection is not None:
			result = aimCorrection.getGunMarkerCollisionPoint(collisionTestStart, collisionTestStop)
			return (result, ) if result is not None else None
		return None
	def colliderMaterial(collisionTestStart, collisionTestStop):
		return ProjectileMover.collideDynamicAndStatic(collisionTestStart, collisionTestStop, (self.getAttachedVehicleID(), ))
	def colliderSpace(collisionTestStart, collisionTestStop):
		_, result = self._avatar.arena.collideWithSpaceBB(collisionTestStart, collisionTestStop)
		return (result, ) if result is not None else None
	colliders = (colliderCorrection, colliderMaterial, colliderSpace)
	vehicleTypeDescriptor = self._avatar.getVehicleDescriptor()
	shotGravity = Math.Vector3(0.0, -1.0, 0.0).scale(vehicleTypeDescriptor.shot.gravity)
	shotMaxDistance = vehicleTypeDescriptor.shot.maxDistance
	hitPoint, hitVector, hitResult, hitCollider = XModLib.CollisionUtils.computeProjectileTrajectoryEnd(shotPoint, shotVector, shotGravity, colliders)
	hitData = hitResult[1] if hitCollider is colliderMaterial and hitResult[1] is not None and hitResult[1].isVehicle() else None
	markerDistance = shotPoint.distTo(hitPoint)
	if hitCollider is colliderSpace and markerDistance >= shotMaxDistance:
		hitVector = XModLib.MathUtils.getNormalisedVector(hitPoint - shotPoint)
		hitPoint = shotPoint + hitVector.scale(shotMaxDistance)
		markerDistance = shotMaxDistance
	markerDiameter = 2.0 * markerDistance * dispersionAngles[0]
	idealMarkerDiameter = 2.0 * markerDistance * dispersionAngles[1]
	if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isClientReady:
		markerDiameter, hitPoint, hitVector = BattleReplay.g_replayCtrl.getGunMarkerParams(hitPoint, hitVector)
	return hitPoint, hitVector, markerDiameter, idealMarkerDiameter, hitData
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
import aih_constants

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import Avatar
import Vehicle
import AvatarInputHandler.control_modes

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.ArenaInfo
import XModLib.HookUtils
import XModLib.KeyboardUtils
import XModLib.ClientMessages
import XModLib.TargetScanners

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['safeShot'] = {
	'enabled': ('Bool', False),
	'activated': ('Bool', True),
	'shortcut': ('AdvancedShortcut', {
		'sequence': ('String', 'KEY_LALT'),
		'switch': ('Bool', False),
		'invert': ('Bool', True)
	}),
	'message': {
		'onActivate': ('LocalizedWideString', u'[SafeShot] ENABLED.'),
		'onDeactivate': ('LocalizedWideString', u'[SafeShot] DISABLED.')
	},
	'useGunTarget': ('Bool', True),
	'considerBlueHostile': ('Bool', False),
	'fragExpirationTimeout': ('Float', 2.0),
	'template': ('LocalizedStandardTemplate', u'[{reason}] Shot has been blocked.'),
	'reasons': {
		'team': {
			'enabled': ('Bool', True),
			'chat': {
				'enabled': ('Bool', True),
				'message': ('LocalizedStandardTemplate', u'{player} ({vehicle}), you\'re in my line of fire!')
			},
			'template': ('LocalizedWideString', u'friendly')
		},
		'dead': {
			'enabled': ('Bool', True),
			'template': ('LocalizedWideString', u'corpse')
		},
		'waste': {
			'enabled': ('Bool', False),
			'template': ('LocalizedWideString', u'waste')
		}
	}
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['safeShot'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/safeShot'),
	g_globals['appDefaultConfig']['plugins']['safeShot']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['safeShot']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# -------------------------- #
#    GunControlMode Hooks    #
# -------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes._GunControlMode, 'updateGunMarker')
def new_GunControlMode_updateGunMarker(self, markerType, pos, dir, size, relaxTime, collData):
	gunTarget = collData.entity if collData is not None else None
	if markerType == aih_constants.GUN_MARKER_TYPE.CLIENT:
		self._clientTarget = gunTarget
	elif markerType == aih_constants.GUN_MARKER_TYPE.SERVER:
		self._serverTarget = gunTarget
	return

# ------------------- #
#    Vehicle Hooks    #
# ------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, Vehicle.Vehicle, '_Vehicle__onVehicleDeath')
def new_Vehicle_onVehicleDeath(self, isDeadStarted=False):
	if not isDeadStarted:
		self._deathTime = BigWorld.time()
	return

# ------------------------------- #
#    SafeShotControlMode Hooks    #
# ------------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'handleKeyEvent')
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'handleKeyEvent')
def new_SafeShotControlMode_handleKeyEvent(self, isDown, key, mods, event=None):
	## Keyboard event parsing
	kbevent = XModLib.KeyboardUtils.KeyboardEvent(event)
	## AvatarInputHandler started, not detached, control mode supported (for AvatarInputHandler shortcuts)
	if True:
		## HotKeys - SafeShot
		mconfig = g_config['plugins']['safeShot']
		if mconfig['enabled']:
			## HotKeys - SafeShot - Global
			fconfig = mconfig
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				fconfig['activated'] = shortcutHandle(fconfig['activated'])
				if shortcutHandle.switch and fconfig['activated']:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onActivate'],
						'green'
					)
				elif shortcutHandle.switch:
					XModLib.ClientMessages.showMessageOnPanel(
						'Player',
						None,
						fconfig['message']['onDeactivate'],
						'red'
					)
				pass
	return

# ------------------------ #
#    PlayerAvatar Hooks    #
# ------------------------ #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, Avatar.PlayerAvatar, 'shoot', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_PlayerAvatar_shoot(old_PlayerAvatar_shoot, self, *args, **kwargs):
	config = g_config['plugins']['safeShot']
	def isIgnoredCtrlMode(ctrlModeName):
		return ctrlModeName not in (aih_constants.CTRL_MODE_NAME.ARCADE, aih_constants.CTRL_MODE_NAME.SNIPER)
	if not config['enabled'] or not config['activated'] or isIgnoredCtrlMode(self.inputHandler.ctrlModeName):
		return old_PlayerAvatar_shoot(self, *args, **kwargs)
	gunTargetClient = getattr(self.inputHandler.ctrl, '_clientTarget', None)
	gunTargetServer = getattr(self.inputHandler.ctrl, '_serverTarget', None)
	gunTarget = gunTargetClient or gunTargetServer
	aimTarget = XModLib.TargetScanners.StandardScanner().getTarget()
	aimTarget = aimTarget or (gunTarget if config['useGunTarget'] else None)
	isEnemy = XModLib.ArenaInfo.isEnemy
	isTeamKiller = XModLib.ArenaInfo.isTeamKiller
	getShortName = XModLib.ArenaInfo.getShortName
	getPlayerName = XModLib.ArenaInfo.getPlayerName
	def isHostile(vehicleID):
		return isEnemy(vehicleID) or config['considerBlueHostile'] and isTeamKiller(vehicleID)
	def isFreshFrag(vehicle):
		return not vehicle.isAlive() and getattr(vehicle, '_deathTime', BigWorld.time()) + config['fragExpirationTimeout'] >= BigWorld.time()
	def isWasteCtrlMode(ctrlModeName):
		return ctrlModeName in (aih_constants.CTRL_MODE_NAME.ARCADE, )
	reason, target = None, None
	if config['reasons']['waste']['enabled'] and gunTarget is None and isWasteCtrlMode(self.inputHandler.ctrlModeName):
		reason, target = 'waste', gunTarget
	elif config['reasons']['team']['enabled'] and aimTarget is not None and aimTarget.isAlive() and not isHostile(aimTarget.id):
		reason, target = 'team', aimTarget
	elif config['reasons']['dead']['enabled'] and aimTarget is not None and isFreshFrag(aimTarget) and isHostile(aimTarget.id):
		reason, target = 'dead', aimTarget
	if reason is None:
		return old_PlayerAvatar_shoot(self, *args, **kwargs)
	rconfig = config['reasons'][reason]
	error = config['template'](reason=rconfig['template'])
	XModLib.ClientMessages.showMessageOnPanel('VehicleError', reason, error, 'red')
	if reason == 'team' and rconfig['chat']['enabled']:
		channel = XModLib.ClientMessages.getBattleChatControllers()[1]
		if channel is not None and channel.canSendMessage()[0]:
			message = rconfig['chat']['message'](player=getPlayerName(target.id), vehicle=getShortName(target.id))
			channel.sendMessage(message.encode('utf-8'))
	if self._PlayerAvatar__tryShootCallbackId is None:
		self._PlayerAvatar__tryShootCallbackId = BigWorld.callback(0.0, self._PlayerAvatar__tryShootCallback)
	return
# ------------ #
#    Python    #
# ------------ #
import weakref
import operator
import collections

# -------------- #
#    BigWorld    #
# -------------- #
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
# nothing

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import Avatar
import Vehicle

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils
import XModLib.VehicleInfo

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['expertPerk'] = {
	'enabled': ('Bool', False),
	'cacheExtrasInfo': ('Bool', False),
	'cacheExpiryTimeout': ('Float', 30.0),
	'responseTimeout': ('Float', 5.0)
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['expertPerk'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/expertPerk'),
	g_globals['appDefaultConfig']['plugins']['expertPerk']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['expertPerk']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# ------------------------ #
#    ExpertPerk Classes    #
# ------------------------ #
class ExtrasInfoEntry(collections.namedtuple('ExtrasInfoEntry', ('criticalExtras', 'destroyedExtras'))):
	__slots__ = ()

	def __new__(cls, criticalExtras=(), destroyedExtras=()):
		return super(ExtrasInfoEntry, cls).__new__(cls, criticalExtras, destroyedExtras)

class ExtrasInfoCacheEntry(collections.namedtuple('ExtrasInfoCacheEntry', ('extrasInfoEntry', 'receiptTime', 'expiryTimeout'))):
	__slots__ = ()

	def __new__(cls, extrasInfoEntry, receiptTime=None, expiryTimeout=30.0):
		if receiptTime is None:
			receiptTime = BigWorld.time()
		return super(ExtrasInfoCacheEntry, cls).__new__(cls, extrasInfoEntry, receiptTime, expiryTimeout)

	@property
	def isExpired(self):
		return self.receiptTime + self.expiryTimeout <= BigWorld.time()

class ExtrasInfoCache(dict):
	__slots__ = ()

	def cleanup(self):
		vehicleIDs = tuple(vehicleID for vehicleID, cacheEntry in self.viewitems() if cacheEntry.isExpired)
		return tuple((vehicleID, self.pop(vehicleID)) for vehicleID in vehicleIDs)

class ExtrasInfoRequest(collections.namedtuple('ExtrasInfoRequest', ('vehicleID', 'requestTime', 'responseTimeout'))):
	__slots__ = ()

	def __new__(cls, vehicleID, requestTime=None, responseTimeout=5.0):
		if requestTime is None:
			requestTime = BigWorld.time()
		return super(ExtrasInfoRequest, cls).__new__(cls, vehicleID, requestTime, responseTimeout)

	@property
	def isExpired(self):
		return self.requestTime + self.responseTimeout <= BigWorld.time()

class ExtrasInfoResponse(collections.namedtuple('ExtrasInfoResponse', ('vehicleID', 'extrasInfoEntry', 'responseTime'))):
	__slots__ = ()

	def __new__(cls, vehicleID, extrasInfoEntry, responseTime=None):
		if responseTime is None:
			responseTime = BigWorld.time()
		return super(ExtrasInfoResponse, cls).__new__(cls, vehicleID, extrasInfoEntry, responseTime)

class ExtrasInfoRequester(object):
	__slots__ = ('__weakref__', '_avatar', '_activeRequest', '_lastResponse')

	def __init__(self, avatar):
		super(ExtrasInfoRequester, self).__init__()
		self._avatar = weakref.proxy(avatar)
		self._activeRequest = None
		self._lastResponse = None
		return

	@property
	def _maySeeOtherVehicleDamagedDevices(self):
		return self._avatar._maySeeOtherVehicleDamagedDevices

	@property
	def isRequested(self):
		return self._activeRequest is not None

	@property
	def isExpired(self):
		return self._activeRequest is not None and self._activeRequest.isExpired

	@property
	def isResponded(self):
		result = self._activeRequest is not None and self._lastResponse is not None
		result = result and self._activeRequest.vehicleID == self._lastResponse.vehicleID
		return result and self._activeRequest.requestTime <= self._lastResponse.responseTime

	@property
	def lastResponse(self):
		return self._lastResponse

	@property
	def activeRequest(self):
		return self._activeRequest

	@activeRequest.setter
	def activeRequest(self, value):
		if self._maySeeOtherVehicleDamagedDevices:
			if self._activeRequest.vehicleID != value.vehicleID:
				# Monitoring is actually activated only four seconds after sending request.
				# Monitoring means that we immediately receive all updates about vehicle modules.
				# After monitoring is successfully activated, we also receive initial data to show.
				# Monitoring could be maintained only if player's target is in direct visibility area.
				# So for most effective usage we should cancel request only when player changes his target.
				# Server may not respond if target has no critical or destroyed extras or is invisible for player.
				# This situations should be ignored, because server will keep us posted anyway when data will be available.
				if self._activeRequest is not None:
					self._avatar.cell.monitorVehicleDamagedDevices(0)
				self._activeRequest = value
				if self._activeRequest is not None:
					self._avatar.cell.monitorVehicleDamagedDevices(self._activeRequest.vehicleID)
		return

	def onExtrasInfoReceived(self, extrasInfoResponse):
		self._lastResponse = extrasInfoResponse
		return

	def __del__(self):
		if self._activeRequest is not None:
			raise RuntimeError('ExtrasInfoRequester is about to be removed with an active request')
		return

class ExtrasInfoController(object):
	__slots__ = ('__weakref__', '_cache', '_requester', '_cacheExtrasInfo', '_cacheExpiryTimeout', '_responseTimeout')

	def __init__(self, avatar, cacheExtrasInfo=False, cacheExpiryTimeout=30.0, responseTimeout=5.0):
		super(ExtrasInfoController, self).__init__()
		self._cache = ExtrasInfoCache()
		self._requester = ExtrasInfoRequester(avatar)
		self._cacheExtrasInfo = cacheExtrasInfo
		self._cacheExpiryTimeout = cacheExpiryTimeout
		self._responseTimeout = responseTimeout
		return

	cacheExtrasInfo = property(operator.attrgetter('_cacheExtrasInfo'))

	def isMonitored(self, vehicleID):
		return self._requester.isResponded and self._requester.activeRequest.vehicleID == vehicleID

	@property
	def activeRequestVehicleID(self):
		return self._requester.activeRequest.vehicleID if self._requester.activeRequest is not None else 0

	@activeRequestVehicleID.setter
	def activeRequestVehicleID(self, value):
		self._requester.activeRequest = ExtrasInfoRequest(value, responseTimeout=self._responseTimeout) if value != 0 else None
		return

	def cancelExtrasInfoRequest(self, vehicleID=None):
		if vehicleID is None or self.activeRequestVehicleID == vehicleID:
			self.activeRequestVehicleID = 0
		return

	def getCachedExtrasInfoEntry(self, vehicleID):
		# Cache provides access to information about modules of vehicles that were monitored before.
		# Cache entries lifetime may expire, but they are still considered actual if target is being monitored now.
		# Monitored vehicle means that active request is related to requested vehicle and has already been replied.
		# For correct operating when caching is disabled we return data about actually monitored vehicles, but only about them.
		cacheEntry = self._cache.get(vehicleID, None)
		if cacheEntry is not None and (self._cacheExtrasInfo and not cacheEntry.isExpired or self.isMonitored(vehicleID)):
			return cacheEntry.extrasInfoEntry
		return None

	def onExtrasInfoReceived(self, vehicleID, criticalExtras, destroyedExtras):
		extrasInfoEntry = ExtrasInfoEntry(criticalExtras, destroyedExtras)
		self._requester.onExtrasInfoReceived(ExtrasInfoResponse(vehicleID, extrasInfoEntry))
		self._cache[vehicleID] = ExtrasInfoCacheEntry(extrasInfoEntry, expiryTimeout=self._cacheExpiryTimeout)
		return

	def __del__(self):
		if self._requester.activeRequest is not None:
			raise RuntimeError('ExtrasInfoController is about to be removed with an active request')
		return

# ------------------------ #
#    PlayerAvatar Hooks    #
# ------------------------ #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, Avatar.PlayerAvatar, '__init__')
def new_PlayerAvatar_init(self, *args, **kwargs):
	config = g_config['plugins']['expertPerk']
	self.XExtrasInfoController = ExtrasInfoController(
		self,
		cacheExtrasInfo=config['cacheExtrasInfo'],
		cacheExpiryTimeout=config['cacheExpiryTimeout'],
		responseTimeout=config['responseTimeout']
	) if config['enabled'] else None
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, Avatar.PlayerAvatar, 'showOtherVehicleDamagedDevices')
def new_PlayerAvatar_showOtherVehicleDamagedDevices(self, vehicleID, damagedExtras, destroyedExtras):
	extrasInfoController = getattr(self, 'XExtrasInfoController', None)
	if extrasInfoController is not None and getattr(self, '_maySeeOtherVehicleDamagedDevices', False):
		extrasInfoController.onExtrasInfoReceived(vehicleID, damagedExtras, destroyedExtras)
		# This code is executed when server sends data and advanced expert handler is activated.
		# First action we should do here is to cache data received from server for use in future.
		# Target scanner is useless here because expert works only on vehicles in direct visibility area.
		# If received data is about current target, and it is alive, we should show this information to player at once.
		target = BigWorld.target()
		if XModLib.VehicleInfo.isVehicle(target) and target.isAlive() and target.id == vehicleID:
			self.guiSessionProvider.shared.feedback.showVehicleDamagedDevices(vehicleID, damagedExtras, destroyedExtras)
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, Avatar.PlayerAvatar, 'targetBlur')
def new_PlayerAvatar_targetBlur(self, prevEntity):
	extrasInfoController = getattr(self, 'XExtrasInfoController', None)
	if extrasInfoController is not None and getattr(self, '_maySeeOtherVehicleDamagedDevices', False):
		# Default handler cancels expert request here, forcing player to hold crosshairs over target for some time.
		# We moved this code to vehicle visual stop handler, so request will be cancelled only when target disappears.
		# Also request is automatically cancelled before new request is sent or when target dies (all modules break).
		# Code below just hides expert information panel because data is useless when no target is specified.
		if XModLib.VehicleInfo.isVehicle(prevEntity) and prevEntity.isAlive():
			self.guiSessionProvider.shared.feedback.hideVehicleDamagedDevices()
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, Avatar.PlayerAvatar, 'targetFocus')
def new_PlayerAvatar_targetFocus(self, entity):
	extrasInfoController = getattr(self, 'XExtrasInfoController', None)
	if extrasInfoController is not None and getattr(self, '_maySeeOtherVehicleDamagedDevices', False):
		# Like default handler does, we send a request if focused target is an alive vehicle.
		# Unless request is cancelled, actual data will be shown just after client receives it.
		# But for now we check if we have actual cached data that will be displayed until the server sends an update.
		if XModLib.VehicleInfo.isVehicle(entity) and entity.isAlive():
			extrasInfoController.activeRequestVehicleID = entity.id
			extrasInfoEntry = extrasInfoController.getCachedExtrasInfoEntry(entity.id)
			if extrasInfoEntry is not None:
				self.guiSessionProvider.shared.feedback.showVehicleDamagedDevices(entity.id, *extrasInfoEntry)
	return

@XModLib.HookUtils.propertyHookExt(p_inject_hooks, Avatar.PlayerAvatar, '_PlayerAvatar__maySeeOtherVehicleDamagedDevices', XModLib.HookUtils.PropertyAction.GET, '_maySeeOtherVehicleDamagedDevices', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_PlayerAvatar_maySeeOtherVehicleDamagedDevices_getter(old_PlayerAvatar_maySeeOtherVehicleDamagedDevices_getter, self):
	return old_PlayerAvatar_maySeeOtherVehicleDamagedDevices_getter(self) and getattr(self, 'XExtrasInfoController', None) is None

# ------------------- #
#    Vehicle Hooks    #
# ------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, Vehicle.Vehicle, 'stopVisual', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_Vehicle_stopVisual(self, *args, **kwargs):
	# When vehicle disappears we should cancel an active request related to it.
	extrasInfoController = getattr(BigWorld.player(), 'XExtrasInfoController', None)
	if extrasInfoController is not None:
		extrasInfoController.cancelExtrasInfoRequest(self.id)
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, Vehicle.Vehicle, '_Vehicle__onVehicleDeath')
def new_Vehicle_onVehicleDeath(self, isDeadStarted=False):
	# This method is also called when dead target appears (player enters its drawing area).
	if isDeadStarted:
		return
	# When vehicle dies we should cancel an active request related to it.
	extrasInfoController = getattr(BigWorld.player(), 'XExtrasInfoController', None)
	if extrasInfoController is not None:
		extrasInfoController.cancelExtrasInfoRequest(self.id)
	return
# ------------ #
#    Python    #
# ------------ #
import math

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import AvatarInputHandler.cameras

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import gui.battle_control.matrix_factory
import AvatarInputHandler.control_modes
import AvatarInputHandler.DynamicCameras.ArtyCamera

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils
import XModLib.MathUtils
import XModLib.KeyboardUtils
import XModLib.ClientMessages

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['advancedArty'] = {
	'enabled': ('Bool', False),
	'cameraAdjustment': {
		'enabled': ('Bool', True),
		'interpolationSpeed': ('Float', 5.0),
		'disableInterpolation': ('Bool', True),
		'disableHighPitchLevel': ('Bool', True)
	},
	'orthogonalView': {
		'enabled': ('Bool', True),
		'activated': ('Bool', False),
		'shortcut': ('AdvancedShortcut', {
			'sequence': ('String', 'KEY_LALT+KEY_MIDDLEMOUSE'),
			'switch': ('Bool', True),
			'invert': ('Bool', False)
		}),
		'cameraDistance': ('Float', 700.0),
		'preserveLastView': ('Bool', True)
	}
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['advancedArty'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/advancedArty'),
	g_globals['appDefaultConfig']['plugins']['advancedArty']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['advancedArty']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# ---------------------- #
#    ArtyCamera Hooks    #
# ---------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, '__init__')
def new_ArtyCamera_init(self, *args, **kwargs):
	config = g_config['plugins']['advancedArty']
	if config['enabled']:
		if config['cameraAdjustment']['enabled']:
			self._cfg['interpolationSpeed'] = config['cameraAdjustment']['interpolationSpeed']
		if config['orthogonalView']['enabled']:
			self._ArtyCamera__strategicAreaViewScaleMatrix = XModLib.MathUtils.getIdentityMatrix()
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, '_ArtyCamera__interpolateStates', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ArtyCamera_interpolateStates(old_ArtyCamera_interpolateStates, self, deltaTime, translation, rotation):
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['cameraAdjustment']['enabled'] and config['cameraAdjustment']['disableInterpolation']:
		self._ArtyCamera__sourceMatrix = rotation
		self._ArtyCamera__targetMatrix.translation = translation
		return self._ArtyCamera__sourceMatrix, self._ArtyCamera__targetMatrix
	return old_ArtyCamera_interpolateStates(self, deltaTime, translation, rotation)

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, '_ArtyCamera__choosePitchLevel', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ArtyCamera_choosePitchLevel(old_ArtyCamera_choosePitchLevel, self, *args, **kwargs):
	result = old_ArtyCamera_choosePitchLevel(self, *args, **kwargs)
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['cameraAdjustment']['enabled']:
		return result and not config['cameraAdjustment']['disableHighPitchLevel']
	return result

@XModLib.HookUtils.propertyAddExt(p_inject_ovrds, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, 'strategicAreaViewScaleMatrix', XModLib.HookUtils.PropertyAction.GET)
def new_ArtyCamera_strategicAreaViewScaleMatrix_getter(self):
	return getattr(self, '_ArtyCamera__strategicAreaViewScaleMatrix', XModLib.MathUtils.getIdentityMatrix())

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, '_ArtyCamera__calculateIdealState', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ArtyCamera_calculateIdealState(old_ArtyCamera_calculateIdealState, self, *args, **kwargs):
	translation, rotation = old_ArtyCamera_calculateIdealState(self, *args, **kwargs)
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['orthogonalView']['enabled'] and config['orthogonalView']['activated']:
		translation = self.aimingSystem.aimPoint - self._ArtyCamera__getCameraDirection().scale(config['orthogonalView']['cameraDistance'])
	return translation, rotation

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, '_ArtyCamera__cameraUpdate')
def new_ArtyCamera_cameraUpdate(self, *args, **kwargs):
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['orthogonalView']['enabled']:
		cameraDistanceRate = self._ArtyCamera__desiredCamDist / self._ArtyCamera__camDist
		verticalFovHalf = AvatarInputHandler.cameras.FovExtended.instance().actualDefaultVerticalFov * 0.5
		fovCorrectionMultiplier = math.atan(math.tan(verticalFovHalf) * cameraDistanceRate) / verticalFovHalf
		AvatarInputHandler.cameras.FovExtended.instance().setFovByMultiplier(fovCorrectionMultiplier)
		self._ArtyCamera__strategicAreaViewScaleMatrix.setScale(Math.Vector3(1.0, 1.0, 1.0).scale(cameraDistanceRate))
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, 'enable', invoke=XModLib.HookUtils.HookInvoke.SECONDARY)
def new_ArtyCamera_enable(self, *args, **kwargs):
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['orthogonalView']['enabled']:
		AvatarInputHandler.cameras.FovExtended.instance().resetFov()
		config['orthogonalView']['activated'] = config['orthogonalView']['activated'] and config['orthogonalView']['preserveLastView']
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.DynamicCameras.ArtyCamera.ArtyCamera, 'disable', invoke=XModLib.HookUtils.HookInvoke.PRIMARY)
def new_ArtyCamera_disable(self, *args, **kwargs):
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['orthogonalView']['enabled']:
		AvatarInputHandler.cameras.FovExtended.instance().resetFov()
		config['orthogonalView']['activated'] = config['orthogonalView']['activated'] and config['orthogonalView']['preserveLastView']
	return

# ------------------------- #
#    MatrixFactory Hooks    #
# ------------------------- #
@XModLib.HookUtils.staticMethodHookExt(p_inject_hooks, gui.battle_control.matrix_factory, 'makeArtyAimPointMatrix', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_MatrixFactory_makeArtyAimPointMatrix(old_MatrixFactory_makeArtyAimPointMatrix, *args, **kwargs):
	result = old_MatrixFactory_makeArtyAimPointMatrix(*args, **kwargs)
	config = g_config['plugins']['advancedArty']
	if config['enabled'] and config['orthogonalView']['enabled']:
		return XModLib.MathUtils.getMatrixProduct(BigWorld.player().inputHandler.ctrl.camera.strategicAreaViewScaleMatrix, result)
	return result

# --------------------------- #
#    ArtyControlMode Hooks    #
# --------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.ArtyControlMode, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ArtyControlMode_handleKeyEvent(old_ArtyControlMode_handleKeyEvent, self, isDown, key, mods, event=None):
	result = old_ArtyControlMode_handleKeyEvent(self, isDown, key, mods, event)
	## Keyboard event parsing
	kbevent = XModLib.KeyboardUtils.KeyboardEvent(event)
	## AvatarInputHandler started, not detached, control mode supported, event not handled by game (for AvatarInputHandler core switches)
	if not result:
		## HotKeys - AdvancedArty
		mconfig = g_config['plugins']['advancedArty']
		if mconfig['enabled']:
			## HotKeys - AdvancedArty - OrthogonalView
			fconfig = mconfig['orthogonalView']
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				fconfig['activated'] = shortcutHandle(fconfig['activated'])
	return result
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
import aih_constants

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import AvatarInputHandler.control_modes
import gui.Scaleform.daapi.view.battle.shared.crosshair.gm_factory
from gui.Scaleform.genConsts.GUN_MARKER_VIEW_CONSTANTS import GUN_MARKER_VIEW_CONSTANTS as _CONSTANTS

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils
import XModLib.KeyboardUtils

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['sniperModeSPG'] = {
	'enabled': ('Bool', False),
	'shortcut': ('SimpleShortcut', 'KEY_E', {'switch': True, 'invert': False})
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['sniperModeSPG'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/sniperModeSPG'),
	g_globals['appDefaultConfig']['plugins']['sniperModeSPG']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['sniperModeSPG']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# --------------------------------- #
#    ControlMarkersFactory Hooks    #
# --------------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, gui.Scaleform.daapi.view.battle.shared.crosshair.gm_factory._ControlMarkersFactory, '_createSPGMarkers', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ControlMarkersFactory_createSPGMarkers(old_ControlMarkersFactory_createSPGMarkers, self):
	result = old_ControlMarkersFactory_createSPGMarkers(self)
	markerType = self._getMarkerType()
	return result + (self._createSniperMarker(markerType, name=_CONSTANTS.SNIPER_GUN_MARKER_NAME), )

# ----------------------------- #
#    ArcadeControlMode Hooks    #
# ----------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, '_ArcadeControlMode__activateAlternateMode')
def new_ArcadeControlMode_activateAlternateMode(self, pos=None, bByScroll=False):
	if g_config['plugins']['sniperModeSPG']['enabled']:
		if not BigWorld.player().isGunLocked and not BigWorld.player().isOwnBarrelUnderWater:
			if self._aih.isSPG and bByScroll:
				self._aih.onControlModeChanged(
					aih_constants.CTRL_MODE_NAME.SNIPER,
					preferredPos=self.camera.aimingSystem.getDesiredShotPoint(),
					aimingMode=self.aimingMode,
					saveZoom=False,
					equipmentID=None
				)
	return

@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_ArcadeControlMode_handleKeyEvent(old_ArcadeControlMode_handleKeyEvent, self, isDown, key, mods, event=None):
	result = old_ArcadeControlMode_handleKeyEvent(self, isDown, key, mods, event)
	## Keyboard event parsing
	kbevent = XModLib.KeyboardUtils.KeyboardEvent(event)
	## AvatarInputHandler started, not detached, control mode supported, event not handled by game (for AvatarInputHandler core switches)
	if not result and self._aih.isSPG:
		## HotKeys - SPG Sniper Mode
		mconfig = g_config['plugins']['sniperModeSPG']
		if mconfig['enabled']:
			## HotKeys - SPG Sniper Mode - Global
			fconfig = mconfig
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				if not BigWorld.player().isGunLocked and not BigWorld.player().isOwnBarrelUnderWater:
					self._aih.onControlModeChanged(
						aih_constants.CTRL_MODE_NAME.SNIPER,
						preferredPos=self.camera.aimingSystem.getDesiredShotPoint(),
						aimingMode=self.aimingMode,
						saveZoom=True,
						equipmentID=None
					)
	return result

# ----------------------------- #
#    SniperControlMode Hooks    #
# ----------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_SniperControlMode_handleKeyEvent(old_SniperControlMode_handleKeyEvent, self, isDown, key, mods, event=None):
	result = old_SniperControlMode_handleKeyEvent(self, isDown, key, mods, event)
	## Keyboard event parsing
	kbevent = XModLib.KeyboardUtils.KeyboardEvent(event)
	## AvatarInputHandler started, not detached, control mode supported, event not handled by game (for AvatarInputHandler core switches)
	if not result and self._aih.isSPG:
		## HotKeys - SPG Sniper Mode
		mconfig = g_config['plugins']['sniperModeSPG']
		if mconfig['enabled']:
			## HotKeys - SPG Sniper Mode - Global
			fconfig = mconfig
			shortcutHandle = fconfig['enabled'] and fconfig['shortcut'](kbevent)
			if shortcutHandle and (not shortcutHandle.switch or shortcutHandle.pushed):
				if not BigWorld.player().isGunLocked and not BigWorld.player().isOwnBarrelUnderWater:
					self._aih.onControlModeChanged(
						aih_constants.CTRL_MODE_NAME.ARCADE,
						preferredPos=self.camera.aimingSystem.getDesiredShotPoint(),
						turretYaw=self.camera.aimingSystem.turretYaw,
						gunPitch=self.camera.aimingSystem.gunPitch,
						aimingMode=self.aimingMode,
						closesDist=False
					)
	return result
# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import CommandMapping

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import AvatarInputHandler.control_modes

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['autoAim'] = {
	'enabled': ('Bool', False),
	'useTargetScan': ('Bool', False),
	'useTargetInfo': ('Bool', False)
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['autoAim'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/autoAim'),
	g_globals['appDefaultConfig']['plugins']['autoAim']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['autoAim']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# -------------------------- #
#    CommandMapping Hooks    #
# -------------------------- #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, CommandMapping.CommandMapping, 'isFired', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_CommandMapping_isFired(old_CommandMapping_isFired, self, command, key):
	return command != CommandMapping.CMD_CM_LOCK_TARGET and old_CommandMapping_isFired(self, command, key)

# ------------------------------ #
#    AutoAimControlMode Hooks    #
# ------------------------------ #
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.ArcadeControlMode, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
@XModLib.HookUtils.methodHookExt(p_inject_hooks, AvatarInputHandler.control_modes.SniperControlMode, 'handleKeyEvent', invoke=XModLib.HookUtils.HookInvoke.MASTER)
def new_AutoAimControlMode_handleKeyEvent(old_AutoAimControlMode_handleKeyEvent, self, isDown, key, mods, event=None):
	result = old_AutoAimControlMode_handleKeyEvent(self, isDown, key, mods, event)
	if not result and CommandMapping.g_instance.get('CMD_CM_LOCK_TARGET') == key and isDown:
		target = BigWorld.target()
		# Target substitution begins.
		if target is None and g_config['plugins']['autoAim']['useTargetScan']:
			targetScanner = getattr(self._aih, 'XTargetScanner', None)
			if targetScanner is not None:
				target = targetScanner.scanTarget().target
		if target is None and g_config['plugins']['autoAim']['useTargetInfo']:
			targetInfo = getattr(self._aih, 'XTargetInfo', None)
			if targetInfo is not None and not targetInfo.isExpired:
				target = targetInfo.getVehicle()
		# Target substitution ends.
		BigWorld.player().autoAim(target)
	return result
# ------------ #
#    Python    #
# ------------ #
# nothing

# -------------- #
#    BigWorld    #
# -------------- #
import GUI
import Math
import BigWorld

# ---------------- #
#    WoT Client    #
# ---------------- #
import CommandMapping

# ---------------------- #
#    WoT Client Hooks    #
# ---------------------- #
import gui.battle_control.controllers.chat_cmd_ctrl
import gui.Scaleform.daapi.view.battle.shared.radial_menu

# ------------------- #
#    X-Mod Library    #
# ------------------- #
import XModLib.HookUtils

# ----------------------------------- #
#    Plug-in default configuration    #
# ----------------------------------- #
g_globals['appDefaultConfig']['plugins']['radialMenu'] = {
	'enabled': ('Bool', False),
	'useTargetScan': ('Bool', False),
	'useTargetInfo': ('Bool', False)
}

# ----------------------------------------- #
#    Plug-in configuration reading stage    #
# ----------------------------------------- #
g_config['plugins']['radialMenu'] = g_globals['appConfigReader'](
	XModLib.XMLConfigReader.overrideOpenSubSection(g_globals['appConfigFile'], 'plugins/radialMenu'),
	g_globals['appDefaultConfig']['plugins']['radialMenu']
)

# ------------------------------------ #
#    Plug-in hooks injection events    #
# ------------------------------------ #
p_inject_hooks = XModLib.HookUtils.HookEvent()
p_inject_ovrds = XModLib.HookUtils.HookEvent()

# ------------------------ #
#    Plug-in init stage    #
# ------------------------ #
if g_config['applicationEnabled'] and g_config['plugins']['radialMenu']['enabled']:
	p_inject_stage_main += p_inject_hooks
	p_inject_stage_init += p_inject_ovrds

# ---------------------- #
#    RadialMenu Hooks    #
# ---------------------- #
@XModLib.HookUtils.methodAddExt(p_inject_ovrds, gui.Scaleform.daapi.view.battle.shared.radial_menu.RadialMenu, 'show')
def new_RadialMenu_show(self):
	player = BigWorld.player()
	target = BigWorld.target()
	# Target substitution begins.
	config = g_config['plugins']['radialMenu']
	if target is None and config['useTargetScan']:
		targetScanner = getattr(player.inputHandler, 'XTargetScanner', None)
		if targetScanner is not None:
			target = targetScanner.scanTarget().target
	if target is None and config['useTargetInfo']:
		targetInfo = getattr(player.inputHandler, 'XTargetInfo', None)
		if targetInfo is not None and not targetInfo.isExpired:
			target = targetInfo.getVehicle()
	# Target substitution ends.
	self._RadialMenu__targetID = target.id if target is not None else None
	ctrl = self.sessionProvider.shared.crosshair
	guiScreenWidth, guiScreenHeight = GUI.screenResolution()
	screenRatio = float(guiScreenWidth / BigWorld.screenWidth()), float(guiScreenHeight / BigWorld.screenHeight())
	screenPosition = ctrl.getDisaredPosition() if ctrl is not None else (guiScreenWidth * 0.5, guiScreenHeight * 0.5)
	crosshairType = self._RadialMenu__getCrosshairType(player, target)
	if self.app is not None:
		self.app.registerGuiKeyHandler(self)
	self.as_showS(crosshairType, screenPosition, screenRatio)
	return

# ---------------------------------- #
#    ChatCommandsController Hooks    #
# ---------------------------------- #
@XModLib.HookUtils.methodAddExt(p_inject_ovrds, gui.battle_control.controllers.chat_cmd_ctrl.ChatCommandsController, 'handleShortcutChatCommand')
def new_ChatCommandsController_handleShortcutChatCommand(self, key):
	player = BigWorld.player()
	target = BigWorld.target()
	# Target substitution begins.
	config = g_config['plugins']['radialMenu']
	if target is None and config['useTargetScan']:
		targetScanner = getattr(player.inputHandler, 'XTargetScanner', None)
		if targetScanner is not None:
			target = targetScanner.scanTarget().target
	if target is None and config['useTargetInfo']:
		targetInfo = getattr(player.inputHandler, 'XTargetInfo', None)
		if targetInfo is not None and not targetInfo.isExpired:
			target = targetInfo.getVehicle()
	# Target substitution ends.
	for chatCommand, keyboardCommand in gui.battle_control.controllers.chat_cmd_ctrl.KB_MAPPING.iteritems():
		if CommandMapping.g_instance.isFired(keyboardCommand, key):
			crosshairType = self._ChatCommandsController__getCrosshairType(player, target)
			action = chatCommand
			if crosshairType != gui.battle_control.controllers.chat_cmd_ctrl.DEFAULT_CUT:
				if chatCommand in gui.battle_control.controllers.chat_cmd_ctrl.TARGET_TRANSLATION_MAPPING:
					if crosshairType in gui.battle_control.controllers.chat_cmd_ctrl.TARGET_TRANSLATION_MAPPING[chatCommand]:
						action = gui.battle_control.controllers.chat_cmd_ctrl.TARGET_TRANSLATION_MAPPING[chatCommand][crosshairType]
			if action in gui.battle_control.controllers.chat_cmd_ctrl.TARGET_ACTIONS:
				if crosshairType != gui.battle_control.controllers.chat_cmd_ctrl.DEFAULT_CUT:
					self.handleChatCommand(action, target.id)
			else:
				self.handleChatCommand(action)
	return
# ---------------------------- #
#    Application init stage    #
# ---------------------------- #
if g_config['applicationEnabled']:
	g_inject_stage_init += g_inject_loads
	g_inject_stage_main += g_inject_basis
	g_inject_stage_main += g_inject_hooks
	g_inject_stage_init += g_inject_ovrds

# --------------------------------- #
#    Application loading message    #
# --------------------------------- #
if not g_config['applicationEnabled']:
	print >> sys.stdout, '[{0[1]}] {0[0]} is globally disabled and was not loaded.'.format(__application__)
elif not g_config['ignoreClientVersion'] and not XModLib.ClientUtils.isCompatibleClientVersion(__client__):
	print >> sys.stdout, '[{0[1]}] {0[0]} was not tested with current client version.'.format(__application__)
	g_globals['appLoadingMessage'] = g_config['appWarningMessage']
else:
	print >> sys.stdout, '[{0[1]}] {0[0]} was successfully loaded.'.format(__application__)
	g_globals['appLoadingMessage'] = g_config['appSuccessMessage']

# -------------------------------- #
#    Hooks injection init stage    #
# -------------------------------- #
g_inject_stage_init()
p_inject_stage_init()
