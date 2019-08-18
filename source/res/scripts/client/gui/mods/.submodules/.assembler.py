import codecs

OUTPUT_FILENAME = '../mod_AdvancedAimingSystem.py'
COLLECTED_FIlES = ['source/main/header.py',
                   'source/main/imports.py',
                   'source/main/globals.py',
                   'source/main/config.py',
                   'source/local/AimingInfo.py',
                   'source/local/TargetInfo.py',
                   'source/local/TargetScanner.py',
                   'source/local/AimCorrection.py',
                   'gui/python/GuiClasses.py',
                   'gui/python/GuiController.py',
                   'source/main/injector.py',
                   'source/hooks/BattleShared.py',
                   'source/hooks/BattleEntry.py',
                   'source/hooks/Account.py',
                   'source/hooks/Vehicle.py',
                   'source/hooks/AvatarInputHandler.py',
                   'source/hooks/OperatingControlMode.py',
                   'source/plugins/AimCorrectionGunMarkerFix.py',
                   'source/plugins/SafeShotExtension.py',
                   'source/plugins/ExpertPerkExtension.py',
                   'source/plugins/AdvancedArtyExtension.py',
                   'source/plugins/SniperModeSPGExtension.py',
                   'source/plugins/AutoAimExtension.py',
                   'source/plugins/RadialMenuExtension.py',
                   'source/main/launcher.py']

def linesCollect():
    lines = []
    for fName in COLLECTED_FIlES:
        with codecs.open(fName, 'r', 'utf-8') as f:
            _lines = f.readlines()
        lines += _lines
    return lines

with codecs.open(OUTPUT_FILENAME, 'w', 'utf-8') as f:
    f.writelines(linesCollect())
