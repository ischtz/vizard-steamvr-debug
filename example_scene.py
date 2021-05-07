# Vizard SteamVR debugging helper
# Immo Schuetz, 2021
# immo.schuetz@psychol.uni-giessen.de

import viz
import vizfx

import steamvr

from vizard_steamvr_debug import SteamVRDebugOverlay

viz.setMultiSample(8)
viz.go()

# Standard SteamVR initialization
hmd = steamvr.HMD()
if not hmd.getSensor():
	sys.exit('Vive not detected')
hmd.setMonoMirror(True)
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())

# Set up a simple scene using Vizard default assets
vizfx.addChild('ground_wood.osgb')
vizfx.addChild('plant.osgb', pos=[0, 0, 2])

# Add the debug overlay
# Press F12 to show
debugger = SteamVRDebugOverlay()
