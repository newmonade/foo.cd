#!/bin/bash


i="0"


# Absolute path this script is in
SCRIPTPATH=$(dirname $(readlink -f "$0"))
PIPE="pipe_test"

echo -e \\033c
	
	echo '	            -=+/  Foo.cd pipe commands  \+=-'
	echo ""
	echo '	1.play/pause    2.stop'
	echo ""
	echo ""
	echo "	Navigate                Volume            Next/Previous"
	echo "	in Tree                 Up/Down               Song "
	echo '	    Z                                           ↑'
	echo '	  Q S D                  ←  →                   ↓'
	echo ""
	echo ""
	echo "	Validate               Append"
	echo "	Enter                  TBD  "
	echo ""
	echo ""
	echo '	7. quit'
	echo ""
	
while [ $i -lt 1 ]
do	
	read -rsn1 ui
	case "$ui" in
		$'\x1b')    # Handle ESC sequence.
		# Flush read. We account for sequences for Fx keys as
		# well. 6 should suffice far more then enough.
		read -rsn1 -t 0.01 tmp
		if [[ "$tmp" == "[" ]]; then
			read -rsn1 -t 0.01 tmp
			case "$tmp" in
				"A") printf "Up\n";;
				"B") printf "Down\n";;
				"C") echo "volume_up" > $SCRIPTPATH/$PIPE;;
				"D") echo "volume_down" > $SCRIPTPATH/$PIPE;;
			esac
		fi
		# Flush "stdin" with 0.1  sec timeout.
		read -rsn5 -t 0.01;;
		
		# Other one byte (char) cases. Here only quit.
		"") echo "tree_validate" > $SCRIPTPATH/$PIPE;;
		z) echo "tree_up" > $SCRIPTPATH/$PIPE;;
		s) echo "tree_down" > $SCRIPTPATH/$PIPE;;
		q) echo "tree_left" > $SCRIPTPATH/$PIPE;;
		d) echo "tree_right" > $SCRIPTPATH/$PIPE;;
		1) echo "play_pause" > $SCRIPTPATH/$PIPE;;
		2) echo "stop" > $SCRIPTPATH/$PIPE;;
		7) echo "quit" > $SCRIPTPATH/$PIPE; i=1 ;;
		*) printf "ERROR: Invalid selection"; printf $ui;;
	esac
	
done
