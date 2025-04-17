from constants import *
import ctypes

os.environ["PYSDL2_DLL_PATH"] = "./"


#TODO:
#make variation of window that shows text only.
#add blinking cursor animation for text editing

buttonsSurf = loadImageAsSurf(paths.buttons)
buttonsTexture = convertSurfToTex(buttonsSurf)
sdl2.SDL_FreeSurface(buttonsSurf)

class inputField: #contains the header for field section and the attributes
    #type 0 = int, type 1 = directory, type 2 = bool, type 3 = string, type 4 = file path
    def __init__(self, text, defaultInput, type):
        self.text = text
        self.type = type
        self.realInput = defaultInput
        self.defaultInput = self.encode(defaultInput)
        self.userInput = ''

        self.textTex = createEmptyTexture()
        
        self.active = False #if active then render highlighted

        self.textXPos = 0
        self.textYPos = 0

    def encode(self, value):
        if self.type == 0:
            value = str(value)
        elif self.type == 1:
            value = str(value)
        elif self.type == 2:
            pass
        return value

    def decode(self, value):
        if self.type == 0: #int
            value = int(value)
        return value
        

    def createText(self, color, typeInput): #generates text texture and also checks if text fits in box.
        if typeInput == 0:
           typeInput = self.defaultInput
        elif typeInput == 1:
           typeInput = self.userInput
        
        sdl2.SDL_DestroyTexture(self.textTex)
        if len(str(typeInput)) == 0: #No text at all, so don't generate text texture because it will create a null pointer.
            self.textTex = sdl2.SDL_CreateTexture(const.renderer.sdlrenderer,
                                    sdl2.SDL_PIXELFORMAT_RGBA8888,
                                    sdl2.SDL_TEXTUREACCESS_TARGET,
                                    10,
                                    12)
            self.textSrcRect = rect(0, 0, 10, 12)
            self.textDestRect = rect(self.textXPos, self.textYPos, 10, 12)
        else: #generate text because it WON'T result in a null pointer
            textSurf = generateText(typeInput, color, 'normal')
            if textSurf.contents.w <= 46: #text width is less than 46 means it fits into the box so it's not cropped
                self.textSrcRect = rect(0, 0, textSurf.contents.w, 12)
                self.textDestRect = rect(self.textXPos, self.textYPos, textSurf.contents.w, 12)
            else: #text is too long to fit in box so it's cropped
                self.textSrcRect = rect(textSurf.contents.w - 46, 0, textSurf.contents.w, 12)
                self.textDestRect = rect(self.textXPos - 2, self.textYPos, 46, 12)
            self.textTex = convertSurfToTex(textSurf)
            sdl2.SDL_FreeSurface(textSurf)

    def disable(self):
        self.disabled = True
        #probably more things.

class inputStarter: #contains the name for the following inputfields and the list of inputfields
    def __init__(self, text, inputFields):
        self.headerText = text
        self.formatAttributes(inputFields)
        self.fieldAreaTextTextures = [] #textures for input field text.
        
        self.checkDisabled = False 

    def formatAttributes(self, inputFields):
        self.inputFields = []
        for attribute in inputFields:
            attribute = inputField(attribute[0], attribute[1], attribute[2])
            self.inputFields.append(attribute)

    def disableOptions(self):
        for option in self.disableOptions:
            option.disable()

