
# Vizard SteamVR debugging tool

## Description

This is a simple Vizard script to help test and debug SteamVR-based scenarios (basically a collection of debugging hacks I use frequently, all using Vizard built-in functionality).

### Features (so far): 
- Enumerate and display all detected SteamVR components (base stations, controllers, trackers), together with their device index, local coordinate axes, and position / orientation data
- Store controller position and orientation data for simple measurements, with CSV export
- Save screenshots of the environment with a controller button press

![screenshot](https://user-images.githubusercontent.com/7711674/114215627-1ac89900-9966-11eb-9dee-2cb319d58fca.png)

## Installation and Usage

With SteamVR installed and active, simply run the included Python script in the Vizard IDE. All included button and keyboard functionality will be displayed in the Vizard window. 
The Main() task function can be freely extended to show scene elements or trigger functionality to debug.

