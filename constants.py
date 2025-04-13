import os
os.environ["PYSDL2_DLL_PATH"] = "./"
import sdl2
import sdl2.ext
import ctypes
import filedialpy #for file opening stuff

# import bootUp
sdl2.ext.init()
sdl2.sdlttf.TTF_Init()

#utility functions:
def rect(x,y,w,h):
    return sdl2.SDL_Rect(x,y,w,h)

def generateText(text, color, style):
    if style == 'bold':
        sdl2.sdlttf.TTF_SetFontStyle(const.fontKeroM, sdl2.sdlttf.TTF_STYLE_BOLD) 
    elif style == 'normal':
        sdl2.sdlttf.TTF_SetFontStyle(const.fontKeroM, sdl2.sdlttf.TTF_STYLE_NORMAL) 
    return sdl2.sdlttf.TTF_RenderUTF8_Solid(const.fontKeroM, bytes(text, 'utf-8'), color)

def loadImageAsSurf(ipath):
    return sdl2.SDL_ConvertSurface(sdl2.ext.load_image(ipath), abgr, 0)

def createBlankSurf(width, height):
    return sdl2.SDL_CreateRGBSurfaceWithFormat(0, width, height, 32, sdl2.SDL_PIXELFORMAT_ABGR32) 


def convertSurfToTex(surf):
    return sdl2.SDL_CreateTextureFromSurface(const.renderer.sdlrenderer, surf)

def convertTexToSurf(texture, width, height, pFormat):
    surf = createBlankSurf(width, height)

    sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, texture)
    
    #copy pixels from formats
    sdl2.SDL_RenderReadPixels(const.renderer.sdlrenderer, None, pFormat, surf.contents.pixels, surf.contents.pitch)

    sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, None)
    return surf

class filePaths:
    def __init__(self):
        self.pxattr = ''
        self.mptTexture = ''

        self.background = os.path.abspath('./images/background.png')

        self.attributeInfoKB = os.path.abspath('attributesKB.txt')
        self.attributeInfoPT = os.path.abspath('attributesPT.txt')
        self.attributeInfo2012 = os.path.abspath('attributes2012.txt')

        self.attributesTextureKB = os.path.abspath('./images/attributes_kero_blaster.png')
        self.attributesTexturePT = os.path.abspath('./images/attributes_kerom.png')
        self.attributesTexture2012 = os.path.abspath('./images/attributes_2012.png')

        self.selectBoxTexture = os.path.abspath('./images/select_box.png')
        self.infoDialogueTexture = os.path.abspath('./images/info_window.png')
        self.font = os.path.abspath(b'./KeroM.ttf')

        self.buttons = os.path.abspath('./images/buttons.png')

paths = filePaths()

class settings:
    def __init__(self):
        self.globalRes = 2
        self.pxRes = 8
        self.windowWidth = 542
        self.windowHeight = 537

        self.window = sdl2.ext.Window("pxAttribute", size=(self.windowWidth, self.windowHeight))
        self.renderer = sdl2.ext.Renderer(self.window)
        sdl2.SDL_SetRenderDrawColor(self.renderer.sdlrenderer, 0, 0, 0, 0)

        self.surfaceFunctions = []

        self.editing = False
        self.placeOdd = True
        self.waitingForDialogueData = False #for the dialogue window to send data if needed.
        self.inputFunction = None #function to input all of the data into.
        self.inputFunctionData = None #func parameters


        #fonts
        self.fontKeroM = sdl2.sdlttf.TTF_OpenFont(paths.font, ctypes.c_int(16))

    def editDrawColor(self, r,g,b,a):
        sdl2.SDL_SetRenderDrawColor(self.renderer.sdlrenderer, r, g, b, a)

    def editPxRes(self, num):
        """
        PxRes (Resolution) is the tile size.

        PiTest uses a resolution of 1 for all of its stages.
        Despite this being for the level format, this edits the rects of the tile, 
        displacing where the attributes actually lay on the grid of tiles.

        Resolution makes it so you can where the attributes would lay if
        the level resolution was set to something different.
        """
        self.pxRes = 8*num

    def updateWindowSize(self, mptWidth, mptHeight, attrWidth):
        self.windowWidth = mptWidth + attrWidth + 50
        self.windowHeight = max(mptHeight, attrWidth) + 70 #50 + 20 (20 is for filebar.)

        sdl2.SDL_SetWindowSize(self.window.window, self.windowWidth, self.windowHeight)
        sdl2.SDL_RenderSetLogicalSize(self.renderer.sdlrenderer, self.windowWidth, self.windowHeight)
        recreateTextures(self.surfaceFunctions)
        self.setViewport()

    def setViewport(self):
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, None)
        sdl2.SDL_RenderSetViewport(self.renderer.sdlrenderer, None)

    def editWindowName(self, name):
        sdl2.SDL_SetWindowTitle(self.window.window, bytes(name, 'utf-8'))

