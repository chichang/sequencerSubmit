# #================================================================================
# # Render the whole sequence in the Camera Sequencer
# #================================================================================
# '''
# camSeqRenderAll

# USAGE:
# local render all shots in the camera sequencer. playblast style.
# after render is done, this will also create a nuke script named sequence_comp.nk in the output filder
# which have all the shots comped together.

# NOTE:
# 1.whatever renderer set in the rener globals will be useed to render.
# 2.file is written out into the shot image/elements directory with the folder same as the maya file name.
# 3.all the shots are rendered in sub-folders with the following naming: (shot name)_(time offset)
# 4.in case sequence_comp.nk fail to create. use makeNukeScript_manual.py in the util folder.

# '''
# import sys
# sys.path.insert(0, "/USERS/chichang/workspace/")
# import sequencerSubmit.submit as submit
# reload(submit)
# submit.camSeqRenderAll()
# #================================================================================

import os
import math
import maya.cmds as mc
import maya.mel as mel
import subprocess
from .globals import *

class sequenceRenderSubmit:
    #handling submit and start renders
    def __init__(self):
        #initializing shot
        pass

class sequenceShots:
    #handling shot info
    def __init__(self):
        #initializing shot
        pass

def bakeSequenceScale(s):
    
    print "baking shot camera: ", s

    #create shot render cam
    renderCam = mc.shot(s, cc=True, q=True)
    copiedRenderCam = mc.duplicate(renderCam, name=renderCam+"_baked_"+s, un=True)[0]
    print "copied render cam for ", s, " : ", copiedRenderCam

    #shot sequence vars
    seq_startTime = mc.shot(s, sst=True, q=True)
    seq_endTime = mc.shot(s, set=True, q=True)
    seq_duration = mc.shot(s, sequenceDuration=True, q=True)

    #get shot info
    #this assumes start time is never subframe 
    startTime = mc.shot(s, st=True, q=True)
    #get actual end time, api endtime doesnt return subframe.
    mc.sequenceManager(currentTime=seq_endTime)
    endTime = mc.currentTime(q=True)


    print renderCam, ":"
    print "camera time:", startTime, "=>", endTime

    #set current time to start time
    mc.setKeyframe(copiedRenderCam, hi="both", t=startTime)
    print "Created initial keys"
    mc.setKeyframe(copiedRenderCam, hi="both", t=endTime)
    print "Created ending keys"

    #remove any keyframes that's not in this frame range
    print "cleanup keyframes."
    mc.cutKey(copiedRenderCam, clear=True,time=(":"+str(startTime-0.01),), option="keys")
    mc.cutKey(copiedRenderCam, clear=True,time=(str(endTime+0.01)+":",), option="keys")

    #set end time to scale
    scaleEndTime = startTime+seq_duration-1

    print "scaling to: ", startTime, " => ", scaleEndTime

    mc.scaleKey(copiedRenderCam, time=(startTime,endTime), newStartTime=startTime, newEndTime=scaleEndTime, timePivot=0 )

    return copiedRenderCam


