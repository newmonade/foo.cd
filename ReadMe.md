Presentation
=============

A simple music player based on Python, Qt, GStreamer and TagLib. Functionalities include 
- Customizable library tree view
- Customizale playlist view
- Gapeless playback
- Library search
- Global shortcuts
- Remote control
- Web radio
- 10 band equalizer
- Tagging facilities

All kinds of audio files are supported, provided that you installed the related gst-plugin (might already be installed on your computer). The GUI is freely - and mostly - inspired by foobar2000 default interface.


<!---
![Alt text](/relative/path/to/img.jpg?raw=true "Optional Title")
-->

Installation
=============
Install the dependencies: pyTagLib, pyQt4, gst-python 1.0. Copy the repository in a folder. Create a named-pipe called pipe in that folder by running `mkfifo pipe`. Run with Python3 ! (and hope everything is OK)


Default behaviour
=================
Press the *Alt* key to show or hide the main window menu.

Library
- *Enter*: append songs to playlist and play
- *Shift+Enter*: append songs to playlist
- *Right click*: context menu for tagging and ReplayGain

Playlist
- *Enter*: play
- *Del*: delete song from playlist 


Shortcuts
=========

Shortcuts concist of a combination of *modifier+key* to trigger an action. They can all be customized in the config file. Modifier takes value among: `Ctrl, Shift, Alt, Meta` (windows key).

Keys are named: `A, B, F1, F2, Left, Right, Tab, Del, Ins, PgUp, Plus, Minus, ...`. Modifiers and keys can be combined using `+`, e.g. `A+B, Ctrl+Shift, ... `

Thus for a configuration file as:
```
...
modifier = Ctrl
play_pause = Shift+Space
stop = A
...
```
Pressing `Ctrl+Shift+Space` will *pause* the playback, `Ctrl+A` will *stop* the playback.

Shortcut actions:
- play/pause
- stop
- next
- previous
- quit
- volume up
- volume down
- toggle radio mode
- open equalizer


Tree order and Playlist columns functions
=============

The hierarchy of the tree library and the playlist columns can be customized in the configuration file, following a basic syntax.

`tree_order = %albumartist% (%genre%)| [%date%] - %album% | $Disc %discnumber% | $ %tracknumber%. %title%`

where:

- Tags are surrounded by *%*, they include any field present in your files plus the defaults: `%length%, %samplerate%, %channels%, %bitrate%`
- Optional parts can be specified using `$...$`. This will display the formated tags for the tracks having the requested fields and nothing for the others. 
	For example `$Disc %discnumber%$` will display *Disc 1* for files having a %discnumber% tag, and nothing for the others
- The pipe `|` separator is used as sub-level for the tree and new column for the playlist


Special tags : 
- `%file%` : path of the file
- `%albumartist%` : if the tag exist in the file it contains the value otherwise it si mapped to the artist tag. Useful for compilation type CDs.
- `%trackartist%` : contains the artist tag only for albums having an albumartist tag different from artist tag


The tree order shown above will give the following tree :

```
		Buena Vista Social Club (Cubano)
			|-- [1996] - Buena Vista Social Club
					|-- 1. Chan Chan
					|-- 2. De Camino A La Vereda
					|-- ...
		George Duke (Jazz)
			|-- [1974] - Feel
			|-- [1975] - The Aura Will Prevail
			|-- [2006] - The Essential
					|-- Disc 1
						|-- 1. Scuse me miss
						|-- 2. Reach for it
						|-- ...
					|-- Disc 2
			|-- [2008] - Dukey Treats
		...	
```		
	
Remote interface
=============

Foo.cd can be controlled by writing keywords to the pipe, allowing global shortcuts (e.g. using xmonad), ssh control, etc. The `remote.sh` for the list of available keywords and actions.