const = settings()

#mouse data also kind of acts like the object for all control in the program.
class mouseData:
    def __init__(self):
        self.pos = (-1, -1)
        self.tilePos = (0, 0) #if position is 0,0. user will not be able to have first placement be on tile 0,0
        self.attribute = 0
        
        self.history = [] #stores edit history in tuple. position is also tuple (oldAttribute, newAttribute, (x, y))
        self.historyIndex = -1

        self.touchedSurface = None #surface the mouse is over.
        self.interactedSurface = None #surface that mouse clicked.

        self.clickedOnDown = False
        self.clickedOnRelease = False

        # self.clicked = False
        self.selectBox = False
        self.stayClicked = False

        #for typing text:
        self.editingText = False
        self.textEdited = False #if this is false it doesn't clear things when exited out of thing
        self.textBeingEdited = None #object and then object function relating to specific text function is called.
        self.textHighlighted = False #higlight text and stuff

        self.toDeleteSurface = False #to delete a surface.

        # self.interactableSurfaces = [None]

    def setSurfaceToEntireScreen(self, surface): #if a thing wants to take up the whole screen so no other surfaces can be clicked
        if not hasattr(self, 'backup'):
            self.backup = self.interactableSurfaces
        else:
            for surf in self.interactableSurfaces:
                if surf is not surface and surf not in self.backup:
                    self.backup.append(surf)

        self.interactableSurfaces = [surface]

    def resetSurfaces(self): #opposite of setSurfaceToEntireScreen()
        self.interactableSurfaces = self.backup
        
    def updateHistory(self, val):
        # Trim redo history if we've undone and are now editing
        if self.historyIndex < len(self.history) - 1:
            self.history = self.history[:self.historyIndex + 1]

        self.history.append(val)
        self.historyIndex += 1

        # Cap history length
        if len(self.history) > 255:
            del self.history[0]
            self.historyIndex -= 1  # Shift index to match new base
        


    #a flag is set in mouse to delete a surface, because I can't really delete surfaces from within class code.

class timer:
    def __init__(self):
        self.lastTime = sdl2.SDL_GetTicks()
        self.updateTime()

        self.waitForTime = False
        self.waitTimes = {} #Function: Time (Int)

    def updateTime(self):
        self.time = sdl2.SDL_GetTicks()
        self.deltaTime = self.time - self.lastTime
        self.lastTime = self.time

    def addToTimes(self, func, time):
        self.lastTime = sdl2.SDL_GetTicks()
        self.updateTime()
        self.waitTimes[func] = time
        self.waitForTime = True

    def removeTime(self, time):
        del self.waitTimes[time]
        self.waitForTime = False

time = timer()

mouse = mouseData()

#const.editDrawColor(23, 22, 47, 255)

abgr = sdl2.SDL_AllocFormat(sdl2.SDL_PIXELFORMAT_RGBA8888)
colRed = 0x00FF0000
colGreen = 0x0000FF00
colBlue = 0x000000FF
colTrans = 0x00000000
colWhite = sdl2.SDL_Color(255, 255, 255)

def checkCursorIntersects():
    for rct in mouse.interactableSurfaces:
        if rct.destRect.x <= mouse.pos[0] <= rct.destRect.x + rct.destRect.w:
            if rct.destRect.y <= mouse.pos[1] <= rct.destRect.y + rct.destRect.h:
                rct.handleCursorIntersect()
                mouse.touchedSurface = rct
                return rct #rct (rect) is the surface.
            elif rct.mouseHover:
                rct.offClick()
                mouse.touchedSurface = None
                mouse.clickedOnRelease = False
        elif rct.mouseHover:
            rct.offClick()
            mouse.touchedSurface = None
            mouse.clickedOnRelease = False

def recreateTextures(formatFunctions): #also for recreating textures because window resize mess program up.
    for surf in formatFunctions:
        surf.recreateTextures()


def updateRender(renderFunctions):
    for surf in renderFunctions:
        surf.render()
    const.setViewport()
    const.renderer.present()
