from constants import *
from pxattr import *
os.environ["PYSDL2_DLL_PATH"] = "./"


class background:
    def __init__(self, destRects):
        self.img = loadImageAsSurf(paths.background)
        self.destRects = destRects
        self.tex = createEmptyTexture()

        self.createBackground() #creates self.tex

    def createBackground(self):
        sdl2.SDL_DestroyTexture(self.tex)
        bg = createBlankSurf(const.windowWidth, const.windowHeight) #background surf (the whole window)
        bgSizeX = 0
        bgSizeY = 0
        #surveying how many times the background image has to be pasted over the window size:
        while bgSizeY < const.windowHeight:
            while bgSizeX < const.windowWidth:
                sdl2.SDL_BlitSurface(self.img, None, bg, rect(bgSizeX, bgSizeY, 64, 64))
                bgSizeX += 64
            bgSizeY += 64
            bgSizeX = 0
        #outline around it.
        for surf in self.destRects:
            sdl2.SDL_FillRect(bg, rect(surf.destRect.x-2, surf.destRect.y-2, surf.destRect.w+4, surf.destRect.h+4), 0x050A08FF)
            sdl2.SDL_FillRect(bg, surf.destRect, 0x0D0F16FF)
        self.tex = convertSurfToTex(bg)
        sdl2.SDL_FreeSurface(bg)
    
    def recreateTextures(self):
        self.createBackground()

    def render(self):
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.tex, None, None)

class selectionBox:
    def __init__(self):
        surf = loadImageAsSurf(paths.selectBoxTexture)
        self.tex = convertSurfToTex(surf)
        sdl2.SDL_FreeSurface(surf)

        self.surface = None
        self.srcRect = None
        self.destRect = rect(0, 0, 18*const.globalRes, 18*const.globalRes)

    def render(self):
        if self.surface is not None and const.editing:
            sdl2.SDL_RenderSetViewport(const.renderer.sdlrenderer, self.surface)
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.tex, None, self.destRect)

selectBox = selectionBox()

class txt:
    def __init__(self, string, **variables):
        self.template = string
        self.variables = variables
        self.string = self.template.format(**self.variables)

        self.tex = createEmptyTexture()

    def updateString(self, xoffset, yoffset):
        self.string = self.template.format(**self.variables)
        sdl2.sdlttf.TTF_SetFontStyle(const.fontKeroM, sdl2.sdlttf.TTF_STYLE_NORMAL)
        surf = sdl2.sdlttf.TTF_RenderUTF8_Solid(const.fontKeroM, bytes(self.string, 'utf-8'), colWhite)
        
        sdl2.SDL_DestroyTexture(self.tex)
        self.tex = convertSurfToTex(surf)

        self.srcRect = rect(0,0, surf.contents.w, surf.contents.h)
        self.destRect = rect(xoffset, yoffset, surf.contents.w * const.globalRes, surf.contents.h * const.globalRes)
        sdl2.SDL_FreeSurface(surf)


    def render(self):
        const.setViewport()
        sdl2.SDL_RenderCopy(
            const.renderer.sdlrenderer,
            self.tex,
            self.srcRect,
            self.destRect
        )

txtMpt = txt("mpt size: (W={w}, H={h}); Game: {game}", w=0, h=0, game="None")
txtAttributes = txt("Attribute: [{attr}]", attr=0)

