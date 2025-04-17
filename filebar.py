from constants import *
from surfaces import *
from fakeWindow import *
from miscFunctions import *

os.environ["PYSDL2_DLL_PATH"] = "./"


def resetRenderer():
    sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, None)

class option():
    def __init__(self, text, dropdownText, dropdownFunctions):
        self.text = text #str
        self.dropdownText = dropdownText
        self.dropdownFunctions = dropdownFunctions
        
        self.dropdownSelectedEntry = -1
        self.xOffset = 0 #offset for destRect.

        self.createOptionTexture() #self.optionTex
        self.createDropdownTexture()
        
        #self.normalSrcRect = rect(0, 0, 0, 0)
        #self.highlightedSrcRect = rect(0, 0, 0, 0)
        #self.clickedSrcRect = rect(0, 0, 0, 0)
        
        self.clicked = False
        self.mouseHover = False #for when option is clicked, so it can highlight others.

    def createOptionTexture(self):
        textNormalSurf = generateText(self.text, sdl2.SDL_Color(74, 85, 84), 'bold')
        textHighlightedSurf = generateText(self.text, sdl2.SDL_Color(77, 104, 82), 'bold')
        textClickedSurf = generateText(self.text, sdl2.SDL_Color(51, 71, 66), 'bold')

        textWidth = textNormalSurf.contents.w
        self.optionWidth = textNormalSurf.contents.w + 20
        self.optionTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.optionWidth * 3,
                20
        )
        pixformat = ctypes.c_uint32()
        sdl2.SDL_QueryTexture(self.optionTex, pixformat, None, None, None)

        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.optionTex)
        
        #normal (bg)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 130, 109, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(0, 0, self.optionWidth, 20))

        #highlighted (bg)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 104, 153, 109, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(self.optionWidth, 0, self.optionWidth, 20))
        #highlighted (emboss (light color, top, left))
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 148, 176, 131, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, self.optionWidth+1, 1, (self.optionWidth*2)-3, 1)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, self.optionWidth+1, 1, self.optionWidth+1, 17)
        #highlighted (emboss (darkish color, right, bottom))
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 72, 98, 99, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, self.optionWidth+2, 18, (self.optionWidth*2)-2, 18)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, (self.optionWidth*2)-2, 18, (self.optionWidth*2)-2, 2)

        #clicked (bg)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 77, 104, 82, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(self.optionWidth*2, 0, self.optionWidth, 20))
        #clicked (emboss (darkish color, top, left), (using rect because double thickness.))
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 51, 71, 66, 255)
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect((self.optionWidth*2), 1, self.optionWidth-3, 2))
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect((self.optionWidth*2), 0, 2, 18))
        #clicked (emboss (light color, bottom, right))
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 130, 109, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, (self.optionWidth*2)+2, 18, (self.optionWidth*3)-2, 18)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, (self.optionWidth*3)-3, 18, (self.optionWidth*3)-3, 3)

        #outline
        xOffset = 0
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 58, 73, 112, 255)
        for text in [textNormalSurf, textHighlightedSurf, textClickedSurf]:
            tex = convertSurfToTex(text)
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, tex, None, rect(xOffset + 3, 2, textWidth, 12))
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(xOffset-1, 0, self.optionWidth, 20))

            sdl2.SDL_DestroyTexture(tex)
            xOffset += self.optionWidth
        
        sdl2.SDL_FreeSurface(textNormalSurf)
        sdl2.SDL_FreeSurface(textHighlightedSurf)
        sdl2.SDL_FreeSurface(textClickedSurf)
        const.setViewport()
        self.normalSrcRect = rect(0, 0, self.optionWidth, 20)
        self.highlightedSrcRect = rect(self.optionWidth, 0, self.optionWidth, 20)
        self.clickedSrcRect = rect(self.optionWidth*2, 0, self.optionWidth, 20)

    def createDropdownTexture(self):
        #get longest text entry
        longest = 0
        dropdownTextTexturesNormal = []
        dropdownTextTexturesHighlighted = []
        
        for text in self.dropdownText:
            textTex = generateText(text, sdl2.SDL_Color(51, 71, 66), 'bold')
            dropdownTextTexturesNormal.append(textTex)
            dropdownTextTexturesHighlighted.append(generateText(text, sdl2.SDL_Color(69, 113, 84), 'bold'))
            if textTex.contents.w > longest:
                longest = textTex.contents.w
        
        self.dropdownWidth = longest + 50
        self.dropdownHeight = 20 * len(self.dropdownText) + 2

        self.dropdownNormalTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.dropdownWidth,
                self.dropdownHeight 
        )
        self.dropdownHighlightedTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.dropdownWidth,
                self.dropdownHeight 
        )
        dropdownButtonsTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.dropdownWidth,
                40
        )

        #in previous versions i render copied using a texture as both the source texture, and destination texture.
        #and I'm pretty sure that that caused memory issues, and corrupted the texture, so the solution is to make
        #a third texture to copy from.

        yPos = 0 

        #Normal Dropdown Button:
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, dropdownButtonsTex)
        #fill background
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 77, 104, 82, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)
        #drawing single button (to be copied later on for all entries); draw outline
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 51, 71, 66, 255)
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(1, yPos, self.dropdownWidth - 2, 20))
        #button shine
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 130, 109, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 2, yPos + 19, self.dropdownWidth - 3, yPos + 19)
             
        yPos += 20

        #Highlighted Dropdown Button:
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 147, 109, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(0, yPos, self.dropdownWidth, 20))
        #emboss (shine, top, left)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 148, 176, 131, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 0, yPos, self.dropdownWidth - 3, yPos)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 1, yPos, 1, yPos + 18)
        #emboss (dark, bottom, right)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 74, 85, 84, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 2, yPos + 19, self.dropdownWidth - 2, yPos + 19)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, self.dropdownWidth - 2, yPos + 1, self.dropdownWidth - 2, yPos + 19)

        #draw button, and then copy it throughout surface.
        def copyButtonThroughoutSurface(yOffsetAmount, srcTex, destTex, lst):
            sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, destTex)
            srcRect = rect(0, yOffsetAmount, self.dropdownWidth, 20)
            yOffset = 0
            for option in lst:
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, srcTex, srcRect, rect(0, yOffset, self.dropdownWidth, 20))
                yOffset += 20
            yOffset = 0
            for option in lst:
                textTex = convertSurfToTex(option)

                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, textTex, None, rect(3, yOffset + 2, option.contents.w, 12))
                sdl2.SDL_DestroyTexture(textTex)
                sdl2.SDL_FreeSurface(option)
                yOffset += 20
            #Outline
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(0, -1, self.dropdownWidth, self.dropdownHeight+1))

        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 58, 73, 112, 255)
        copyButtonThroughoutSurface(0, dropdownButtonsTex, self.dropdownNormalTex, dropdownTextTexturesNormal)
        copyButtonThroughoutSurface(20, dropdownButtonsTex, self.dropdownHighlightedTex, dropdownTextTexturesHighlighted)
        sdl2.SDL_DestroyTexture(dropdownButtonsTex)
        del dropdownButtonsTex

