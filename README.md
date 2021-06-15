
# Vizard SteamVR debugging tool

## Description

This is a simple Vizard script to help test and debug SteamVR-based scenarios (basically a collection of debugging hacks I use frequently, all using Vizard built-in functionality).

### Features (so far): 
- Enumerate and display all detected SteamVR components (base stations, controllers, trackers), together with their device index, local coordinate axes, and position / orientation data
- Store controller position and orientation data for simple measurements, with CSV export
- Save screenshots of the environment with a controller button press
- Save the entire debug scene to OSG format (useful e.g. when measuring rooms)
- Can be added to any Vizard script and toggled using a hotkey (default: F12)

![screenshot](https://user-images.githubusercontent.com/7711674/114215627-1ac89900-9966-11eb-9dee-2cb319d58fca.png)

## Installation and Usage

With SteamVR installed and active, run vizard_steamvr_debug.py in the Vizard IDE to use as a debugging tool directly. All included button and keyboard functionality will be displayed in the Vizard window. Look at example_scene.py for an example on how the debug tool can be added to any script (press F12 to toggle the debug overlay).



