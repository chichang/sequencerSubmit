
#!/usr/bin/env python

from ShotGlobals import *
from XSubmit import *
from MayaVRayJob import *
from LinuxJob import *

# --------------------------------------config
theShow = 'vikings3'
theShot = 'PARIS_ARMY'
fullPath = '/X/projects/vikings3/SHOTS/PARIS_ARMY/chichang/maya/scenes/lighting/FRANK_WARRIOR_A_lookdev_v004.ma'

startFrame = 1
endFrame = 23
byframe = 1
oddsAndEnds = ''

dept = getSGDepartment()

prefix = 'FRANK_WARRIOR_A_lookdev'
resw = 1920
resh = 1080
renderLayer = 'defaultRenderLayer'
renderCam = 'perspShape2'
verNum = 4
renderEye = 'center'

slaveGroup = 'LINUX_24G'
if dept is not None:
    slaveGroup += ',' + dept

vrscene_group = 'LINUX_24G'
if dept is not None:
    vrscene_group += ',' + dept

dynMemLimit = 10000
numThreads = '0'
vrimgExt = 'vrimg2exr'

#u mad?
disableXRTV = 0

VRSceneParts = '40'
extraVRSceneArgs = ''
extraVRayArgs = ''
requiresShave = '0'
# -------------------------------------/config

shotName=theShot
showName=theShow
version=verNum

if renderEye == "center":
    renderEye = ""

if renderLayer != "defaultRenderLayer":
    prefix = prefix + "_" + renderLayer
shot = ShotGlobals()

shot.setShow(showName)
shot.setShot(shotName)
shot.setSlaveGroup(slaveGroup)

shot.setFrames(startFrame,endFrame,byframe)
if oddsAndEnds:
    shot.setOddsEnds(oddsAndEnds)

shot.setPriority('normal')
shot.setVersion(version)

# Break glass in case of emergency
if renderEye == "right":
    shot.setPriority('idle')

vjob = MayaVRayJob(prefix,shot)
vrayfile = fullPath


if renderEye == "left" or renderEye == "right":
    vjob.setStereo(renderEye)

vjob.setMayaFile(vrayfile)
vjob.setExtension(vrimgExt)
vjob.setRenderCam(renderCam)
vjob.setDynamicMemLimit(dynMemLimit)
vjob.setNumThreads(numThreads)
#vjob.setTextureMemLimit(4096)

if requiresShave == 1:
    vjob.setRequiresShave(True)

#if disableXRTV == 1:
#    vjob.disable_xrtv

vjob.setRenderLayer(renderLayer)
vjob.setResolutionSpecial(resw,resh)
vjob.setVrsParts(VRSceneParts)
vjob.setVRSSlaveGroup (vrscene_group)

if extraVRSceneArgs:
    vjob.setExtraVrsceneArgs(extraVRSceneArgs)
if extraVRayArgs:
    vjob.setExtraVrayArgs(extraVRayArgs)

sub = XSubmit()
sub.addPass(vjob)
sub.submit()