class attributeSurface:
    def __init__(self, attrPath):
        self.attrPath = attrPath
        self.attrSurf = loadImageAsSurf(attrPath)
        self.tex = createEmptyTexture()

        self.srcRect = rect(0, 0, 256, 256)

        self.mouseHover = False
    
    def recreateTextures(self):
        self.updateTex()
    
    def render(self):
        sdl2.SDL_RenderSetViewport(const.renderer.sdlrenderer, self.destRect)
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.tex, self.srcRect, None)
    
    def createDestRect(self, x):
        self.destRect = rect(
            x + 30,
            (4 * const.globalRes) + 20,
            256 * const.globalRes,
            256 * const.globalRes
        )

    def updateTex(self):
        sdl2.SDL_DestroyTexture(self.tex)
        self.tex = convertSurfToTex(self.attrSurf)

    def handleCursorIntersect(self):
        self.mouseHover = True
        if not const.editing:
            return
        mouse.surface = 1
        #I DO NOT REMEMBER WHAT MOUSE.DRAWING IS FOR SO JUST LIKE IN THE FUTURE FIX THIS.
        if not mouse.stayClicked:
            self.attribute = ((mouse.pos[1]-self.destRect.y)//const.globalRes//16) * 16 + (mouse.pos[0]-self.destRect.x)//const.globalRes//16
            if mouse.clickedOnDown:
               if self.attribute != mouse.attribute or selectBox.surface is not self.destRect:
                    mouse.attribute = self.attribute
                    mouse.surface = 1
                    #selectbox stuff...
                    selectBox.surface = self.destRect
                    #rounding mouse position to nearest multiple. num - (num%divisor)
                    xPos = (mouse.pos[0] - self.destRect.x) - ((mouse.pos[0] - self.destRect.x)%(16 * const.globalRes))
                    yPos = (mouse.pos[1] - self.destRect.y) - ((mouse.pos[1] - self.destRect.y)%(16 * const.globalRes))
                    selectBox.destRect = rect(xPos - (1 * const.globalRes), yPos - (1 * const.globalRes), 18 * const.globalRes, 18 * const.globalRes)
                    txtAttributes.variables['attr'] = mouse.attribute
                    txtAttributes.updateString(self.textOffset, const.windowHeight - (16*const.globalRes))
                    #num - (num%divisor)
                    #convert mouse to pixel value than, round number down to nearest multiple
                    
                    updateRender(const.surfaceFunctions)

    def offClick(self):
        self.mouseHover = False
        return
       
class attributeInfoDialogue:
    def __init__(self):
       attributeInfoImgSurf = loadImageAsSurf(paths.infoDialogueTexture)
       self.attributeInfoImgTex = convertSurfToTex(attributeInfoImgSurf)
       sdl2.SDL_FreeSurface(attributeInfoImgSurf)

       self.attributeInfoTex = createEmptyTexture()

    def updateTexture(self, attribute):
        bottomTextSurf = generateText(findAttributeText(attribute), sdl2.SDL_Color(201, 200, 206), 'normal')
        headerTextSurf = generateText('Attribute: [{attr}]'.format(attr=attribute), sdl2.SDL_Color(201, 200, 206), 'normal')
        self.infoTexWidth = max(bottomTextSurf.contents.w + 6, headerTextSurf.contents.w + 7)

        sdl2.SDL_DestroyTexture(self.attributeInfoTex)
        self.attributeInfoTex = sdl2.SDL_CreateTexture(
            const.renderer.sdlrenderer,
            sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_TARGET,
            self.infoTexWidth,
            32
        )
        sdl2.SDL_SetTextureBlendMode(self.attributeInfoTex, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.attributeInfoTex)

        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 32, 31, 38, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(3, 0, self.infoTexWidth - 5, 32))

        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 19, 18, 22, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 3, 14, self.infoTexWidth-3, 14)

        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.attributeInfoImgTex, rect(0, 0, 4, 32), rect(0, 0, 4, 32))
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.attributeInfoImgTex, rect(4, 0, 4, 32), rect(self.infoTexWidth - 4, 0, 4, 32))



        bottomTextTex = convertSurfToTex(bottomTextSurf)
        headerTextTex = convertSurfToTex(headerTextSurf)

        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, headerTextTex, None, rect(4, 0, headerTextSurf.contents.w, 12))
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, bottomTextTex, None, rect(4, 16, bottomTextSurf.contents.w, 12))

        sdl2.SDL_FreeSurface(headerTextSurf)
        sdl2.SDL_FreeSurface(bottomTextSurf)
        const.setViewport()

    def render(self):
        const.setViewport()
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.attributeInfoTex, None, rect(mouse.pos[0]+10, mouse.pos[1]+14, self.infoTexWidth, 32))

