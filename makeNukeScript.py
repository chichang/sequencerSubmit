
import nuke
import os

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

if __name__ == "__main__":
    pass