class miniWindow:
    def __init__(self):
        #self.returnData = None!
        # self.editFriendly = True #non edit friendly only shows text and stuff.
        pass #just exist

    def importData(self, header, inputFields):
        self.headerText = header
        self.inputFields = inputFields #packed full of inputstarters

        self.mouseHover = False
        self.clicked = False
        self.clickedOnButton = False

    def destroy(self): #delete surface
        mouse.textBeingEdited = None
        mouse.textEdited = False
        mouse.textHighlighted = None

        mouse.clickedOnDown = False
        mouse.stayClicked = False
        mouse.clickedOnRelease = False

        mouse.touchedSurface = None
        const.surfaceFunctions.remove(self)
        mouse.resetSurfaces()

        sdl2.SDL_DestroyTexture(self.windowTex)


        sdl2.SDL_DestroyTexture(self.inputFieldNormalTex)
        sdl2.SDL_DestroyTexture(self.inputFieldHighlightedTex)

        sdl2.SDL_DestroyTexture(self.inputFieldButtonsTex)
        sdl2.SDL_DestroyTexture(self.inputFieldTextTex)

        for tex in self.buttons[1:]: #tex is a tuple, [1] is texture index. Also index 0 is x button, and destroying it would be stupid.
            sdl2.SDL_DestroyTexture(tex[1])

        for entry in self.inputFields:
            for tex in entry.fieldAreaTextTextures:
                sdl2.SDL_DestroyTexture(tex)

        # for inputField in self.inputFields:
        #     for field in inputField.inputFields:
        #         del field
        #     del inputField
        # del self.inputFields
        
        updateRender(const.surfaceFunctions)


    def calculateWindowSize(self):

        #creating textures for all of the text. And checking how big they would be.
        windowHeaderLength = 0
        inputStarterHeaderLength = 0
        inputFieldTextLength = 0

        self.fieldHeaderTextTextures = []

        textColor = sdl2.SDL_Color(207, 219, 199)

        self.headerTextSurf = generateText(self.headerText, textColor, 'bold')
        headerWidth = self.headerTextSurf.contents.w * 2 #sprite is 2 times big.
        headerHeight = self.headerTextSurf.contents.h * 2

        windowHeaderLength = headerWidth
        self.headerTextTex = convertSurfToTex(self.headerTextSurf)
        sdl2.SDL_FreeSurface(self.headerTextSurf)


        self.height = 29 #header height
        #self.height accumulates height through this loop:
        for entry in self.inputFields:
            entryTextSurf = generateText(entry.headerText, textColor, 'bold')
            if entryTextSurf.contents.w > inputStarterHeaderLength:
                inputStarterHeaderLength = entryTextSurf.contents.w
            self.height += 18 #input field header height
            entryTextTex = convertSurfToTex(entryTextSurf)
            sdl2.SDL_FreeSurface(entryTextSurf)

            self.fieldHeaderTextTextures.append(entryTextTex)
            for attribute in entry.inputFields:
                attributeTextSurf = generateText(attribute.text, textColor, 'bold')
                if attributeTextSurf.contents.w + 67 > inputFieldTextLength:
                    inputFieldTextLength = attributeTextSurf.contents.w + 67
                self.height += 17 #input field height

                attributeTextTex = convertSurfToTex(attributeTextSurf)
                entry.fieldAreaTextTextures.append(attributeTextTex)
                sdl2.SDL_FreeSurface(attributeTextSurf)

            self.height += 17 #height until next header.
        self.height += 30 #height to botom.
                
        self.width = max(windowHeaderLength + 36,
                        inputStarterHeaderLength,
                        inputFieldTextLength)
       
        self.windowTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.width,
                self.height
        )

        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.windowTex)
        #filling in background
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 105, 130, 109, 255)
        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)
        #shine
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 148, 176, 131, 255)
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(3, 2, self.width - 6, 2)) #top
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 2, 2, 2, self.height - 5)
        #shade
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 72, 98, 99, 255)
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(2, self.height - 4, self.width - 5, 2))
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, self.width - 3, self.height - 3, self.width - 3, 4)
        #outline
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 58, 73, 112, 255)
        sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(0, 0, self.width, self.height))

        fieldHeaderIndex = 0
        fieldAreaIndex = 0
        textYPos = 29
        
        #I'm iterating through the self.inputFields list instead of the list of textures
        #because the list of textures is not always proportional to the size of the inner list of field attributes
        #so it could cause out of bounds index issues.
        
        #Also the Y Position is determined from like all of the elements, so that's why they seem to just be randomly
        #placed, but I assure you they're not.
        #top of bar line:
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 72, 98, 99, 255)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 6, 28, self.width - 3, 28)
        sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 6, self.height - 30, self.width - 6, self.height - 30) #line at bottom
        
        #TEXT:
        #header:
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.headerTextTex, None, rect(7, 2, headerWidth, headerHeight))

        self.activeField = None #for what field's being edited.

        for fieldHeader in self.inputFields: 
            textWidth = ctypes.c_long(0)
            sdl2.SDL_QueryTexture(self.fieldHeaderTextTextures[fieldHeaderIndex], None, None, textWidth, None)

            fieldHeader.destRect = rect(7, textYPos, textWidth, 12)
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.fieldHeaderTextTextures[fieldHeaderIndex], None, fieldHeader.destRect)
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, textWidth.value + 9, textYPos + 7, self.width - 6, textYPos + 7)  #aesthetic line
            textYPos += 18 #padding to next part
            for fieldArea in fieldHeader.fieldAreaTextTextures:
                textWidth = ctypes.c_long(0)
                sdl2.SDL_QueryTexture(fieldArea, None, None, textWidth, None)
                
                xPos = self.width - (60+textWidth.value) #text is aligned to the right.
                fieldHeader.inputFields[fieldAreaIndex].destRect = rect(xPos, textYPos, textWidth, 12)

                #destRect for the input fields (not the text but the buttons themselves:)
                if fieldHeader.inputFields[fieldAreaIndex].type != 2:
                    fieldHeader.inputFields[fieldAreaIndex].inputDestRect = rect(self.width - 58, textYPos + 1, 52, 16)
                else: #if it's a bool...
                    fieldHeader.inputFields[fieldAreaIndex].inputDestRect = rect(self.width - 58, textYPos - 1, 16, 16)
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, fieldArea, None, fieldHeader.inputFields[fieldAreaIndex].destRect)
                textYPos += 18
                fieldAreaIndex += 1
            textYPos += 16
            fieldAreaIndex = 0
            fieldHeaderIndex += 1

        for tex in self.fieldHeaderTextTextures:
            sdl2.SDL_DestroyTexture(tex)
            
        #BUTTONS:

        self.createInputFieldTextures()

        self.inputFieldButtonsTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGBA8888, #transparency
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.width,
                self.height
        )

        self.inputFieldTextTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGBA8888, #transparency
                sdl2.SDL_TEXTUREACCESS_TARGET,
                self.width,
                self.height
        )

        sdl2.SDL_SetTextureBlendMode(self.inputFieldButtonsTex, sdl2.SDL_BLENDMODE_BLEND)
        sdl2.SDL_SetTextureBlendMode(self.inputFieldTextTex, sdl2.SDL_BLENDMODE_BLEND)
        mouse.setSurfaceToEntireScreen(self)

        #buttons
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldButtonsTex)
        for entry in self.inputFields:
            for field in entry.inputFields:
                if field.type == 2:
                    if field.defaultInput == False:
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, buttonsTexture, rect(66, 0, 16, 16), field.inputDestRect)
                    else:
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, buttonsTexture, rect(50, 0, 16, 16), field.inputDestRect)
                else:
                    sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldNormalTex, None, field.inputDestRect)
                    entry.inputFields[fieldAreaIndex].textXPos = self.width - 54
                    entry.inputFields[fieldAreaIndex].textYPos = field.inputDestRect.y + 2
                    entry.inputFields[fieldAreaIndex].createText(sdl2.SDL_Color(51, 71, 66), 0) #color of text, default or user input
                fieldAreaIndex += 1
            fieldAreaIndex = 0

        #okay and cancel buttons.
        cancelButtonTex, cancelButtonNormalRect, cancelButtonPressedRect = self.drawButton('CANCEL')
        okayButtonTex, okayButtonNormalRect, okayButtonPressedRect = self.drawButton('OKAY')

        #(buttonDestRect, buttonTex, buttonNormalRect, buttonPressedRect, function)
        self.buttons = [(rect(self.width - 27, 5, 25, 25), buttonsTexture, rect(0, 0, 25, 25), rect(25, 0, 25, 25), self.close), #X button
                        (rect(0, self.height - 24, cancelButtonNormalRect.w, cancelButtonNormalRect.h), cancelButtonTex, cancelButtonNormalRect, cancelButtonPressedRect, self.close),
                        (rect(0, self.height - 24, okayButtonNormalRect.w, okayButtonNormalRect.h), okayButtonTex, okayButtonNormalRect, okayButtonPressedRect, self.saveAndClose)]
        
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.windowTex)
        #xbutton is special.
        print(type(buttonsTexture))
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.buttons[0][1], self.buttons[0][2], self.buttons[0][0])
        offset = self.width - 3
        for tup in self.buttons[1:]:
            offset -= (7 + tup[2].w) #adjust offset
            tup[0].x = offset #adjust button rect
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, tup[1], tup[2], tup[0]) #render copy to window tex
        self.buttonIndex = -1

        #text
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldTextTex)
        for entry in self.inputFields:
            for field in entry.inputFields:
                if field.type != 2: #bools don't have text
                    sdl2.SDL_RenderCopy(const.renderer.sdlrenderer,
                                        entry.inputFields[fieldAreaIndex].textTex,
                                        entry.inputFields[fieldAreaIndex].textSrcRect,
                                        entry.inputFields[fieldAreaIndex].textDestRect)
                fieldAreaIndex += 1
            fieldAreaIndex = 0

        #center = width and a half, and then stupid math to center both orgins.
        xPos = ((const.windowWidth - (const.windowWidth//2)) - (self.width - (self.width//2)))
        yPos = ((const.windowHeight - (const.windowHeight//2)) - (self.height - (self.height//2)))

        self.windowDestRect = rect(xPos, yPos, self.width, self.height)
        self.destRect = rect(0, 0, const.windowWidth, const.windowHeight)

        const.setViewport()
        updateRender(const.surfaceFunctions)

    def drawButton(self, text):
        #texture is twice as big for both normalTex and pressedTex
        width = ctypes.c_int()
        sdl2.sdlttf.TTF_SizeText(const.fontKeroM, bytes(text, 'utf-8'), width, None)  
        width = width.value + 16
        tex = sdl2.SDL_CreateTexture(const.renderer.sdlrenderer,
                               sdl2.SDL_PIXELFORMAT_RGB888,
                               sdl2.SDL_TEXTUREACCESS_TARGET,
                               width * 2,
                               16)
        
        def drawButtonTex(xPos, bgColor, shineColor, shadeColor, textColor): #*bgColor
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, *bgColor, 255)
            sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, rect(xPos, 0, width, 16))
            
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, *shineColor, 255)
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, xPos+1, 13, xPos+1, 1) #up
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, xPos+1, 1, xPos+width-2, 1) #right
            
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, *shadeColor, 255)
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, xPos+2, 14, xPos+width-1, 14) #right
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, xPos+width-2, 14, xPos+width-2, 2)#up
            #outline
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 51, 71, 66, 255)
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(xPos, 0, width, 16))

            textSurf = generateText(text, textColor, 'bold')
            textTex = convertSurfToTex(textSurf)
            sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, textTex, None, rect(xPos + 8, 1, textSurf.contents.w, textSurf.contents.h))
            sdl2.SDL_FreeSurface(textSurf)
            sdl2.SDL_DestroyTexture(textTex)

        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, tex)
        drawButtonTex(0, (105, 130, 109), (148, 176, 131), (72, 98, 99), sdl2.SDL_Color(207, 219, 199))
        drawButtonTex(width, (77, 104, 82), (68, 85, 101), (105, 130, 109), sdl2.SDL_Color(51, 71, 66))
            
        normalRect = rect(0, 0, width, 16)
        pressedRect = rect(width, 0, width, 16)
        return tex, normalRect, pressedRect

    def createInputFieldTextures(self):
        def drawInputField(tex, bgCol, shadeCol, shineCol, outlineCol):
            sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, tex)
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, bgCol[0], bgCol[1], bgCol[2], 255)
            sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, None)
        
            #blue shine thing
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, shadeCol[0], shadeCol[1], shadeCol[2], 255)
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(1, 1, 53, 17))
            
            #shine at bottom:
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, shineCol[0], shineCol[1], shineCol[2], 255)
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(2, 14, 49, 2))
            sdl2.SDL_RenderDrawLine(const.renderer.sdlrenderer, 50, 15, 50, 1)

            #outline:
            sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, outlineCol[0], outlineCol[1], outlineCol[2], 255)
            sdl2.SDL_RenderDrawRect(const.renderer.sdlrenderer, rect(0, 0, 52, 16))        

        self.inputFieldNormalTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                52,
                16
        )
        self.inputFieldHighlightedTex = sdl2.SDL_CreateTexture(
                const.renderer.sdlrenderer,
                sdl2.SDL_PIXELFORMAT_RGB888,
                sdl2.SDL_TEXTUREACCESS_TARGET,
                52,
                16
        )

        drawInputField(self.inputFieldNormalTex, (77, 104, 82), (68, 85, 101), (105, 130, 109), (51, 71, 66))
        drawInputField(self.inputFieldHighlightedTex, (105, 130, 109), (72, 98, 99), (148, 176, 131), (51, 71, 66))

    def moveDestRect(self):
        """ Moves the rectangle while dragging based on mouse position. """

        # Move the rectangle by the same difference
        self.windowDestRect.x = mouse.pos[0] - self.startX
        self.windowDestRect.y = mouse.pos[1] - self.startY
        updateRender(const.surfaceFunctions)

        # self.render()

    def offClick(self):
        mouse.stayClicked = False
        pass

    def handleCursorIntersect(self):
        """ Handles mouse clicks to initiate dragging. """
        
        mouseX = mouse.pos[0] - self.windowDestRect.x #dest rect takes up all of screen so we have to get the "real" mouse position
        mouseY = mouse.pos[1] - self.windowDestRect.y
        #self.buttonRects[]

        mouseOverPart = False #if statements do weird stuff lol
        rerenderInputFields = False
        if mouse.stayClicked:
            self.moveDestRect()
        
        #mouse not on window.
        elif not[self.windowDestRect.x <= mouseX <= self.windowDestRect.x + self.windowDestRect.w and self.windowDestRect.y <= mouseY <= self.windowDestRect.y + self.windowDestRect.h]:
             mouse.clickedOnDown = False
             mouse.clickedOnRelease = False
             return

        #if mouse clicked on button and check if released on button:
        elif self.clickedOnButton and mouse.clickedOnRelease:
            self.clickedOnButton = False
            mouse.clickedOnRelease = False
            for index, tup in enumerate(self.buttons): #(buttonDestRect, buttonTex, buttonNormalRect, buttonPressedRect, function)
                if tup[0].x <= mouseX <= tup[0].x + tup[0].w and tup[0].y <= mouseY <= tup[0].y + tup[0].h and index == self.buttonIndex:
                    tup[4]()
                    return
            #if not on anything, rerender everything as normal...
            sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.windowTex)
            for tup in self.buttons:
                sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, tup[1], tup[2], tup[0])
            const.setViewport()
            updateRender(const.surfaceFunctions)

        elif mouse.clickedOnDown:
            #check input fields
            #check other buttons
            #else: move window.
            if (self.width - 58) <= mouseX <= self.width - 6:
                sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 183, 31, 112, 255)
                for entry in self.inputFields:
                    for fieldAttribute in entry.inputFields:
                        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, fieldAttribute.inputDestRect)

                        #check if it's on any of the buttons:
                        if fieldAttribute.type == 2: #if on bool
                            if mouseX <= self.width - 42:
                                if fieldAttribute.inputDestRect.y <= mouseY <= fieldAttribute.inputDestRect.y + 12: #if mouse in range
                                    if mouse.editingText: #since a bool was just clicked. it should stop editing the text.
                                        mouse.textBeingEdited.saveText(self.activeField, False)
                                        #set text field to normal
                                        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldButtonsTex)
                                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldNormalTex, None, self.activeField.inputDestRect)
                                        const.setViewport()

                                        self.activeField = None
                                        mouse.editingText = False
                                        break
                                    if fieldAttribute.defaultInput == False: #turn bool on
                                        fieldAttribute.defaultInput = True

                                    else: #turn bool off
                                        fieldAttribute.defaultInput = False
                                
                                    rerenderInputFields = True
                                    mouseOverPart = True
                                    mouse.editingText = False
                                    break
                                
                        #if on input field.
                        elif fieldAttribute.inputDestRect.y <= mouseY <= fieldAttribute.inputDestRect.y + 12:
                            #select path:
                            if fieldAttribute.type == 1 or fieldAttribute.type == 4:
                                if fieldAttribute.type == 1:
                                    fTitle="Select a folder (Just select a file in the folder you want to use.)"
                                else:
                                    fTitle="Select Image File"
                                path = filedialpy.openFile(initial_dir="./",
                                            title=fTitle,
                                )
                                if fieldAttribute.type == 1: #get directory instead
                                    path = os.path.dirname(os.path.abspath(path)) +'/'
                                fieldAttribute.defaultInput = path
                                fieldAttribute.userInput = path
                                fieldAttribute.createText(sdl2.SDL_Color(51, 71, 66), 1)
                                self.replaceTextTex(fieldAttribute)
                                mouse.editingText = False
                                mouse.textBeingEdited = None
                                self.renderInputFields()
                                mouse.clickedOnDown = False
                                return
                            else:
                                if self.activeField == fieldAttribute:
                                    #runs mouse over part which off clicks on the field.
                                    break
                                self.activeField = fieldAttribute
                                self.activeField.active = True
                                sdl2.SDL_StartTextInput()
                                mouse.editingText = True
                                mouse.textBeingEdited = self
                            rerenderInputFields = True
                            # self.checkDisabled(entry) #fix this
                            mouseOverPart = True
                            break
                            
            if not mouse.editingText:
                for index, button in enumerate(self.buttons):
                    if button[0].x <= mouseX <= button[0].x + button[0].w and button[0].y <= mouseY <= button[0].y + button[0].h:
                        self.clickedOnButton = True
                        self.buttonIndex = index
                        mouse.clickedOnDown = False
                        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.windowTex)
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, button[1], button[3], button[0]) #render normal again
                        const.setViewport()
                        updateRender(const.surfaceFunctions)
                        return

            if mouseOverPart == False: #off click
                if 0 <= mouseX <= self.windowDestRect.w and 0 <= mouseY <= self.windowDestRect.h:
                    if mouse.editingText:
                        self.activeField = None
                        rerenderInputFields = True
                        mouse.editingText = False

                    mouse.stayClicked = True  # Start dragging

                    # Record the initial click position relative to the rectangle
                    self.mouseXPos = mouse.pos[0]
                    self.mouseYPos = mouse.pos[1]
                    self.startX = mouse.pos[0] - self.windowDestRect.x
                    self.startY = mouse.pos[1] - self.windowDestRect.y
            # Reset click flag
            mouse.clickedOnDown = False

        if rerenderInputFields:
            self.renderInputFields()

        if mouse.stayClicked:
            if self.startX != mouse.pos[0] or self.startY != mouse.pos[1]:
                self.moveDestRect()

    def renderInputFields(self): #for rerendering all of them after something happens (like one get's pressed.)
        #this renders the buttons... and it should render text too???
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldButtonsTex)

        for entry in self.inputFields:
            for field in entry.inputFields:
                if field.type == 2:
                    sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldButtonsTex)
                    if field.defaultInput == False:
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, buttonsTexture, rect(66, 0, 16, 16), field.inputDestRect)
                    else:
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, buttonsTexture, rect(50, 0, 16, 16), field.inputDestRect)              
                #for text stuff.
                elif field.active:
                    sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldButtonsTex)
                    if field == self.activeField:
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldHighlightedTex, None, field.inputDestRect)
                        field.createText(sdl2.SDL_Color(76, 56, 51), 0) #highlighted
                        self.replaceTextTex(field)
                    else: #not the right one, disable
                        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldNormalTex, None, field.inputDestRect)
                        if mouse.textEdited: #if any edits were made
                            self.saveText(field, False)
                            mouse.textEdited = False
                        else:
                            field.createText(sdl2.SDL_Color(51, 71, 66), 0)
                            self.replaceTextTex(field)
                    
                        # const.setViewport()
                        field.active = False
        const.setViewport()
        updateRender(const.surfaceFunctions)

    
    def close(self): #function exists to work for cancel button.
        mouse.toDeleteSurface = True

    def saveAndClose(self):
        returnTuple = []
        mouse.editingText = False
        sdl2.SDL_StopTextInput()
        for field in self.inputFields:
            for input in field.inputFields:
                if input.type != 2:
                    self.saveText(input, False)
                input.defaultInput = input.decode(input.defaultInput)
                returnTuple.append(input.defaultInput)
        const.waitingForDialogueData = True
        const.inputFunctionData = returnTuple
        self.close()
        return

    def replaceTextTex(self, field): #erase parts of text texture and then add new text texture to it
        sdl2.SDL_SetRenderTarget(const.renderer.sdlrenderer, self.inputFieldTextTex)
        sdl2.SDL_SetRenderDrawColor(const.renderer.sdlrenderer, 0, 0, 0, 0)

        sdl2.SDL_RenderFillRect(const.renderer.sdlrenderer, field.inputDestRect)

        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer,
                            field.textTex,
                            field.textSrcRect,
                            field.textDestRect)
        
    def addToText(self, stringPart, render):
        if self.activeField.type == 0: #if an int
            if stringPart not in {b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9'}:
                return
        self.activeField.userInput += stringPart.decode('utf-8')
        self.activeField.createText(sdl2.SDL_Color(76, 56, 51), 1)

        #erase text portion and then draw over it
        self.replaceTextTex(self.activeField)
        const.setViewport()
        if render:
            updateRender(const.surfaceFunctions)

    def removeFromText(self, render):
        self.activeField.userInput = self.activeField.userInput[:-1]
        self.activeField.createText(sdl2.SDL_Color(76, 56, 51), 1)

        self.replaceTextTex(self.activeField)
        const.setViewport()
        if render:
            updateRender(const.surfaceFunctions)

    def clearString(self, render): #clear while still in edit mode (ctrl+a del)
        self.activeField.userInput = ''
        self.activeField.createText(sdl2.SDL_Color(76, 56, 51), 1)

        self.replaceTextTex(self.activeField)
        const.setViewport()
        if render:
            updateRender(const.surfaceFunctions)

    def resetText(self, render):
        self.activeField.userInput = self.activeField.defaultInput
        self.activeField.createText(sdl2.SDL_Color(51, 71, 66), 0)

        self.replaceTextTex(self.activeField)
        const.setViewport()
        mouse.editingText = False
        self.activeField.active = False
        if render:
           updateRender(const.surfaceFunctions)

    def copyFromText(): #TODO
        pass

    def pasteIntoText(): #TODO
        pass

    def saveText(self, field, render): #enter
        if mouse.textEdited: #so it doesn't clear things when you click on an input field and exit out of it.
           field.defaultInput = field.userInput
        field.createText(sdl2.SDL_Color(51, 71, 66), 0)
        self.replaceTextTex(field)
        const.setViewport()
        field.active = False
        if render:
           self.render()

    def exitTextEditing(self):
        self.activeField = None
        self.renderInputFields()

    def recreateTextures(self): #broken. Also is never used so it does not matter...
        pass
        # self.calculateWindowSize()
    
    def render(self):
        const.setViewport()
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.windowTex, None, self.windowDestRect)
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldButtonsTex, None, self.windowDestRect)
        sdl2.SDL_RenderCopy(const.renderer.sdlrenderer, self.inputFieldTextTex, None, self.windowDestRect)

dialogueWindow = miniWindow()

def resetDialogueWindow():
    for attr in list(dialogueWindow.__dict__):
        if not callable(getattr(dialogueWindow, attr)):  # Check if it's not a function
            delattr(dialogueWindow, attr)
