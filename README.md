![Screenshot of the Program.](https://github.com/folderplug/pxAttribute/blob/main/programimg.png?raw=true)
![Pixel Art of Kaeru from Kero Blaster.](https://github.com/folderplug/pxAttribute/blob/main/kbimg.png?raw=true)

# pxAttribute
pxAttribute is an editor designed to edit the data of .pxattr file types. pxattr files are collision data that associate a tile from a tilesheet to an specific attribute. They have been used for Pixel's newer games (ranging from around 2012 to present day.) This editor is designed to both edit, and create pxattr files.

## Using pxAttribute:
pxAttribute has basic editing tools featuring: Opening pxattr files, creating pxattr files, editing pxattr files, undoing an action, and redoing one (ctrl z, ctrl shift z). Besides the obvious, it also lets you display any tile resolution. Tile resolution is actually set in the level format (pxpack), so it's a purely visual change. The reason tile resolution is important is because it sets the amount of pixels per tile, without the right resolution, tiles will be messed up. Games like Rockfish and Pitest use this (and Kero Blaster as well, but it is unused), so you should make sure the level has the right resolution before you start whatever that it is that you're doing.

## Pxattr Info:
Pxattr has several aspects to them besides just hosting the attributes.
* Header: This is a feature only existing for post 2012 versions of the format. It defines what game the file is for. You can set it (automatically) by setting the "Version" value to one of the values listed when saving or  editing the file data.
* Width/Height: uint16 width and height values, for the dimensions of the format. (Having uneven dimensions could cause issues when changing the tile resolution, creating artifacts like half-tiles.)
* Compression: an RLE compression format for storing the attribute data, existing for post 2012 versions of the format. 0 is for no compression, 1 is for horizontal compression, and 2 is for vertical compression.
* Attribute Data: Attributes, and how they work change from game to game, the code for them is handled by the game code, so when editing specific versions, some tiles do not have graphics for themselves, however you can still view the attribute value by hovering over it while editing.

Anyone has permission to modify this software's code (with credit.)

![Pitest Pixel Art.](https://github.com/folderplug/pxAttribute/blob/main/pitestimg.png?raw=true)
![Rockfish Pixel .](https://github.com/folderplug/pxAttribute/blob/main/rfimg.png?raw=true)
