from constants import *
from pxattr import *
from surfaces import *
from filebar import *
os.environ["PYSDL2_DLL_PATH"] = "./"


filebar = fileMenuBar(const.windowWidth, 20)
filebar.formatOptions(optionList)

filebarWidth = const.windowWidth
filebarHeight = 20

#render functions [].
const.surfaceFunctions.extend([bg,
                        surfMpt,
                        surfAttr,
                        txtMpt,
                        txtAttributes,
                        selectBox,
                        filebar])
updateRender(const.surfaceFunctions)

const.window.show()
updateRender(const.surfaceFunctions)


mouse.interactableSurfaces = [filebar]
#surfMpt and others get added when editing is enabled (const.editing)
filebarSurfaces = [filebar]

running = True
#MAIN PROGRAM LOOP:
while running:
    events = sdl2.ext.get_events()
    for event in events:
        #Mouse Events:
        if event.type == sdl2.SDL_MOUSEBUTTONUP:
            mouse.clickedOnDown = False
            if mouse.stayClicked == True: #disables stay clicked
               if mouse.touchedSurface is not None:
                    mouse.touchedSurface.offClick()
            else: #thing to do on release.
                mouse.clickedOnRelease = True
                if mouse.touchedSurface is not None:
                    mouse.touchedSurface.handleCursorIntersect() #this gets cleared pretty soon after.
    
            if mouse.toDeleteSurface:
                dialogueWindow.destroy()
                mouse.touchedSurface = None
                mouse.toDeleteSurface = False

        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            mouse.clickedOnDown = True
            if mouse.touchedSurface is not None:
                mouse.touchedSurface.handleCursorIntersect()

        if event.type == sdl2.SDL_MOUSEMOTION:
            mouse.pos = (event.motion.x, event.motion.y)
            checkCursorIntersects()
            if surfMpt.attributeInfoDisplayed:
                updateRender(const.surfaceFunctions)
        
        #keyboard events:
        elif event.type == sdl2.SDL_QUIT:
            sdl2.SDL_Quit()
            running = False
            break

        if event.type == sdl2.SDL_KEYDOWN:
            #taking in keyboard input instead of text input (for stuff like esc, return ect.)
            if mouse.editingText:
                #exit text editing:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    mouse.textBeingEdited.resetText(True)
                    mouse.textBeingEdited = None
                #pressing backspace

                elif event.key.keysym.sym == sdl2.SDLK_a and sdl2.SDL_GetModState() & sdl2.KMOD_CTRL:
                    mouse.textHighlighted = True

                elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                    mouse.textEdited = True
                    if mouse.textHighlighted: #delete all of string
                        mouse.textBeingEdited.clearString(True)
                        mouse.textHighlighted = False
                    else: #delete one character from string.
                        mouse.textBeingEdited.removeFromText(True)
                #pressing enter
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    mouse.editingText = False
                    sdl2.SDL_StopTextInput()
                    mouse.textBeingEdited.exitTextEditing()
                #highlight text    
            elif const.editing:
                mod = sdl2.SDL_GetModState()
                if event.key.keysym.sym == sdl2.SDLK_z: #undo/redo
                    if len(mouse.history) == 0:
                        break
                    if mod & sdl2.KMOD_CTRL and mod & sdl2.KMOD_SHIFT:
                        redo()
                    elif mod & sdl2.KMOD_CTRL:
                        undo()

                elif event.key.keysym.sym == sdl2.SDLK_s: #save
                    if mod & sdl2.KMOD_CTRL and mod & sdl2.KMOD_SHIFT:
                        promptSaveAs()
                    elif mod & sdl2.KMOD_CTRL:
                        saveFile()
                    
                     

        #typing stuff:
        elif mouse.editingText and event.type == sdl2.SDL_TEXTINPUT:
            if mouse.textHighlighted:
                mouse.textBeingEdited.clearString(True)
                mouse.textHighlighted = False
            mouse.textEdited = True
            mouse.textBeingEdited.addToText(event.text.text, True)
    
    #waiting to import data collected from dialogue window into the associated process function
    if const.waitingForDialogueData:
        const.waitingForDialogueData = False
        const.inputFunction(const.inputFunctionData)

    if mouse.stayClicked:
        sdl2.SDL_Delay(5)
    else:
        sdl2.SDL_Delay(15)

    if time.waitForTime:
        time.updateTime()
        for func, countdown in list(time.waitTimes.items()):
            time.waitTimes[func] -= time.deltaTime #- timer
            func(time.waitTimes[func]) #run active function, and give current time.

sdl2.ext.quit()
