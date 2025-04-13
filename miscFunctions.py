from constants import *
from pxattr import *
from surfaces import *
from fakeWindow import *

os.environ["PYSDL2_DLL_PATH"] = "./"

#prompt - dialogue window

def handleUndoRedo(attribute):
    pxattr.pxEdit(attribute)
    surfMpt.editTile(attribute)
    updateRender(const.surfaceFunctions)
    const.setViewport()

def redo():
    mouse.resetSurfaces()
    if not const.editing:
        return
    if mouse.historyIndex < len(mouse.history) - 1:
        mouse.historyIndex += 1
        attribute = mouse.history[mouse.historyIndex][1]
        mouse.tilePos = mouse.history[mouse.historyIndex][2]
        handleUndoRedo(attribute)

def undo():
    mouse.resetSurfaces()
    if not const.editing:
        return
    if mouse.historyIndex >= 0:
        attribute = mouse.history[mouse.historyIndex][0]
        mouse.tilePos = mouse.history[mouse.historyIndex][2]
        mouse.historyIndex -= 1
        handleUndoRedo(attribute)

def updateAttributesTexture():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if pxattr.version == 0:
        surfAttr.attrSurf = loadImageAsSurf(paths.attributesTextureKB)
        surfMpt.attributeSurf = loadImageAsSurf(paths.attributesTextureKB)

    elif pxattr.version == 1:
        surfAttr.attrSurf = loadImageAsSurf(paths.attributesTexturePT)
        surfMpt.attributeSurf = loadImageAsSurf(paths.attributesTexturePT)
    elif pxattr.version == 2:
        surfAttr.attrSurf = loadImageAsSurf(paths.attributesTexture2012)
        surfMpt.attributeSurf = loadImageAsSurf(paths.attributesTexture2012)
    surfAttr.updateTex()

def openFile():
    imgPath = ''
    path = filedialpy.openFile(
            initial_dir="./",
            title="Select pxAttr",
            filter=["pxAttr Files *.pxattr", "All Files *"]
        )
    if not os.path.exists(path):
        if surfMpt.fileSelected: #if file not selected when editing file, don't clear the file.
            const.editing = True
            mouse.resetSurfaces()            
        return
    else:
        mouse.history.clear()
        mouse.historyIndex = -1
        pxattr.pxOpen(path)
        pxattr.path = path
        pxattr.attributeArrayEdit = pxattr.attributeArray

        updateAttributesTexture()

        surfMpt.path = path[:-7]+'.png'
        surfMpt.formatFile()

def processSaveAs(inputData):
    pxattr.savePath = inputData[0]
    pxattr.version = inputData[1]
    pxattr.compression = inputData[2]
    pxattr.pxSave()
    
def promptSaveAs():
    resetDialogueWindow()
    dialogueWindow.importData('Saving .pxattr',
            [inputStarter('Save Path', [('SAVE PATH:', pxattr.path, 4)]),
            inputStarter('Game Version', [('0 = KB; 1 = PITEST; 2 = 2012', pxattr.version, 0)]),
            inputStarter('Compression', [("0 = None; 1 = Horizontal; 2 = Vertical", 0, 0)])])
    dialogueWindow.calculateWindowSize()
    const.surfaceFunctions.append(dialogueWindow)
    const.inputFunction = processSaveAs
    updateRender(const.surfaceFunctions)
    const.setViewport()

def saveFile():
    if not const.editing:
        return
    pxattr.pxSave()
    mouse.resetSurfaces()

def fileInfo(): #TODO
    if not const.editing:
        return
    

def processCreatePxattr(inputData):
    pxattr.path = inputData[0]
    pxattr.savePath = inputData[0]
    pxattr.version = inputData[2]
    #0 - fileName; 1 - version; 2 - width; 3 - height; 4 = use image, 5 = path
    surfMpt.path = inputData[4]
    const.editPxRes(inputData[5])

    pxattr.pxCreate(*inputData[:4])
    mouse.tilePos = (0, 0)

    updateAttributesTexture()
    surfMpt.formatFile()
    
def promptCreatePxattr():
    resetDialogueWindow()
    dialogueWindow.importData('New .pxattr',
            [inputStarter('File Name', [('NAME:', '.pxattr', 3)]),
            inputStarter('Game Version', [('0 = KB; 1 = PITEST; 2 = 2012', 0, 0)]),
            inputStarter('Size (Tiles)', [('SIZE X:', 16, 0), ('SIZE Y:', 16, 0)]),
            inputStarter('Image', [('IMAGE PATH (OPTIONAL:) ', './', 4)]),
            inputStarter('Tile Resolution', [("(DOESN'T AFFECT FILE DATA.)", 2, 0)])])
    dialogueWindow.calculateWindowSize()
    const.surfaceFunctions.append(dialogueWindow)
    const.inputFunction = processCreatePxattr
    updateRender(const.surfaceFunctions)
    const.setViewport()

