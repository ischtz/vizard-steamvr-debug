# Vizard SteamVR debugging helper
# Immo Schuetz, 2021
# immo.schuetz@psychol.uni-giessen.de

import sys 
import csv 

import viz
import vizfx
import vizmat
import vizact
import vizinfo
import viztask
import vizshape

import steamvr

viz.setMultiSample(8)
viz.go(viz.FULLSCREEN)


# SCENE OBJECTS
# -----------------------------------------------------------------------------

# Global coordinate visualization
grid = vizshape.addGrid((100, 100), color=[0.4, 0.4, 0.4])
main_axes = vizshape.addAxes(pos=(0,0,0), scale=(0.5, 0.5, 0.5))
ground_plane = vizshape.addPlane((100,100), color=[0.3, 0.3, 0.3], alpha=0.5)

# Lighting
headlight = viz.MainView.getHeadLight()
headlight.disable()
main_light = vizfx.addDirectionalLight(euler=(0,90,0), color=viz.WHITE)
origin_light = vizfx.addPointLight(color=viz.WHITE, pos=(0,0,0))

# UI
txt = 'Hotkeys:\nS - Save collected points data\nC - Clear point data\nQ - Quit\n\n'
txt += 'Controller Buttons:\nTrigger - place point axes\nA - Save point data\nB - Take screenshot'
ui = vizinfo.InfoPanel(txt, icon=True, align=viz.ALIGN_RIGHT_TOP, title='SteamVR Debug Tool')
ui.renderToEye(viz.RIGHT_EYE)
ui.addSeparator()

points = []
screenshot = 1


# TASKS
# -----------------------------------------------------------------------------

def showVRText(msg, color=[1.0, 1.0, 1.0], distance=2.0, scale=0.05, duration=2.0):
    """ Display head-locked message in VR, e.g. for instructions.
    
    Args:
        msg (str): Message text
        color: RBG 3-tuple of color values
        distance (float): Z rendering distance from MainView
        scale (float): Text node scaling factor
        duration (float): Message display duration (seconds)
    """
    # Create 3D text object
    text = viz.addText3D(msg, scale=[scale, scale, scale], color=color)
    text.resolution(1.0)
    text.setThickness(0.1)
    text.alignment(viz.ALIGN_CENTER)
    
    # Lock text to user viewpoint at fixed distance
    text_link = viz.link(viz.MainView, text, enabled=True)
    text_link.preTrans([0.0, 0.0, distance])
    
    # Fade text away after <duration> seconds
    fadeout = vizact.fadeTo(0, time=0.7)
    yield viztask.waitTime(duration)
    text.addAction(fadeout)
    yield viztask.waitActionEnd(text, fadeout)
    text.remove()


def storeControllerData(controller, index):
	""" Print position and orientation of a controller, 
	and create an axis object to visualize it
	"""
	s = 'Controller {:d}: pos=[{:1.3f}, {:1.3f}, {:1.3f}], ori=[{:3.3f}, {:3.3f}, {:3.3f}]'
	p = controller.getPosition()
	e = controller.getEuler()
	print(s.format(index, p[0], p[1], p[2], e[0], e[1], e[2]))
	
	px = vizshape.addAxes(scale=(0.05, 0.05, 0.05))
	px.setPosition(p)
	px.setEuler(e)
	points.append(px)


def savePoints(filename='viz_svr_debug.csv'):
	""" Save list of stored points """
	global points
	fields = ['point', 'posX', 'posY', 'posZ', 'eulerX', 'eulerY', 'eulerZ']
	with open(filename, 'w') as pfile:
		writer = csv.DictWriter(pfile, delimiter='\t', lineterminator='\n', 
							    fieldnames=fields, extrasaction='ignore')
		writer.writeheader()
		for pidx, point in enumerate(points):
			p = point.getPosition()
			e = point.getEuler()
			writer.writerow({'point': pidx, 'posX': p[0], 'posY': p[1], 'posZ': p[2], 
							 'eulerX': e[0], 'eulerY': e[1], 'eulerZ': e[2]})

	viztask.schedule(showVRText('Points data saved.'))
	print('Points data saved.')


def clearPoints():
	""" Remove previously placed point axes objects
	and clear the point data list """
	global points
	for object in points:
		object.remove()
	points = []
	viztask.schedule(showVRText('Points data cleared.'))
	print('Point data and axes cleared.')


def saveScreenshot():
	""" Save a BMP screenshot of the current Vizard window """
	global screenshot
	fn = 'svr_screenshot_{:d}.bmp'.format(screenshot)
	viz.window.screenCapture(fn)
	screenshot += 1
	viztask.schedule(showVRText('Screenshot saved.'))
	print('Screenshot saved.')