attributeInfoDlg = attributeInfoDialogue()
    

class mptSurface:
    def __init__(self, path):
        self.path = path
        self.width = 16
        self.height = 16

        self.mptSurf = createBlankSurf(0, 0)
        # self.attributeSurf = createBlankSurf(0, 0)

        self.mptTex = createEmptyTexture()
        self.tileTex = createEmptyTexture()
        self.createNoPxattr()
        
        self.fileSelected = False
        self.selectedTile = (0, 0)
        
        self.width = 16
        self.height = 16

        self.mouseHover = False
        self.useImage = False
        self.showAttributes = True

        self.attributeInfoDisplayed = False
        self.attributeInfoImg = loadImageAsSurf(paths.infoDialogueTexture)

    def formatFile(self):
        self.fileSelected = True

        self.width = pxattr.width
        self.height = pxattr.height
        txtMpt.variables['w'] = pxattr.width
        txtMpt.variables['h'] = pxattr.height
        if pxattr.version == 0:
            txtMpt.variables['game'] = "Kero Blaster"
        elif pxattr.version == 1:
            txtMpt.variables['game'] = "Pitest"
        elif pxattr.version == 2:
            txtMpt.variables['game'] = "2012 Era"

        self.createDestRect()

        self.generateTiles(pxattr.attributeArray)
        self.updateTileTex()
        
        #update window size if affected changes mess up program orientation
        if const.windowWidth != self.destRect.w + (256*const.globalRes) + 50 or const.windowHeight != max(self.destRect.h, 256*const.globalRes)+70:
            const.updateWindowSize(self.destRect.w, self.destRect.h, 256 * const.globalRes)

        if os.path.exists(self.path) and self.path[-4:] == '.png' or self.path[-4:] == '.bmp' and self.useImage:
            sdl2.SDL_FreeSurface(surfMpt.mptSurf)
            surfMpt.mptSurf = loadImageAsSurf(self.path)
            surfMpt.updateMptTex() 
        else:
            surfMpt.createNoImage()
        
        #we have to move surfaces to adjust for new mpt size
        surfAttr.createDestRect(self.destRect.x + self.destRect.w)
        txtMpt.updateString(self.destRect.x, const.windowHeight - (16*const.globalRes))
        if txtMpt.destRect.x + txtMpt.destRect.w > surfAttr.destRect.x:
            surfAttr.textOffset = const.windowWidth - (txtAttributes.destRect.w + 16)
        else:
            surfAttr.textOffset = surfAttr.destRect.x
        txtAttributes.updateString(surfAttr.textOffset, const.windowHeight - (16*const.globalRes))

        bg.createBackground()

        const.editing = True
        updateRender(const.surfaceFunctions)
        if self not in mouse.interactableSurfaces:
            if self not in mouse.backup:
                mouse.backup.append(self)
        #I know this is bad code, but I can't think of another way to implement this
        if surfAttr not in mouse.interactableSurfaces:
            if surfAttr not in mouse.backup:
                mouse.backup.append(surfAttr)
        mouse.resetSurfaces()

    def createNoImage(self): #no image
        sdl2.SDL_DestroyTexture(self.mptTex)
        self.mptTex = sdl2.SDL_CreateTexture(
                                const.renderer.sdlrenderer,
                                sdl2.SDL_PIXELFORMAT_RGB888,
                                sdl2.SDL_TEXTUREACCESS_TARGET,
                                (self.width * const.pxRes) * const.globalRes,
                                (self.height * const.pxRes) * const.globalRes
                                )
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.mptTex)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 13, 15, 22, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)
        const.setViewport()

    def createNoPxattr(self): #screen for no pxattr file: (Also placeholders for mptTex and)
        self.destRect = rect(4 * const.globalRes,
                             (4 * const.globalRes) + 20,
                             187 * const.globalRes,
                             45 * const.globalRes
        )
        #mptTex is replaced with this so it doesnt really matter.
        #for editing window size:
        sdl2.SDL_DestroyTexture(self.mptTex)
        self.mptTex = sdl2.SDL_CreateTexture(
                                const.renderer.sdlrenderer,
                                sdl2.SDL_PIXELFORMAT_RGB888,
                                sdl2.SDL_TEXTUREACCESS_TARGET,
                                187,
                                45
        )
        self.mptSrcRect = rect(0, 0, 187, 45)
        #232B44
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.mptTex)

        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 13, 15, 22, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)
        
        textColor = sdl2.SDL_Color(166, 165, 165, 255)

        line0 = sdl2.sdlttf.TTF_RenderUTF8_Solid(const.fontKeroM, bytes('No .pxattr loaded!', 'utf-8'), textColor)
        line1 = sdl2.sdlttf.TTF_RenderUTF8_Solid(const.fontKeroM, bytes('Create or Open a pxattr file', 'utf-8'), textColor)
        line2 = sdl2.sdlttf.TTF_RenderUTF8_Solid(const.fontKeroM, bytes('To use this program.', 'utf-8'), textColor)

        line0 = convertSurfToTex(line0)
        line1 = convertSurfToTex(line1)
        line2 = convertSurfToTex(line2)
        
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, line0, None, rect(6, 3, 97, 12))
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, line1, None, rect(6, 17, 157, 12))
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, line2, None, rect(6, 31, 112, 12))
        const.setViewport()
        #creating placeholders

        self.tileSurf = createBlankSurf(0, 0)
        self.tileSrcRect = rect(0, 0, 0, 0)

    def createDestRect(self):
        self.destRect = rect(
                            4 * const.globalRes,
                            (4 * const.globalRes) + 20, #20 is filebar height
                            (self.width * const.pxRes) * const.globalRes,
                            (self.height * const.pxRes) * const.globalRes
        )
        self.mptSrcRect = rect(
                       0,
                       0,
                       pxattr.width * 8,
                       pxattr.height * 8
        )
        surfMpt.tileSrcRect = rect(
                       0,
                       0,
                       (pxattr.width * const.pxRes) * const.globalRes,
                       (pxattr.height * const.pxRes) * const.globalRes
        )

    def updateMptTex(self):
        sdl2.SDL_DestroyTexture(self.mptTex)
        self.mptTex = convertSurfToTex(self.mptSurf)

    def updateTileTex(self):
        sdl2.SDL_DestroyTexture(self.tileTex)
        self.tileTex = convertSurfToTex(self.tileSurf)
    
    def generateTiles(self, attributesArray): #assigns self.attributeTiles
        xPos = 0
        yPos = 0
        sdl2.SDL_FreeSurface(self.tileSurf)
        self.tileSurf = blank = createBlankSurf(self.width * const.pxRes, self.height * const.pxRes)
        #resolution only matters to surface, not blitting
        for row in attributesArray:
            for column in row:
                sdl2.SDL_BlitSurface(
                    self.attributeSurf,
                    rect((column % 16) * 16, (column // 16) * 16, 16, 16),
                    self.tileSurf,
                    rect(xPos, yPos, 16, 16)
                )
                xPos += 16
            xPos = 0
            yPos += 16

    def handleCursorIntersect(self):
        toUpdateRender = False
        self.mouseHover = True
        tilePos = ((mouse.pos[0] - self.destRect.x)//16//const.globalRes, (mouse.pos[1] - self.destRect.y)//16//const.globalRes)

        if mouse.clickedOnDown:
            if tilePos[0]+1 > pxattr.width or tilePos[1]+1 > pxattr.height: #out of pxattr array bounds
                mouse.clickedOnDown = False
                mouse.stayClicked = False
                return
                  
            if tilePos != mouse.tilePos:
                toUpdateRender = True
                mouse.tilePos = tilePos
            #set selection box dest rect

            #I think it has to make a new rect every time and that's kind of extensive????
            selectBox.surface = self.destRect
            
            selectBox.destRect.x = (mouse.tilePos[0] * const.globalRes * 16) - (1 * const.globalRes)
            selectBox.destRect.y = (mouse.tilePos[1] * const.globalRes * 16) - (1 * const.globalRes)

            mouse.stayClicked = True
            
            #to make sure if tile is the exact same as before it doesn't place anything there.
            if pxattr.attributeArrayEdit[mouse.tilePos[1]][mouse.tilePos[0]] != mouse.attribute:
                mouse.updateHistory((pxattr.attributeArrayEdit[mouse.tilePos[1]][mouse.tilePos[0]],
                                     mouse.attribute, (mouse.tilePos[0], mouse.tilePos[1])))
                pxattr.pxEdit(mouse.attribute)
                self.editTile(mouse.attribute)

                toUpdateRender = True
        else:
            mouse.stayClicked = False

        if not self.attributeInfoDisplayed:
            self.mousePos = mouse.tilePos
            self.tilePos = tilePos #mouse.tilePos is for the tile edited, not the tile it's over.
            time.addToTimes(surfMpt.timerActiveAttributeInfo, 680)
            
        elif self.attributeInfoDisplayed:
            if tilePos != self.tilePos:
                self.attributeInfoDisplayed = False
                const.surfaceFunctions.remove(attributeInfoDlg)
                updateRender(const.surfaceFunctions)

        if toUpdateRender:
           updateRender(const.surfaceFunctions)

    def recreateTextures(self):
        sdl2.SDL_DestroyTexture(self.mptTex)
        sdl2.SDL_DestroyTexture(self.tileTex)
        self.updateMptTex()
        self.updateTileTex()

    def render(self):
        sdl2.SDL_RenderSetViewport(const.renderer.sdlrenderer, self.destRect)
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.mptTex, self.mptSrcRect, None)
        if self.showAttributes:
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.tileTex, self.tileSrcRect, None)


    def editTile(self, attribute):
        if not const.editing:
            return
        
        sdl2.SDL_FillRect(self.tileSurf, rect(mouse.tilePos[0]*16, mouse.tilePos[1]*16, 16, 16), 0x00000000)
        sdl2.SDL_BlitSurface(
            self.attributeSurf,
            rect((attribute % 16) * 16, (attribute // 16) * 16, 16, 16),
            self.tileSurf,
            rect(mouse.tilePos[0]*16, mouse.tilePos[1]*16, 16, 16)
        )
        self.updateTileTex()
        return
    
    def offClick(self):
        self.mouseHover = False
        return
    
    def timerActiveAttributeInfo(self, timeVal):
        tilePos = ((mouse.pos[0] - self.destRect.x)//16//const.globalRes, (mouse.pos[1] - self.destRect.y)//16//const.globalRes)
        if tilePos != self.tilePos:
            if self.timerActiveAttributeInfo in time.waitTimes:
                time.removeTime(self.timerActiveAttributeInfo)
        if timeVal <= 0:
            #I think you should create an object so it can follow the mouse around while it moves
            self.attributeInfoDisplayed = True

            attribute = pxattr.attributeArrayEdit[self.tilePos[1]][self.tilePos[0]]
            attributeLine = findAttributeText(attribute)

            attributeInfoDlg.updateTexture(attribute)            
            time.removeTime(self.timerActiveAttributeInfo)

            const.surfaceFunctions.append(attributeInfoDlg)
            updateRender(const.surfaceFunctions)


surfMpt = mptSurface('')

surfAttr = attributeSurface(paths.attributesTextureKB)
surfAttr.createDestRect(surfMpt.destRect.x + surfMpt.destRect.w)
surfAttr.attrSrcRect = rect(0, 0, 256, 256)
surfAttr.updateTex()
surfAttr.textOffset = surfAttr.destRect.x

surfMpt.attributeSurf = createBlankSurf(256, 256)

const.updateWindowSize(surfMpt.destRect.w, surfMpt.destRect.h, surfAttr.destRect.w)
bg = background([surfMpt, surfAttr])

txtMpt.updateString(10, const.windowHeight - (16*const.globalRes))
txtAttributes.updateString(surfAttr.textOffset, const.windowHeight - (16*const.globalRes))

