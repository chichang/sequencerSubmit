# #================================================================================
# #  Render a single shot with a single camera
# #================================================================================
# startFrame = None   #render start frame
# endFrame = None     #render end frame
# '''
# renderShot

# USAGE:
# local render a single shot. playblast style.
# this script will render the current camera with the input frame range.

# NOTE:
# 1.whatever renderer set in the rener globals will be useed to render.
# 2.which ever view you have selected. the camera will be use as the render camera.
# 3.file is written out into the shot image/elements directory with the folder same as the maya file name.

# '''
# import sys
# sys.path.insert(0, "/USERS/chichang/workspace/sequencerSubmit/util")
# import renderShot
# reload(renderShot)
# renderShot.renderShot(startFrame, endFrame)
# #================================================================================

import maya.cmds as mc
import maya.mel as mel
import subprocess
import os

def renderShot(startTime, endTime):

    if not startTime or not endTime:
        mc.warning("please specify frame range to render.")
        return
    else:
        print "start rendering..."

    currentFile = mc.file(q=True, sn=True).split("/")[-1]
    fileName = os.path.splitext(currentFile)[0]
    userShotDir = os.getenv("USER_SHOT_DIR")
    fileRuleImages = mc.workspace("images",fre=True, q=True)[3:]
    renderGlobalPath = os.path.join(userShotDir, fileRuleImages)
    renderTempPath = os.path.join(renderGlobalPath, "tmp")
    shotDir = os.path.join(renderGlobalPath, fileName)
    
    #if shot render already exists. stop the render
    #other wise mv(rename) will fail and will move tmp into shot dir
    if os.path.exists(shotDir):
        mc.warning("output directory already exist. render canceled.")
        return
    else:
        pass
    
    allMdPanel = mc.getPanel(type="modelPanel")
    activePanel = mc.getPanel(wf=True)
    print activePanel
    if activePanel not in allMdPanel:
        mc.warning("please select the view you want to render.")
        return
    else:
        renderCam = mc.modelEditor(activePanel, camera=True, q=True)
        print renderCam

    #remove all tmp
    #for my local hacking rendering only ...
    #If temp exists
    if os.path.exists(renderTempPath):
        try:
            print "deleting current tmp dir: ", renderTempPath
            callString = "rm -rf "+renderTempPath
            mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error=mycmd.communicate()
        except:
            print error
    else:
        print "no temp dir found."


    #set current panel to the current shot cam
    mel.eval("lookThroughModelPanel %s %s;"%(renderCam, activePanel))

    #initialize render! note this will render out an image!
    mel.eval('currentTime %s ;'%(startTime))
    mel.eval('RenderIntoNewWindow;')

    mel.eval('currentTime %s ;'%(startTime))
    while(startTime <= endTime):
        mel.eval('renderWindowRender redoPreviousRender renderView;')
        startTime += 1
        mel.eval('currentTime %s ;'%(startTime))

    #rename tmp dir
    print "renameing: ", renderTempPath, " to ", shotDir
    callString = "mv "+renderTempPath+" "+shotDir
    mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error=mycmd.communicate()

    #display result
    mc.confirmDialog( title='render finished: ', message=shotDir, button=['OK'], defaultButton='OK')