#import pygst
#pygst.require("1.0")
#import Gst


from gi.repository import GObject
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')
GObject.threads_init()
Gst.init(None)





def on_tag(bus, msg):
    
    print( msg)
    print(msg.src)
    ''' taglist = msg.parse_tag()
        for key in taglist.keys():
        print('\t%s = %s' % (key, taglist[key]))
    '''

def main():

	#our stream to play
	music_stream_uri = 'http://173.245.94.220:80'
	#music_stream_uri = 'http://tsfjazz.ice.infomaniak.ch:80/tsfjazz-high'
	
	'''
	#creates a playbin (plays media form an uri) 
	player = Gst.ElementFactory.make("playbin", "player")
	
	#set the uri
	player.set_property('uri', music_stream_uri)
	
	#start playing
	player.set_state(Gst.State.PLAYING)
	'''
	
	
	
	pipeline = Gst.Pipeline()
	playbin = Gst.ElementFactory.make('playbin', None)
	playbin.set_property('uri', music_stream_uri)
	pipeline.add(playbin)
	
	#start playing
	pipeline.set_state(Gst.State.PLAYING)
	
	bus = pipeline.get_bus()
	bus.add_signal_watch()
	bus.enable_sync_message_emission()



	bus.connect('message::tag', on_tag)
	#bus.connect('message::new_tag', on_tag)
	
	bus.connect('message', on_tag)
	
	#bus.set_sync_handler(on_tag)
	
	
	#wait and let the music play
	input('Press enter to stop playing...')
	

if __name__ == '__main__':
	main()