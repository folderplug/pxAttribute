import os
os.environ["PYSDL2_DLL_PATH"] = "./"
from re import M
from constants import *

# from constants import *

class pxattrProcess:
    def __init__(self):
        self.path = ''
        self.savePath = 'NULL.pxattr'
        self.fileName = '.pxattr'
    
        self.header = b''
        self.version = 255 #0 = Kero Blaster; 1 = Pitest; 2 = Pre 0.116 Starfrog/Rockfish 2011
        
        self.width = 16
        self.height = 16
        
        self.compression = 0
        self.attributes = []
        self.attributeArray = [[]]

        self.attributeArrayEdit = [[]] #pxattr from memory

    @staticmethod
    def UInt(x, file): #int from read file
        return int.from_bytes(file.read(x), 'little')
    
    def pxOpen(self, path): #opens - reads file - converts to list.
        with open(path, 'rb') as file:
            self.fileName = os.path.basename(path)
            const.editWindowName('pxAttribute: {path}'.format(path=self.fileName))
            self.savePath = path
            self.header = file.read(8) #TODO: include starfrog 0.103 and 0.104 support. (Also Rockfish support I think.)
            if self.header == b'kmMAP02\x00':
               self.version = 1
               const.editPxRes(1)
               const.placeOdd = False#kerom

               self.width = self.UInt(2, file)
               self.height = self.UInt(2, file)
               self.compression = self.UInt(1, file)
            elif self.header == b'pxMAP01\x00':
               self.version = 0
               const.editPxRes(2)
               const.placeOdd = True

               self.width = self.UInt(2, file)
               self.height = self.UInt(2, file)
               self.compression = self.UInt(1, file)
              #kero blaster
            else: 
                self.width = int.from_bytes(self.header[0:2], 'little')
                self.height = int.from_bytes(self.header[2:4], 'little')
                
                #get file size.
                file.seek(0, os.SEEK_END)
                remainingFileSize = file.tell() - 4

                if self.width*self.height == remainingFileSize:
                    self.version = 2 
                    self.compression = 0
                    const.editPxRes(2)
                    const.placeOdd = True
                    file.seek(4)
                else:
                    raise ValueError("bad header")

            self.size = self.width*self.height
            if self.size < 1: raise ValueError('ERROR: pxattr size is invalid.')

            attributes = self.pxRead(self.size, self.compression, self.version, file)
            file.close()
            # const.editing = True
            if self.compression == 2: #Vertical
                self.attributeArray = self.pxArray(attributes, False)
                # self.attributes = [attribute for sublist in self.attributeArray for attribute in sublist] #flattens array.
            else: 
                self.attributeArray = self.pxArray(attributes, False) #convert lists to arrays

    def pxCreate(self, fileName, version, width, height): #assigns class attributes - creates file.
        self.path = fileName
        self.savePath = fileName
        self.version = version
        if version == 0:
            self.header = b'pxMAP01\x00'
        elif version == 1:
            self.header = b'kmMAP02\x00'
        elif version == 2:
            self.header = b''

        self.width = width
        self.height = height
        self.attributeArray = [[0 for x in range(self.width)] for y in range(self.height)] 
        self.attributeArrayEdit = self.attributeArray
        #create file:
        # self.pxWrite(self.version, self.compression)
               
    def pxRead(self, size, compression, version, file): #Read pxattr attribute data.
        if compression != 0: file.read(4)    
        attributes = []

        if version == 0 or version == 2: #Kero Blaster
            if compression == 0:
                attributes = list(file.read())
            else: #Kero Blaster Compression
                while len(attributes) < size:
                    attributes.extend([self.UInt(1, file)]*self.UInt(1, file))
                    
        elif version == 1: #KeroM
            attribute = file.read(2)
            if compression == 0:
                repeat = 0
                while len(attributes) < size:
                    nextAttribute = file.read(2)
                    repeat += 1
                    if nextAttribute != attribute: #in kerom attributes have xy ids.
                        attributes.extend([attribute[0]+(attribute[1]*16)]*repeat) #(attribute[0] is x and [1] is y)
                        attribute = nextAttribute; repeat = 0 #move to next attribute, reset repeat.         
            else: #KeroM Compression
                while len(attributes) < self.size:
                    repeat = self.UInt(2, file)
                    attributes.extend([attribute[0]+(attribute[1]*16)]*repeat)
                    attribute = file.read(2)
        return attributes
          
    def pxEdit(self, attribute):
        #[0] tile, [1] inner tuple with x and y info
        #subslice into array with tuple in [y][x] format.
        self.attributeArrayEdit[mouse.tilePos[1]][mouse.tilePos[0]] = attribute

    def pxResize(self, sizeX, sizeY):

        if sizeX == self.width and sizeY == self.height: #size is same
            return
        
        #width
        if self.width > sizeX: #sizeX less than width
            for row in self.attributeArrayEdit:
                del row[sizeX:]
        elif self.width < sizeX: #sizeX more than width
            for row in self.attributeArrayEdit:
                row.extend([0] * (sizeX - self.width))

        # Resize height
        if self.height > sizeY: #sizeY less than height
            del self.attributeArrayEdit[sizeY:]
        elif self.height < sizeY: #sizeY more than height
            for _ in range(sizeY - self.height):
                self.attributeArrayEdit.append([0] * sizeX)

        self.width = sizeX
        self.height = sizeY

        
    #TEMP:
    def pxSave(self):
        if self.savePath[-7:] != '.pxattr':
            self.savePath += '.pxattr'
        with open(self.savePath, 'wb') as file:
            if self.version == 1:
                file.write(b'kmMAP02\x00')
            elif self.version == 0:
                file.write(b'pxMAP01\x00')
                
            #doesn't write anything for header if version 2

            file.write(self.width.to_bytes(2, 'little'))
            file.write(self.height.to_bytes(2, 'little'))
            if self.version in range(0, 2): #rockfish doesnt have tile compression
                file.write(self.compression.to_bytes(1, 'little'))
            
            if self.version == 1 and self.compression == 0: #keroM
                for attributes in self.attributeArrayEdit:
                    for attribute in attributes:
                        file.write((attribute%16).to_bytes(1)+(attribute//16).to_bytes(1))
            elif self.compression != 0: #if compression exists
                compressedAttributes = self.pxCompress(self.version, self.compression)
                file.write(len(compressedAttributes).to_bytes(4, 'little')+bytes(compressedAttributes))#writing byte size and bytes
            else: #kero blaster no compression
                for attributes in self.attributeArrayEdit:
                    file.write(bytes(attributes))          
        file.close()


    def pxSaveAs(self):
        savePath = filedialpy.saveFile(initial_dir="./",
                                            initial_file=self.fileName,
                                            title="Save pxAttr file.",
                                            filter=["*.pxattr"]
        )
        if savePath != '':
            self.savePath = savePath
            self.pxSave()
        else:
            return
    
    def pxWrite(self, game, compression):
        with open(self.savePath, 'wb') as file:
            if game == 0:
                file.write(b'pxMAP01\x00')
            elif game == 1:
                file.write(b'kmMAP02\x00')

            file.write(self.width.to_bytes(2, 'little'))
            file.write(self.height.to_bytes(2, 'little'))
            if game in range(0, 2):
                file.write(compression.to_bytes(1, 'little'))
            
            if game == 1 and compression == 0: #keroM
                for attributes in self.attributeArrayEdit:
                    for attribute in attributes:
                        file.write((attribute%16).to_bytes(1)+(attribute//16).to_bytes(1))
            elif compression != 0: #if compression exists
                compressedAttributes = self.pxCompress(game, compression)
                file.write(len(compressedAttributes).to_bytes(4, 'little')+bytes(compressedAttributes))#writing byte size and bytes
            else: #kero blaster no compression/rockfish
                for attributes in self.attributeArrayEdit:
                    file.write(bytes(attributes))          
        file.close()
        
    def pxArray(self, attributes, split): #converts list to array or array to list
        if split:

            pass
        else:
            if self.compression == 2: #compression 2 = vertical. Shuffles around entries so it's layed out correctly.
                return [attributes[i::self.height] for i in range(self.height)] 
            else: #horizontal or no compression:
                return [attributes[i:i+self.width] for i in range(0, self.size, self.width)] 
    
    def pxCompress(self, game, compression):     
        def processAttr(RLE, attributes, intAttribute, repeat, b):
            if intAttribute != attributes or (repeat == 256 and game == 0 or repeat == 65536):
                if game == 1:
                    RLE += (attributes % 16).to_bytes(1)+(attributes// 16).to_bytes(1) #if keroM add xy id
                else: 
                    RLE += attributes.to_bytes(1) #add indexed id
                if repeat > 65535 and game == 1: #uInt16
                    return RLE+b'\xff\xff', intAttribute, 0 
                elif repeat > 255 and game == 0:  #uInt8
                    return RLE+b'\xff', intAttribute, 0 
                return RLE+repeat.to_bytes(b, 'little'), intAttribute, 0 #edited RLE, move attribute to next tile, repeat = 0.
            return RLE, attributes, repeat #return unedited 
        bValue = 2 if game == 1 else 1 #read 2 bytes if kerom
        attribute = self.attributeArray[0][0] #start value

        RLE = b''
        repeat = 0
        if compression == 1: #horizontal
            for row in self.attributeArray:
                for intAttribute in row:
                    RLE, attribute, repeat = processAttr(RLE, attribute, intAttribute, repeat, bValue)
                    repeat += 1
        else: #vertical
            for x in range(self.width):
                for y in range(self.height):
                    RLE, attribute, repeat = processAttr(RLE, attribute, self.attributeArray[y][x], repeat, bValue)
                    repeat += 1
        #last tile:
        if game == 1:
           RLE += (attribute%16).to_bytes(1)+(attribute//16).to_bytes(1)+repeat.to_bytes(2, 'little')
        else:
           RLE += attribute.to_bytes(1)+repeat.to_bytes(1)
        return RLE

def findAttributeText(attribute):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


    if pxattr.version == 0:
        path = paths.attributeInfoKB
    elif pxattr.version == 1:
        path = paths.attributeInfoPT
    else:
        path = paths.attributeInfo2012
    
    with open(path, 'r+') as file:
        if attribute >= 100:
            iAmount = 3
        elif attribute >= 10:
            iAmount = 2
        else:
            iAmount = 1

        while True:
            line = file.readline()
            if line[0] == '$':
                def fetchNumber(line, index):
                    strg = ''
                    for char in line[index:]:
                        if char == '-' or char == ' ':
                            break
                        strg += char
                    return strg
                lowRange = fetchNumber(line, 1)
                highRange = fetchNumber(line, len(lowRange)+2)
                
                if attribute in range(int(lowRange), int(highRange)+1):
                    return line[len(lowRange) + len(highRange) + 3:]
            elif line[0:iAmount] == str(attribute):
                return line[iAmount+1:-1]

pxattr = pxattrProcess()