def processEditPxattr(inputData): #0 = version, 1 = compression, 2 = Size X, 3 = Size Y, 4 = pxRes
    pxattr.version = inputData[0]
    pxattr.compression = inputData[1]
    pxattr.pxResize(*inputData[2:4])
    mouse.tilePos = (0, 0)
    const.editPxRes(inputData[4])
    surfMpt.formatFile()

def promptEditPxattr():
    if not const.editing: 
        return #nothing to modify would break program
    resetDialogueWindow()
    dialogueWindow.importData('Edit .pxattr data',
                             [inputStarter('Game Version', [('0 = KB; 1 = PITEST; 2 = SFROG/RFISH', pxattr.version, 0)]),
                              inputStarter('Compression', [('0 = NONE; 1 = HORIZONTAL; 2 = VERTICAL', pxattr.compression, 0)]),
                              inputStarter('Size (Tiles)', [('SIZE X:', pxattr.width, 0), ('SIZE Y:', pxattr.height, 0)]),
                              inputStarter('Tile Resolution', [('(THIS ONLY AFFECTS PROGRAM VISIBILITY)', const.pxRes//8, 0)])])
    dialogueWindow.calculateWindowSize()
    const.surfaceFunctions.append(dialogueWindow)
    const.inputFunction = processEditPxattr
    updateRender(const.surfaceFunctions)
    const.setViewport()

def processReplaceImage(inputData): #[path]
    surfMpt.path = inputData[0]
    if os.path.exists(surfMpt.path) and surfMpt.path[-4:] == '.png' or surfMpt.path[-4:] == '.bmp':
        surfMpt.mptSurf = loadImageAsSurf(surfMpt.path)
        surfMpt.updateMptTex()
        updateRender(const.surfaceFunctions)

def promptReplaceImage():
    if not const.editing: 
        return #nothing to modify would break program
    resetDialogueWindow()
    dialogueWindow.importData('Change Tilesheet Texture',
                             [inputStarter('Image', [('IMAGE PATH:', './', 4)])])
    dialogueWindow.calculateWindowSize()
    const.surfaceFunctions.append(dialogueWindow)
    const.inputFunction = processReplaceImage
    updateRender(const.surfaceFunctions)
    const.setViewport()


def mptShowAttributes():
    mouse.resetSurfaces()
    if not const.editing:
        return
    surfMpt.showAttributes = not surfMpt.showAttributes
    updateRender(const.surfaceFunctions)

def processEditProgramSize(inputData):
    const.globalRes = inputData[0]

    surfAttr.createDestRect(surfMpt.destRect.x + surfMpt.destRect.w)
    surfAttr.attrSrcRect = rect(0, 0, 256, 256)
    surfAttr.updateTex()

    if not const.editing:
        surfMpt.createNoPxattr()
    else:
        surfMpt.formatFile()

    surfAttr.createDestRect(surfMpt.destRect.x + surfMpt.destRect.w)
    surfAttr.textOffset = surfAttr.destRect.x

    const.updateWindowSize(surfMpt.destRect.w, surfMpt.destRect.h, surfAttr.destRect.w)

    txtMpt.updateString(10, const.windowHeight - (16*const.globalRes))
    txtAttributes.updateString(surfAttr.textOffset, const.windowHeight - (16*const.globalRes))

    selectBox.destRect = rect((mouse.tilePos[0] * const.globalRes * 16) - (1 * const.globalRes),
                              (mouse.tilePos[1] * const.globalRes * 16) - (1 * const.globalRes),
                              18 * const.globalRes,
                              18 * const.globalRes)

    if not const.editing:
        surfMpt.createNoPxattr()
    else:
        surfMpt.formatFile


    updateRender(const.surfaceFunctions)

def promptEditProgramSize():
    resetDialogueWindow()
    dialogueWindow.importData('Edit Program Resolution',
                            [inputStarter('Program Resolution', [('WINDOW SIZE:', const.globalRes, 0)])])
    dialogueWindow.calculateWindowSize()
    const.surfaceFunctions.append(dialogueWindow)
    const.inputFunction = processEditProgramSize
    updateRender(const.surfaceFunctions)
    const.setViewport()