
'''
import sys
sys.path.insert(0, "/USERS/chichang/workspace/")
import sequencerSubmit.submit as submit
reload(submit)
submit.camSeqRenderAll()
'''


##Cam seq render
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



import maya.cmds as mc
import math
allshots = mc.sequenceManager(lsh=True)
#for s in allshots:
    #print s, mc.shot(s, scale=True, q=True)


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

    #query render settings
    #todo

    #setup output path
    currentFile = mc.file(q=True, sn=True).split("/")[-1]
    fileName = os.path.splitext(currentFile)[0]
    outputDir = os.path.join(renderGlobalPath, fileName)

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
    try:
        callString = "rm -rf /X/projects/luna/SHOTS/"+os.getenv("SHOT")+"/chichang/images/elements/tmp/"
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
    except:
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
        
        #get cam transform
        camTransform = mc.listRelatives(renderCam, p=True)[0]


        ###!!! Panel 4 Hardcoded
        #set current panel to the current shot cam
        mel.eval("lookThroughModelPanel %s modelPanel4;"%(renderCam))

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
        callString = "mv "+renderTempPath+" "+shotDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
        
        #move into output dir
        callString = "mv "+shotDir+" "+outputDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()

    #write nuke comp
    makeSeqComp(elementsDir=outputDir)

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