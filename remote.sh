#!/bin/bash

i="0"

# Absolute path this script is in
SCRIPTPATH=$(dirname $(readlink -f "$0"))
PIPE="pipe_test"

echo -e \\033c
	
	echo -e '\e[91m	  -=+/  Foo.cd pipe commands  \+=- \e[39m'
	echo ""
	echo -e "\e[37m	Play/Pause       Stop         Quit \e[21m"
	echo -e "\e[1m	    1             2            9 \e[21m"
	echo ""
	echo -e "\e[37m	 Navigate       Volume      Previous/"
	echo -e "	 in Tree        Up/Down     Next Song \e[39m"
	echo -e '\e[1m	    Z                          ↑'
	echo -e '	  Q S D          ←  →          ↓ \e[21m'
	echo ""
	echo ""
	echo -e "\e[37m	 Validate       Append  \e[21m"
	echo -e "\e[1m	  Enter          TBD \e[21m"
	echo ""
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
		9) echo "quit" > $SCRIPTPATH/$PIPE; i=1 ;;
		*) printf "ERROR: Invalid selection"; printf $ui;;
	esac
	
done
