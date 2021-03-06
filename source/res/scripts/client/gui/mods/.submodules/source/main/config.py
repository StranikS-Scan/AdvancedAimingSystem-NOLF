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