# Key callbacks
vizact.onkeydown('s', savePoints)
vizact.onkeydown('c', clearPoints)
vizact.onkeydown('q', viz.quit)


# HARDWARE SETUP
# -----------------------------------------------------------------------------

# Headset
hmd = steamvr.HMD()
if not hmd.getSensor():
	sys.exit('Vive not detected')
hmd.setMonoMirror(True)
navigationNode = viz.addGroup()
viewLink = viz.link(navigationNode, viz.MainView)
viewLink.preMultLinkable(hmd.getSensor())

# Lighthouses
lighthouses = {}
for lidx, lighthouse in enumerate(steamvr.getCameraList()):
	lighthouse.model = lighthouse.addModel(parent=navigationNode)
	if not lighthouse.model:
		lighthouse.model = viz.addGroup(parent=navigationNode)
		
	lighthouse.model.disable(viz.INTERSECTION)
	viz.link(lighthouse, lighthouse.model)
	
	l_text = viz.addText3D(str(lidx), scale=(0.05, 0.05, 0.05), color=viz.YELLOW,
						   parent=lighthouse.model, pos=(0.1, 0, 0))
	l_text.setEuler(180, 0, 0)
	
	lighthouses[lidx] = {'model': lighthouse.model,
						 'text': l_text}
	print('Found Lighthouse: {:d}'.format(lidx))


# Controllers
controllers = {}
if steamvr.getControllerList():
	ui.addItem(viz.addText('Controllers'))

for cidx, controller in enumerate(steamvr.getControllerList()):
	
	controller.model = controller.addModel(parent=navigationNode)
	if not controller.model:
		controller.model = viz.addGroup(parent=navigationNode)
	controller.model.disable(viz.INTERSECTION)
	viz.link(controller, controller.model)
	
	c_axes = vizshape.addAxes(scale=(0.1, 0.1, 0.1))
	viz.link(controller, c_axes)
	c_text = viz.addText3D(str(cidx), scale=(0.05, 0.05, 0.05), 
						   parent=controller.model, pos=(-0.05, 0, 0))
	
	controllers[cidx] = {'model': controller.model,
						 'axes': c_axes,
						 'text': c_text,
						 'ui': viz.addText('N/A')}
	
	ui.addLabelItem(str(cidx), controllers[cidx]['ui'])
	vizact.onsensordown(controller, steamvr.BUTTON_TRIGGER, storeControllerData, controller, cidx)
	vizact.onsensordown(controller, 1, savePoints)
	vizact.onsensordown(controller, 0, saveScreenshot)

	print('Found Controller: {:d}'.format(cidx))
	

# Trackers
trackers = {}
if steamvr.getTrackerList():
	ui.addSeparator()
	ui.addItem(viz.addText('Vive Trackers'))

for tidx, tracker in enumerate(steamvr.getTrackerList()):
	
	tracker.model = tracker.addModel(parent=navigationNode)
	if not tracker.model:
		tracker.model = viz.addGroup(parent=navigationNode)
	tracker.model.disable(viz.INTERSECTION)
	viz.link(tracker, tracker.model)

	t_axes = vizshape.addAxes(scale=(0.1, 0.1, 0.1))
	viz.link(tracker, t_axes)

	t_text = viz.addText3D(str(tidx), scale=(0.05, 0.05, 0.05), color=viz.BLUE,
						   parent=tracker.model, pos=(-0.1, 0, 0))

	trackers[tidx] = {'model': tracker.model,
					  'axes': t_axes,
					  'text': t_text,
					  'ui': viz.addText('N/A')}
	ui.addLabelItem(str(tidx), trackers[tidx]['ui'])
	
	print('Found Vive tracker: {:d}'.format(tidx))


def updateUI():
	""" Update displayed position and orientation data """
	FMT = '({:.2f},{:.2f},{:.2f}) / ({:3.1f},{:3.1f},{:3.1f})'
	for c in controllers.keys():
		pos = controllers[c]['model'].getPosition()
		ori = controllers[c]['model'].getEuler()
		controllers[c]['ui'].message(FMT.format(pos[0], pos[1], pos[2], 
												ori[0], ori[1], ori[2]))
	for t in trackers.keys():
		pos = trackers[t]['model'].getPosition()
		trackers[t]['ui'].message(FMT.format(pos[0], pos[1], pos[2], 
											 ori[0], ori[1], ori[2]))


# MAIN TASK 
# -----------------------------------------------------------------------------

def Main():#
	""" Main task, use this to implement any scenes etc. to test """
	while True:
		yield updateUI()
		yield viztask.waitTime(0.01)

viztask.schedule(Main)
