import pygst
import gst
import pygtk
import gtk
from daemon import become_daemon

pipeline = gst.Pipeline('mypipeline')

alsasrc = gst.element_factory_make('alsasrc')
alsasrc.set_property('device', 'hw:0,4')
pipeline.add(alsasrc)

#wavepack = gst.element_factory_make('wavpackenc')
#pipeline.add(wavepack)
#
#wavefile = gst.element_factory_make('filesink')
#wavefile.set_property('location', '/tmp/gst.wav')
#pipeline.add(wavefile)

stereo = gst.element_factory_make('audiopanorama')
stereo.set_property('panorama', 0.5)
pipeline.add(stereo)

encoder = gst.element_factory_make('ffenc_libfaac')
pipeline.add(encoder)

#video = gst.element_factory_make('videotestsrc')
#video.set_property('pattern', 'snow')
#pipeline.add(video)

#mpeg = gst.element_factory_make('ffenc_libx264')
#pipeline.add(mpeg)

muxer = gst.element_factory_make('ffmux_mpegts')
pipeline.add(muxer)

sink = gst.element_factory_make('tcpclientsink')
sink.set_property('host', 'c0001.neohippie.net')
sink.set_property('port', 9201)
pipeline.add(sink)

#alsasrc.link(wavepack)
#wavepack.link(wavefile)

alsasrc.link(stereo)
stereo.link(encoder)
encoder.link(muxer)
#video.link(mpeg)
#mpeg.link(muxer)
muxer.link(sink)

pipeline.set_state(gst.STATE_PLAYING)

#become_daemon()
gtk.main()