optionFile = option('FILE', ['Open', 'New', 'Save', 'Save As...', 'File Info'], [openFile, promptCreatePxattr, saveFile, promptSaveAs, fileInfo])
optionEdit = option('EDIT', ['Undo', 'Redo', 'Replace Image', 'File Data'], [undo, redo, promptReplaceImage, promptEditPxattr])
optionHelp = option('VIEW', ['Show Attributes', 'Program Resolution'], [mptShowAttributes, promptEditProgramSize])

optionList = [optionFile, optionEdit, optionHelp]

class fileMenuBar:
    def __init__(self, width, height): #options
        self.width = width
        self.height = height

        self.mouseHover = False

        self.drawMenuBar()

        #for cursor interactions and such:

    def drawMenuBar(self):
        self.tex = sdl2.SDL_CreateTexture(
            const.renderer.sdlrenderer,
            sdl2.SDL_PIXELFORMAT_RGB888,
            sdl2.SDL_TEXTUREACCESS_TARGET,
            self.width,
            self.height
        )
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.tex)

        #make surface green
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 130, 109, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)

        #dark green
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 72, 98, 99, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(1, 13, self.width - 2, 6))

        #shine
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 148, 176, 131, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(1, 1, self.width - 2, 2))

        #set render target back to window:
        const.setViewport()

    #creating options dest rects and positions
    def formatOptions(self, options):

        self.options = options
        self.curOption = self.options[0]

        #get width of all the buttons:
        offsetAmount = 0
        for option in self.options:
            option.xOffset = offsetAmount

            option.destRect = rect(offsetAmount - 1, 0, option.optionWidth, 20)
            offsetAmount = option.destRect.x + option.optionWidth 
        self.totalOptionsWidth = offsetAmount
        self.destRect = rect(0, 0, self.totalOptionsWidth, 20)

        self.optionsTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.totalOptionsWidth,
                20 
        )
        self.optionsDestRect = rect(0, 0, offsetAmount, 20)
        
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.optionsTex)
        for option in self.options:
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.optionTex, option.normalSrcRect, option.destRect)
        const.setViewport()

    def recreateTextures(self):
        self.drawMenuBar()
        for option in self.options:
            sdl2.SDL_DestroyTexture(option.optionTex)
            sdl2.SDL_DestroyTexture(option.dropdownNormalTex)
            sdl2.SDL_DestroyTexture(option.dropdownHighlightedTex)
            option.createOptionTexture()
            option.createDropdownTexture()

    def handleCursorIntersect(self):
        self.mouseHover = True
        checkYOffset = False #check yOffset for if mouse interactable surface is entire screen.
        toUpdateRender = False


        #if user is drawing with attributes then don't do anything
        if mouse.stayClicked:
            return
        
        const.setViewport()
        #Checking if mouse is in range of dropdown menu:
        if self.curOption.clicked:
            checkYOffset = True #filebar takes up all of screen, so checking y is necessary for option buttons at the top.
            #in range of dropdown:
            if self.curOption.xOffset <= mouse.pos[0] <= self.curOption.xOffset + self.curOption.dropdownWidth:
                if 20 <= mouse.pos[1] <= 20 + self.curOption.dropdownHeight:
                    #weird math to find what entry mouse is over
                    #entry gets clamped because there is an outline to the dropdown menu that interfers with it and gives it entries over the index range.
                    entry = ((mouse.pos[1]-20)//19)
                    entry = max(min(len(self.curOption.dropdownText)-1, entry), 0)
                    if entry != self.curOption.dropdownSelectedEntry:
                        self.curOption.dropdownSelectedEntry = entry
                        toUpdateRender = True
                    if mouse.clickedOnRelease:
                        mouse.clickedOnDown = False
                        mouse.clickedOnRelease = False
                        
                        self.curOption.dropdownFunctions[entry]()
                        self.offClick()

                        self.destRect = rect(0, 0, const.windowWidth, 20)
                        mouse.touchedSurface = None
                        return

                elif self.curOption.dropdownSelectedEntry != -1:
                    self.curOption.dropdownSelectedEntry = -1
                    toUpdateRender = True

            elif self.curOption.dropdownSelectedEntry != -1:
                self.curOption.dropdownSelectedEntry = -1
                toUpdateRender = True

        unclickOptions = False

        for option in self.options:
            if checkYOffset: #when dropdown menu is active, the surface destrect is the entire screen. because normally, mouse interactions are only checked when the mouse is at the top of the screen.
                if not 0 <= mouse.pos[1] <= 20:
                    break

            #criteria:
            #if mouse over it: highlight
            #if mouse not over it, but highlight = true: unhighlight
            #if mouse over it, and button clicked: click

            if option.destRect.x <= mouse.pos[0] <= option.destRect.x + option.destRect.w:
                if not option.mouseHover and not option.clicked:
                    option.mouseHover = True
                    toUpdateRender = True
                if mouse.clickedOnDown:
                    if option.clicked:
                        option.clicked = False
                        option.mouseHover = True
                        self.destRect = rect(0, 0, const.windowWidth, 20)
                    else:
                        option.clicked = True
                        self.curOption = option
                        unclickOptions = True
                        self.destRect = rect(0, 0, const.windowWidth, const.windowHeight)
                        mouse.setSurfaceToEntireScreen(self)
                    toUpdateRender = True
                    mouse.clickedOnDown = False

            else:
                if option.mouseHover:
                    option.mouseHover = False
                    toUpdateRender = True

        if unclickOptions:
            for option in self.options:
                if option.clicked and option != self.curOption:
                    option.clicked = False

        if toUpdateRender:
            updateRender(const.surfaceFunctions)

        mouse.clickedOnRelease = False
        mouse.clickedOnDown = False

    def resetMouseHover(self, hoverOption):
        for option in self.options:
            if option != hoverOption:
                option.mouseHover = False
                option.clicked = False

        #Option has new state, so we check all other entries to remove their state if they have the same state.
        #(This is because it indexes downwards, so we have to reiterate the list to make sure we don't make a mistake.)
        #when mouse is no longer hovering over the file bar:
    def offClick(self):
        self.mouseHover = False
        for option in self.options:
            option.dropdownSelectedEntry = -1
            option.clicked = False
            option.mouseHover = False
        self.curOption = self.options[0]
        updateRender(const.surfaceFunctions)


    def render(self):
        const.setViewport()
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.tex, None, rect(0, 0, const.windowWidth, 20))
        for option in self.options:
            if option.clicked:
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.optionTex, option.clickedSrcRect, option.destRect) 
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.dropdownNormalTex, None, rect(option.xOffset, 20, option.dropdownWidth, option.dropdownHeight))
                if option.dropdownSelectedEntry != -1:
                    srcRect = rect(0, option.dropdownSelectedEntry*20, option.dropdownWidth, 20)
                    destRect = rect(option.xOffset, (option.dropdownSelectedEntry*19)+option.dropdownSelectedEntry+20, option.dropdownWidth, 20)
                    sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.dropdownHighlightedTex, srcRect, destRect)
            elif option.mouseHover:
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.optionTex, option.highlightedSrcRect, option.destRect) 
            else:
               sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, option.optionTex, option.normalSrcRect, option.destRect) 

renderAmount = 0
