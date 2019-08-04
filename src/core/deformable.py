# builtin
import random
from typing import List

# packages
import numpy as np
import pymunk.pygame_util
import pygame
from pygame.locals import *
from pygame.color import *
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt

# SPARCpy
from src.core import Trace, Slide
from src.utils import Exceptionable, SetupMode, ReshapeNerveMode, ConfigKey


class Deformable(Exceptionable):

    def __init__(self, exception_config: list, boundary_start: Trace, boundary_end: Trace, contents: List[Trace]):

        # init superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        # initialize instance variables
        self.start = boundary_start
        self.end = boundary_end
        self.contents = contents

    def deform(self, morph_count: int = 100, morph_index_step: int = 10, render: bool = True) -> List[tuple]:

        # init space with default gravity (0, 0)
        space = pymunk.Space()

        pygame.init()

        clock = pygame.time.Clock()


        #TODO: implement static line segment version of Trace to pymunk

        morph_steps = [step.pymunk_segments(space) for step in self.deform_steps(self.start, self.end, morph_count)]
        # morph_steps = [step.pymunk_segments(space) for step in (self.start, self.end)]



        # TODO: FIND ACTUAL VALUES
        bounds = self.start.polygon().bounds

        width = int(1.5 * bounds[2])
        height = int(1.5 * bounds[3])

        aspect = float(width) / height

        display_dimensions = int(800 * aspect), 800
        screen = pygame.display.set_mode(display_dimensions)

        drawing_screen = pygame.Surface((width, height))
        options = pymunk.pygame_util.DrawOptions(drawing_screen)
        options.shape_outline_color = (0, 0, 0, 255)
        options.shape_static_color = (0, 0, 0, 255)

        # init vector of start positions
        start_positions: list = []

        # add fascicles bodies to space
        for body, shape in [trace.pymunk_poly() for trace in self.contents]:
            start_positions.append(body.position)
            space.add(body, shape)

        def add_boundary():
            for seg in morph_step:
                seg.elasticity = 2.0
                seg.group = 1
            space.add(morph_step)

        running = True
        loop_count = morph_index_step
        morph_index = 0
        morph_step = morph_steps[morph_index]
        add_boundary()

        while running:
            # if the loop count is divisible by the index step, update morph
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    pass

            if loop_count % morph_index_step == 0:
                space.remove(morph_step)
                morph_index += 1

                if morph_index == len(morph_steps):
                    running = False
                else:
                    morph_step = morph_steps[morph_index]
                    add_boundary()

            # update physics
            dt = 1.0 / 60.0 / 2
            for x in range(2):
                space.step(dt)

            # draw screen
            if render:
                drawing_screen.fill(THECOLORS["white"])


                # draw the actual screen
                space.debug_draw(options)
                pygame.transform.scale(drawing_screen, display_dimensions, screen)
                pygame.display.flip()
                pygame.display.set_caption('nerve morph step {} of {}'.format(morph_index, len(morph_steps)))

            loop_count += 1

    def deform_steps(self, start: Trace, end: Trace, count: int = 2) -> List[Trace]:
        # Find point along old_nerve that is closest to major axis of best fit ellipse
        (x, y), (a, b), angle = start.ellipse()

        angle *= 2 * np.pi / 360
        print(angle)

        ray = LineString([(x, y), (x + (2 * a * np.cos(angle)),  y + (2 * a * np.sin(angle)))])

        start_intersection = ray.intersection(start.polygon().boundary)
        end_intersection = ray.intersection(end.polygon().boundary)

        start_distances = [Point(point[:2]).distance(start_intersection) for point in start.points]
        end_distances = [Point(point[:2]).distance(end_intersection) for point in end.points]

        # Use point on major axis as the first point on old_nerve, find closest point on new_nerve
        # and assign as first point

        # Sweep CW assigning consecutive points
        start_initial_index = np.where(np.array(start_distances == np.min(start_distances)))[0][0]
        end_initial_index = np.where(np.array(end_distances == np.min(end_distances)))[0][0]

        start_i = start_initial_index
        end_i = end_initial_index
        associated_points = [(0, 0)] * len(start.points)
        while True:
            associated_points[start_i] = (start.points[start_i], end.points[end_i])

            if start_i == len(start.points) - 1:
                start_i = 0
            else:
                start_i += 1

            if end_i == 0:
                end_i = len(end.points) - 1
            else:
                end_i -= 1

            if start_i == start_initial_index and end_i == end_initial_index:
                break

        # Find vector between old_nerve and new_nerve associated points
        vectors = [second - first for first, second in associated_points]

        # Save incremental steps of nerve
        ratios = np.linspace(0, 1, count)
        traces = []
        for ratio in ratios:
            trace = start.deepcopy()
            for i, point in enumerate(trace.points):
                point += vectors[i] * ratio
            traces.append(trace)

        return traces

    @staticmethod
    def from_slide(slide: Slide, mode: ReshapeNerveMode) -> 'Deformable':
        # method in slide will pull out each trace and add to a list of contents, go through traces and build polygons

        # get start boundary
        boundary_start = slide.nerve

        # get end boundary
        boundary_end = slide.reshaped_nerve(mode)

        # get contents
        contents = [fascicle.outer for fascicle in slide.fascicles]

        # exception configuration data
        exception_config_data = slide.configs[ConfigKey.EXCEPTIONS.value]

        # return new object
        return Deformable(exception_config_data, boundary_start, boundary_end, contents)






