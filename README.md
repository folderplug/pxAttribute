.Pxattr are collision data files used for tilesets; it associates a tile from a tileset to a collision type. The data values vary from version, so I included info for what tiles exist in other versions.

Select an attribute from the right side, and then draw with it. Undo and Redo with Ctrl-Z and Ctrl-Shift-Z if needed. Save File with Ctrl-S or from the Filebar.
Edit file data from Filebar.

Pxattr Info:
Compression has existed since post 2012 (Kero Blaster), but it has been unused. It is used in Pitest, for both the level files and the pxattr files.
The compression is RLE compression (storing a tile, and then the amount of times that tile gets repeated.)

Version:
Games like Kero Blaster and Pitest do not have the same header, by changing this it determines if the game engine will be able to read the pxattr file. If you use the wrong version in the wrong game, it will not work. Make sure to set the version to the correct Value.
...Interestingly, Pre-2012 (Rockfish and early versions of Starfrog) don't have headers, this is compromised by the program reading the width and height (which are at the start of the file), and then seeing if the total size matches the file length.

Tile Resolution:
This is a visual aspect that actually comes from pxmap files (the level format). This affects how they're rendered, pxattr files don't store this data, only pxmap files, however this is important because it sets how many pixels are per tile, if you use the wrong setting it can mess up the rendering of it in game.

Anyone can modify this code if they please (with credit.)
