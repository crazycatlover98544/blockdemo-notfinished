#!/usr/bin/env python3
'''
Copyright (c) 2026 @crazycatlover98544

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

You may also read these terms at the following website: https://opensource.org/license/mit

My GitHub account is located at https://github.com/crazycatlover98544
My MistWarp account is located at https://mistwarp.org/users/crazycatlover98544

Please note that this code is not written by an expert.
I am not responsible if this harms your computer.

THIS PROGRAM WILL LAG.

11/7/2026@6:20 P.M. EST
World height changed from 16 blocks to 20
Added a space for people to build at without mining
You can change the block you are holding with "1" or "2" (1: Dirt; 2: Grass)
'''

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import numpy

try:
    from tkinter import messagebox
    messagebox.showwarning('Notice','This is in early development. Expect lagging and bugs.\nPress "OK" to start the game.')
except (ModuleNotFoundError, ImportError): # Some people do not have tkinter; ImportError is added just in case.
    pass # Just let them play

app = Ursina(
    title='Test',
    show_ursina_splash=False,
    fullscreen=True,
    editor_ui_enabled=False
)

currently_held_block = 1

coords = Text(text='', position=((-camera.aspect_ratio / 2) + 0.05, 0.47), scale=0.75)
current_hold = Text(text=str(currently_held_block), position=((-camera.aspect_ratio / 2) + 0.05, -0.47), scale=0.75)
sky = Sky(model='sky_dome')
player_respawn = Vec3(7,15,7)

player = FirstPersonController()
# Settings for the player
player.mouse_sensitivity = Vec2(60,60)
player.position = player_respawn
player.gravity = 1.0
player.jump_height = 2.0
player.jump_up_duration = 0.6
player.fall_after = 0.25
player.air_time = 0.3
player.speed = 6

world = numpy.ones((16, 16, 20), dtype=int)
# np z is y; np y is z

i = 0
while i < 16: # Clear a space for building
    j = 0
    while j < 16:
        k = 15
        while k < 20:
            world[i,j,k] = 0
            k += 1
        j += 1
    i += 1

world[7,7,14] = 3
world[7,8,14] = 2
world[7,8,15] = 2

cubes = []

keys_down = {
    'w': False,
    'a': False,
    's': False,
    'd': False,
    'space': False,
    'left shift': False
}

textures = {
    'dirt': 'textures/dirt.png',
    'grass': 'textures/grass.png'
}

blocks_list = { # used for rendering the currently selected block; it makes no sense to just see "1" and "2"
    '1': 'bd-nf:dirt',
    '2': 'bd-nf:grass'
}

def reload_world():
    global cubes
    for item in cubes:
        destroy(item)
    cubes = []
    for (x, z, y), value in numpy.ndenumerate(world):
        if value == 1:
            c = color.white
            t = textures.get('dirt','')
        elif value == 2:
            c = color.white
            t = textures.get('grass','')
        elif value == 3:
            c = color.green
            t = ''
        else:
            continue
        if (not (x == 0 or x == 15 or z == 0 or z == 15 or y == 0 or y == 15)) and ((not world[x+1,z,y] == 0) and (not world[x-1,z,y] == 0) and (not world[x,z+1,y] == 0) and (not world[x,z-1,y] == 0) and (not world[x,z,y+1] == 0) and (not world[x,z,y-1] == 0)):
            continue
        cubes.append(Entity(model='cube', position=Vec3(x,y,z), color=c, scale=1, collider='box', enabled=value, texture=t, texture_scale=(1,1)))

def formatted_coords(coords_as_list):
    playerpos_tmp = coords_as_list
    fc_tmp = 0
    while fc_tmp < len(playerpos_tmp):
        playerpos_tmp[fc_tmp] = float(f'{playerpos_tmp[fc_tmp]:.1f}')
        fc_tmp += 1
    return str(tuple(playerpos_tmp))

def update():
    if player.y < -5:
        player.position = player_respawn
    coords.position = Vec2((-camera.aspect_ratio / 2)+0.05, 0.47)
    current_hold.text = f'Currently holding {blocks_list.get(str(currently_held_block),"notfound")}'
    try:
        coords.text = f'Pos: {formatted_coords(list(player.position))}  Pointed: {formatted_coords(list(mouse.hovered_entity.position + mouse.normal))}'
    except AttributeError:
        pass # for some reason, mouse is not initialized properly before rendering starts; this prevents the error

def key_pressed(key,target):
    global keys_down
    if target == key:
        keys_down[target] = True
    elif f'{target} up' == key:
        print('hi')
        keys_down[target] = False
    elif f'{target} hold' in key:
        keys_down[target] = True

def input(key):
    global world, currently_held_block
    print(key)
    if key == 'escape':
        mouse.locked = not mouse.locked
    if key == 'r':
        player.position = player_respawn
    if key == '1':
        currently_held_block = 1
    elif key == '2': # use elif here as it will make sure the code does not glitch out and rapidly change between blocks if both "1" and "2" are pressed at the same time
        currently_held_block = 2
    if key == 'left mouse down':
        if mouse.hovered_entity:
            if hasattr(mouse.hovered_entity, 'position'):
                hepos = tuple(mouse.hovered_entity.position)
                tx = hepos[0]
                ty = hepos[1]
                tz = hepos[2]
                world[int(tx),int(tz),int(ty)] = 0
                print(world[int(tx),int(tz),int(ty)])
                reload_world()
    if key == 'right mouse down':
        if mouse.hovered_entity:
            if hasattr(mouse.hovered_entity, 'position'):
                hepos = tuple(mouse.hovered_entity.position + mouse.normal)
                tx = hepos[0]
                ty = hepos[1]
                tz = hepos[2]
                    
                try:
                    world[int(tx),int(tz),int(ty)] = currently_held_block
                    reload_world()
                except IndexError:
                    pass
    for item in ['w','a','s','d','space','left shift']:
        key_pressed(key,item)

reload_world()

while True:
    app.step()