def camSeqRenderAll(deleteBakedCam=True):
    '''
    render all shots in sequence manager.
    '''
    #path variables
    userShotDir = os.getenv("USER_SHOT_DIR")
    fileRuleImages = mc.workspace("images",fre=True, q=True)[3:]
    renderGlobalPath = os.path.join(userShotDir, fileRuleImages)
    renderTempPath = os.path.join(renderGlobalPath, "tmp")

    #setup output path
    currentFile = mc.file(q=True, sn=True).split("/")[-1]
    fileName = os.path.splitext(currentFile)[0]
    outputDir = os.path.join(renderGlobalPath, fileName)

    #if shot render already exists. stop the render
    if os.path.exists(outputDir):
        mc.warning("output directory already exist. render canceled.")
        return
    else:
        pass

    #query render settings
    #todo
    #check if active panel is 
    allMdPanel = mc.getPanel(type="modelPanel")
    activePanel = mc.getPanel(wf=True)
    if activePanel not in allMdPanel:
        mc.warning("please select the view you want to render.")
        return

    #create shot output dir
    try:
        #create dir 
        callString = "mkdir "+outputDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
    except:
        print error

    #delete current tmp if found
    #for my local hacking rendering only ...
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

    #get all shots in sequence
    allshots = mc.sequenceManager(lsh=True)
    
    renderedShots = []
    #playblast each shot
    for s in allshots:

        deleteCam = False

        #shot render cam vars
        renderCam = mc.shot(s, cc=True, q=True)
        startTime = math.floor(mc.shot(s, st=True, q=True))
        endTime = math.floor(mc.shot(s, et=True, q=True))

        #shot sequence vars
        seq_startTime = math.floor(mc.shot(s, sst=True, q=True))
        seq_endTime = math.floor(mc.shot(s, set=True, q=True))
        seq_duration = mc.shot(s, sequenceDuration=True, q=True)
        seq_scale = mc.shot(s, scale=True, q=True)
        offsetTime = int(seq_startTime-startTime)
        
        #setup render time
        renderStartFrame = startTime
        renderEndFrame = startTime+seq_duration-1
        
        print s, startTime, endTime,"(",seq_startTime, seq_endTime, ")", renderCam, seq_duration


        if seq_scale != 1.0:
            print "sequnce scale is not uniform. baking camera animation for endering."
            renderCam = bakeSequenceScale(s)
            deleteCam = True

        print "start rendering: ", renderCam

        #set current panel to the current shot cam
        mel.eval("lookThroughModelPanel %s %s;"%(renderCam, activePanel))

        #initialize render! note this will render out an image!
        mel.eval('currentTime %s ;'%(renderStartFrame))
        mel.eval('RenderIntoNewWindow;')
        
        #close render view
        mel.eval('removeRenderWindowPanel renderView;')

        #do the render
        mel.eval('currentTime %s ;'%(renderStartFrame))
        while(renderStartFrame <= renderEndFrame):
            mel.eval('renderWindowRender redoPreviousRender renderView;')
            renderStartFrame += 1
            mel.eval('currentTime %s ;'%(renderStartFrame))

        #remove render camera
        if deleteBakedCam and deleteCam:
            print "deleting camera: ", renderCam
            mc.delete(renderCam)

        #File Operations
        #rename and move shot renders
        shotDirName = s+"_"+str(offsetTime)
        shotDir = os.path.join(renderGlobalPath, shotDirName)

        #TODO: handle this better
        #if there is a same found. this will move the tmp into it instead of rename tmp.
        #for now just remove the old one assume it's from a preveus failed render
        if os.path.exists(shotDir):
            print "found "+shotDir+ "removing it..."
            callString = "rm -rf "+shotDir
            mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, error=mycmd.communicate()
        else:
            pass

        #rename the tmp dir to the shot name
        callString = "mv "+renderTempPath+" "+shotDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
        
        #move into output dir
        callString = "mv "+shotDir+" "+outputDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()

    #write nuke comp
    makeSeqComp(elementsDir=outputDir)

    #display result
    mc.confirmDialog( title='render finished: ', message=outputDir, button=['OK'], defaultButton='OK')

    #done.
    mc.warning("all shots submited for render, Check script editer for more detail.")

def makeSeqComp(elementsDir, startFrame=None, endFrame=None):

    print "making sequence comp script."

    #nuke
    nukePath = os.getenv("NUKE_HOME")
    nukeAppPath = os.path.join(nukePath, "nuke")
    print "running nuke from: ", nukeAppPath

    callString = nukeAppPath
    callString += " -t " + MAKE_SCRIPT_PY
    callString += " -p " + elementsDir

    print callString

    #try:
    mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error=mycmd.communicate()
    print output, error
    #except:
    #    print "error making sequence comp script."