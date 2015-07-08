Presentation
=============

A simple audio player based on Qt, GStreamer and Python. Functionalities include customizable tree view, playlist view, global shortcuts, remote control, and web radio.


<!---
![Alt text](/relative/path/to/img.jpg?raw=true "Optional Title")
-->



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

Shortcuts concist of a combination of a *modifier+key* to trigger an action. They can all be set in the config file. Modifier takes value among: `Ctrl, Shift, Alt, Meta (windows key)`, and can be combined using `+` e.g. `Ctrl+Shift`.

Keys are named: `A, B, ..., F1, F2, ..., Left, Right, Tab, Del, Ins, PgUp, Plus, Minus, ...,` and can be combined using `+`, e.g. `A+B, Ctrl+A, ... `

Thus for a config file like:
```
...
modifier = Ctrl
play_pause = Shift+Space
stop = A
...
```
Pressing `Ctrl+Shift+Space` would *pause* the playback, `Ctrl+A` would *stop* the playback.

Functionalities:
- play/pause
- stop
- next
- previous
- quit
- volume up
- volume down


Tree order and Playlist columns functions
=============

- Tags: `%tag%` e.g. `%albumartist%, %date%, %album%, %artist%, ...`
- Optional parts: `$...$` e.g. `$Disc %discnumber%$` will display *Disc 1*
		for files having a discnumber tag, and nothing for the others
- Separator: `|` used as sub-level for the tree, new column for the playlist
	
Tags : `%length%, %samplerate%, %channels%, %bitrate%`, plus any tag in your file

Special tags : 
- `%file%` : path of the file
- `%albumartist%` : if the tag exist in the file it contains the value otherwise contains the artist tag. Useful for compilation type CDs.
- `%trackartist%` : contains the artist tag for albums having an albumartist tag


A tree order like : `%albumartist% (%genre%)| [%date%] - %album% | $Disc %discnumber% | $ %tracknumber%. %title%`

Would give a tree like :

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

Foo.cd can be controlled by writing to a pipe named pipe_test, 
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
- quit
