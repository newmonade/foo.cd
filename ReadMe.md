Presentation
=============

A simple music player based on Python, Qt, GStreamer and TagLib. Functionalities include 
- customizable library tree view
- customizale playlist view
- gapeless playback
- library search
- global shortcuts
- remote control
- web radio
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
=============

Tree	
- Enter: append songs to playlist and play
- Shift+Enter : append songs to playlist

Playlist
- Enter: play
- Del: delete song from playlist 


Shortcuts
=============

Shortcuts concist of a combination of *modifier+key* to trigger an action. They can all be customized in the config file. Modifier takes value among: `Ctrl, Shift, Alt, Meta (windows key)`, and can be combined using `+` e.g. `Ctrl+Shift`.

Keys are named: `A, B, ..., F1, F2, ..., Left, Right, Tab, Del, Ins, PgUp, Plus, Minus, ...,`. They can be combined using `+`, e.g. `A+B, Ctrl+A, ... `

Thus for a config file as:
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

The hierarchy of the tree and the columns displayed can be customized from the config file, following a basic syntax.
- Tags: `%tag%` e.g. `%albumartist%, %date%, %album%, %artist%, ...`
- Optional parts: `$...$` e.g. `$Disc %discnumber%$` will display *Disc 1*
		for files having a discnumber tag, and nothing for the others
- Separator: `|` used as sub-level for the tree, new column for the playlist
	
Tags : `%length%, %samplerate%, %channels%, %bitrate%`, plus any tag in your file

Special tags : 
- `%file%` : path of the file
- `%albumartist%` : if the tag exist in the file it contains the value otherwise contains the artist tag. Useful for compilation type CDs.
- `%trackartist%` : contains the artist tag for albums having an albumartist tag


A tree order as : `%albumartist% (%genre%)| [%date%] - %album% | $Disc %discnumber% | $ %tracknumber%. %title%`

Will give the following tree :

```
		Buena Vista Social Club (cubano)
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

Foo.cd can be controlled by writing to the pipe, 
allowing global shortcuts (e.g. using xmonad), ssh control, etc. The `remote.sh` script provide an example of that behaviour

Key words:
- play_pause
- stop
- volume_up
- volume_down
- song_next
- song_prev
- tree_up
- tree_down
- tree_left
- tree_right
- tree_validate
- tree_append
- radio_mode
- quit
