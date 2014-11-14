# #================================================================================
# #  Create sequence render comp
# #================================================================================
# elementsDir=None #directory that contains all shot renders
# '''
# makeSeqenceComp

# USAGE:
# run this in nuke.
# given the directory that contains all the shot renders.
# this will comp all the shots together with proper time offset.

# NOTE:
# 3.all the shot folders need to have the following naming: (shot name)_(time offset)

# '''
# import sys
# sys.path.insert(0, "/USERS/chichang/workspace/sequencerSubmit/util")
# import makeNukeScript_manual
# reload(makeNukeScript_manual)
# makeNukeScript_manual.makeSeqenceComp(elementsDir)
# #================================================================================

import nuke
import os

def makeSeqenceComp(elementsDir):
    #initialize variables
    allShots = os.listdir(elementsDir)
    #variables
    mergeNodeA = None
    padding="%04d"
    beforAfter = 3

    root = nuke.Root()
    nodes2Merge=[]
    projFirstFrames=[]
    projLastFrames=[]
    projOffsets=[]

    for s in allShots:
        print "importing: ", s
        #initialize variables for shot
        cameraName=s.split("_")[0]
        shotOffset = int(s.split("_")[1])
        filePath = os.path.join(elementsDir, s)
        allShotFrames = os.listdir(filePath)
        fileStringList = allShotFrames[0].split(".")

        #for getting frame range
        frames = []
        for f in allShotFrames:
            frameStringList = f.split(".")
            frame=int(frameStringList[1])
            frames.append(frame)

        #for read node
        firstFrame = min(frames)
        lastFrame = max(frames)
        fileName = fileStringList[0]+"."+padding+"."+fileStringList[2]
        filePath = os.path.join(filePath, fileName)

        #for Project settings
        projFirstFrames.append(firstFrame)
        projLastFrames.append(lastFrame)
        projOffsets.append(shotOffset)

        #Read
        readNode = nuke.nodes.Read(name=cameraName,file=filePath)
        readNode["first"].setValue(firstFrame)
        readNode["last"].setValue(lastFrame)
        readNode["before"].setValue(beforAfter)
        readNode["after"].setValue(beforAfter)

        #Time Offset
        offsetNode = nuke.nodes.TimeOffset(inputs=[readNode], time_offset=int(shotOffset))
        nodes2Merge.append(offsetNode)

        #Merge
        if mergeNodeA:
            mergeNode = nuke.nodes.Merge(inputs=(mergeNodeA,offsetNode))
        else:
            mergeNode = nuke.nodes.Dot()
            mergeNode.setInput(0, offsetNode)
        
        #set to merge to next
        mergeNodeA = mergeNode

    #Project setting
    ##todo: get this from maya seq manager
    firstFrame = min(projFirstFrames)+min(projOffsets)
    lastFrame = max(projLastFrames)+max(projOffsets)
    root["first_frame"].setValue(firstFrame)
    root["last_frame"].setValue(lastFrame)
