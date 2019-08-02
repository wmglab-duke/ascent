"""
Proof-of-concept for a physics-based fascicle repositioning method, adapted from flipper.py in the Pymunk examples.
"""

import random

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

width = 600
height = 600

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

### Physics stuff
space = pymunk.Space()
space.gravity = (0.0, 0.0)
draw_options = pymunk.pygame_util.DrawOptions(screen)

## Balls
balls = []

### walls
def line_points(w: float = width, h: float = height, center: bool = False):
    x, y = 0, 0
    if center:
        x = (600 - width)/2
        y = (600 - height)/2

    return [((0 + x, h/2 + y), (w/2 + x, 0 + y)),
            ((w/2 + x, 0 + y), (w + x, h/2 + y)),
            ((w + x, h/2 + y), (w/2 + x, h + y)),
            ((w/2 + x, h + y), (0 + x, h/2 + y))]


static_lines = [pymunk.Segment(space.static_body, a, b, 2.0) for a, b in line_points()]


for line in static_lines:
    line.elasticity = 0.7
    line.group = 1
space.add(static_lines)


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False

        elif event.type == KEYDOWN and event.key == K_SPACE:
            width -= 15
            height -= 15

            for line in static_lines:
                space.remove(line)

            static_lines = [pymunk.Segment(space.static_body, a, b, 2.0) for a, b in line_points(width,
                                                                                                 height,
                                                                                                 center=True)]
            for line in static_lines:
                line.elasticity = 0.7
                line.group = 1
            space.add(static_lines)

        elif event.type == KEYDOWN and event.key == K_b:

            mass = 1
            radius = 25
            # inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
            # body = pymunk.Body(mass, inertia)
            # x = random.randint(115,350)
            # body.position = x, 400
            # shape = pymunk.Circle(body, radius, (0,0))

            vertices = [(0, 60), (60, 60), (60, 0), (0, 0)]
            x = random.randint(115, 350)
            position = x, 400
            inertia = pymunk.moment_for_poly(mass, vertices)
            body = pymunk.Body(mass, inertia)
            body.position = position
            shape = pymunk.Poly(body, vertices)
            shape.friction = 0.6
            shape.density = 0.01

            shape.elasticity = 0.0
            space.add(body, shape)
            balls.append(shape)

    ### Clear screen
    screen.fill(THECOLORS["white"])

    ### Draw stuff
    space.debug_draw(draw_options)

    ### Update physics
    dt = 1.0 / 60.0 / 5.
    for x in range(2):
        space.step(dt)

    ### Flip screen
    pygame.display.flip()
    clock.tick(50)
    pygame.display.set_caption("fps: " + str(clock.get_fps()))

