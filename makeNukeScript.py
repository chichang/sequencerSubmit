#================================================================================
#  Create nuke comp
#================================================================================

import nuke
import os
from optparse import OptionParser

class ScriptWriter:
    #writes out comp for the sequence.
    def __init__(self, elementsDir, sequenceStart=None, sequenceEnd=None):

        print "initializing script writer."
        #initalize variables
        self.elementsDir = elementsDir
        self.sequenceEnd = sequenceEnd
        self.sequenceStart = sequenceStart
        self.show=os.getenv("SHOW")
        self.shot=os.getenv("SHOT")

        #variables
        self.mergeNodeA = None
        self.padding="%04d"
        self.beforAfter = 3

        #initialize variables
        self.allShots = os.listdir(self.elementsDir)
        self.scriptName = self.shot + "_comp"
        self.scrittPath = os.path.join(self.elementsDir,self.scriptName)

    def write(self):
        #write out the comp
        #todo: for now it's based on the folder naming. "shot_offset"
        #initialize lists
        root = nuke.Root()
        nodes2Merge=[]
        projFirstFrames=[]
        projLastFrames=[]
        projOffsets=[]

        #open a file
        nkScriptPath = os.path.join(self.elementsDir, "sequence_comp.nk")
        try:
            nuke.scriptOpen(nkScriptPath)
        except:
            print "error creating nuke script: ", nkScriptPath
            return

        for s in self.allShots:
            print "importing: ", s
            #initialize variables for shot
            cameraName=s.split("_")[0]
            shotOffset = int(s.split("_")[1])
            filePath = os.path.join(self.elementsDir, s)
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
            fileName = fileStringList[0]+"."+self.padding+"."+fileStringList[2]
            filePath = os.path.join(filePath, fileName)

            #for Project settings
            projFirstFrames.append(firstFrame)
            projLastFrames.append(lastFrame)
            projOffsets.append(shotOffset)

            #Read
            readNode = nuke.nodes.Read(name=cameraName,file=filePath)
            readNode["first"].setValue(firstFrame)
            readNode["last"].setValue(lastFrame)
            readNode["before"].setValue(self.beforAfter)
            readNode["after"].setValue(self.beforAfter)

            #Time Offset
            offsetNode = nuke.nodes.TimeOffset(inputs=[readNode], time_offset=int(shotOffset))
            nodes2Merge.append(offsetNode)

            #Merge
            if self.mergeNodeA:
                mergeNode = nuke.nodes.Merge(inputs=(self.mergeNodeA,offsetNode))
            else:
                mergeNode = nuke.nodes.Dot()
                mergeNode.setInput(0, offsetNode)
            
            #set to merge to next
            self.mergeNodeA = mergeNode

        #Project setting
        ##todo: get this from maya seq manager
        firstFrame = min(projFirstFrames)+min(projOffsets)
        lastFrame = max(projLastFrames)+max(projOffsets)
        root["first_frame"].setValue(firstFrame)
        root["last_frame"].setValue(lastFrame)

        #save
        nuke.scriptSave(nkScriptPath)


if __name__ == "__main__":
    
    #parse options
    usage = 'usage: %prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-p', action='store', type='string', dest='path', help="path to files")
    #parser.add_option('-ss', action='store', type='int', dest='start_frame', default=None, help="start frame")
    #parser.add_option('-se', action='store', type='int', dest='end_frame', default=None, help="end frame")

    (options, args) = parser.parse_args()

    path = options.path
    #start_frame = options.start_frame
    #end_frame = options.end_frame

    #writer = ScriptWriter(elementsDir=path, sequenceStart=start_frame, sequenceEnd=end_frame)
    writer = ScriptWriter(elementsDir=path)
    writer.write()