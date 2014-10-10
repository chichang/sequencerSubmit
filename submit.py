

'''
import sys
sys.path.insert(0, "/USERS/chichang/workspace/")
import sequencerSubmit.makeNukeScript as makeNukeScript
reload(makeNukeScript)

elements="/X/projects/luna/SHOTS/_default/chichang/images/elements/PV060_anim_v020"

writer = makeNukeScript.ScriptWriter(elements)
writer.write()
'''



##Cam seq render
import os
import math
import maya.cmds as mc
import maya.mel as mel
import subprocess

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
    copiedRenderCam = mc.duplicate(renderCam, name=renderCam+"_baked"+s, un=True)[0]
    print "copied render cam for ", s, " : ", copiedRenderCam

    #get shot info
    startTime = math.floor(mc.shot(s, st=True, q=True))
    endTime = math.floor(mc.shot(s, et=True, q=True))

    print renderCam, ":"
    print "camera time:", startTime, "=>", endTime

    #set current time to start time
    mc.currentTime(startTime, e=True)
    noKeys = mc.setKeyframe(copiedRenderCam, hi="both", t=startTime)
    print "Created ", noKeys, " initial keys"
    mc.currentTime(endTime, e=True)
    noKeys = mc.setKeyframe(copiedRenderCam, hi="both", t=endTime)
    print "Created ", noKeys, " ending keys"

    #remove any keyframes that's not in this frame range
    print "cleanup keyframes."
    mc.cutKey(copiedRenderCam, clear=True,time=(":"+str(startTime-1),), option="keys")
    mc.cutKey(copiedRenderCam, clear=True,time=(str(endTime+1)+":",), option="keys")

    #shot sequence vars
    seq_startTime = math.floor(mc.shot(s, sst=True, q=True))
    seq_endTime = math.floor(mc.shot(s, set=True, q=True))
    seq_duration = mc.shot(s, sequenceDuration=True, q=True)
    scaleEndTime = startTime+seq_duration-1

    print "scaling to: ", startTime, " => ", scaleEndTime

    mc.scaleKey(copiedRenderCam, time=(startTime,endTime), newStartTime=startTime, newEndTime=scaleEndTime, timePivot=0 )

    return copiedRenderCam



def camSeqRenderAll():
    
    currentFile = mc.file(q=True, sn=True).split("/")[-1]
    fileName = os.path.splitext(currentFile)[0]
    outputDir = "/X/projects/luna/SHOTS/"+os.getenv("SHOT")+"/chichang/images/elements/"+fileName
    
    #delete current tmp if found
    try:
        callString = "rm -rf /X/projects/luna/SHOTS/"+os.getenv("SHOT")+"/chichang/images/elements/tmp/"
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
    except:
        print "no temp dir found."

    #create shot output dir
    try:
        #create dir 
        callString = "mkdir "+outputDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
    except:
        print error
        
    #get all shots in sequence
    allshots = mc.sequenceManager(lsh=True)
    
    renderedShots = []
    #playblast each shot
    for s in allshots:
        
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


        print "start rendering: ", renderCam
        
        #get cam transform
        camTransform = mc.listRelatives(renderCam, p=True)[0]

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

        #rename and move shot renders
        shotDir = "/X/projects/luna/SHOTS/"+os.getenv("SHOT")+"/chichang/images/elements/"+s+"_"+str(offsetTime)+"/"
        callString = "mv /X/projects/luna/SHOTS/"+os.getenv("SHOT")+"/chichang/images/elements/tmp/ "+shotDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()
        
        #move into output dir
        callString = "mv "+shotDir+" "+outputDir
        mycmd=subprocess.Popen(callString, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error=mycmd.communicate()




'''


proc ProcessShot(string $curShot, string $targetCam[]) {
string $shotCam = `shot -q -cc $curShot`;
string $copiedCam[] = `duplicate -un $shotCam`;
$shotCam = $copiedCam[0];

int $camStartTime = `shot -q -startTime $curShot`;
int $camEndTime = `shot -q -endTime $curShot`;
currentTime $camStartTime;
int $noKeys = `setKeyframe -hi "both" -t $camStartTime $shotCam`;

print("Created "+$noKeys +" initial keys\n");
currentTime $camEndTime;
$noKeys = `setKeyframe -hi "both" -t $camEndTime $shotCam`;
print("Created "+$noKeys +" ending keys\n");


string $fromTime = $camStartTime+":"+$camEndTime;//`shot -q -startTime $curShot`+":"+`shot -q -endTime $curShot`;
string $toTime = `shot -q -sequenceStartTime $curShot`+":"+`shot -q -sequenceEndTime $curShot`;


print("Processing shot: "+$curShot+"=======\nCopying from "+$shotCam+" to "+$targetCam[1]+"\nTime from "+$fromTime+" to "+$toTime+"\n");
$noKeys = `copyKey -time $fromTime -hi "both" $shotCam`;
print("Copied "+$noKeys +" keys. ");

$noKeys = `pasteKey -time $toTime -option "scaleReplace" $targetCam[0]`;
print("Pasted "+$noKeys+" keys.\n==================================\n");
delete $shotCam;
}


proc CreateSequenceRenderCam()
{
int $userStartTime = `currentTime -q`;
string $targetCam[] = `camera`;
int $timeLineStart = `playbackOptions -q -min`;
int $timeLineEnd = `playbackOptions -q -max`;

sequenceManager -ct $timeLineStart;
string $nextShot = `sequenceManager -q -cs`;
string $curShot = "";
while($nextShot!=$curShot)
{
$curShot = $nextShot; 
ProcessShot($curShot, $targetCam); 
int $nextTime = `shot -q -sequenceEndTime $curShot`;
$nextTime = $nextTime+1;
if($nextTime > $timeLineEnd)break;
print("Next time is "+$nextTime+"\n");
sequenceManager -ct $nextTime;
$nextShot = `sequenceManager -q -cs`;
}
currentTime $userStartTime;

}

'''