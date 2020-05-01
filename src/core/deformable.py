#!/usr/bin/env python3.7

# builtin
from typing import List, Tuple

# packages
import pymunk.pygame_util
import numpy as np
from shapely.geometry import LineString, Point

# access
from src.core import Trace, Slide
from src.utils import Exceptionable, SetupMode, ReshapeNerveMode, Config


class Deformable(Exceptionable):

    def __init__(self, exception_config: list, boundary_start: Trace, boundary_end: Trace, contents: List[Trace]):
        """
        :param exception_config: pre-loaded data
        :param boundary_start: original start trace
        :param boundary_end: end trace
        :param contents: list of traces assumed to be within boundary start, not required to be within boundary end.
        Assumed boundary end will be able to hold all contents.
        """

        # init superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        # initialize instance variables
        self.start = boundary_start
        self.end = boundary_end
        self.contents = contents

    def deform(self,
               morph_count: int = 100,
               morph_index_step: int = 10,
               render: bool = True,
               minimum_distance: float = 0.0,
               ratio: float = None) -> Tuple[List[tuple], List[float]]:
        """
        :param ratio:
        :param morph_count: number of incremental traces including the start and end of boundary
        :param morph_index_step: steps between loops of updating outer boundary, i.e. 1 is every loop,
        2 is every other loop...
        :param render: True if you care to see it happen... makes this method WAY slower
        :param minimum_distance: separation between original inputs
        :return: tuple of a list of total movement vectors and total angle rotated for each fascicle
        """

        # copy the "contents" so multiple deformations are possible
        contents = [trace.deepcopy() for trace in self.contents]

        bounds = self.start.polygon().bounds
        width = int(1.5 * (bounds[2] - bounds[0]))
        height = int(1.5 * (bounds[3] - bounds[1]))

        # offset all the traces to provide for an effective minimum distance for original fascicles
        for trace in contents:
            trace.offset(distance=minimum_distance / 2.0)

        # initialize drawing vars, regardless of whether or not actually rendering
        # these have been moved below (if render...)
        drawing_screen = options = display_dimensions = screen = None

        # initialize the physics space (gravity is 0)
        space = pymunk.Space()

        # referencing the deform_steps method below
        morph_steps = [step.pymunk_segments(space) for step in Deformable.deform_steps(self.start,
                                                                                       self.end,
                                                                                       morph_count,
                                                                                       ratio)]

        # draw the deformation
        if render:
            # packages
            import pygame
            from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_SPACE
            from pygame.colordict import THECOLORS

            width = int(1.5 * (bounds[2] - bounds[0]))
            height = int(1.5 * (bounds[3] - bounds[1]))

            aspect = 2

            display_dimensions = int(800 * aspect), 800
            drawing_screen = pygame.display.set_mode(display_dimensions)

            # pygame.init()
            # drawing_screen = pygame.Surface((width, height))
            options = pymunk.pygame_util.DrawOptions(drawing_screen)
            options.shape_outline_color = (0, 0, 0, 255)
            options.shape_static_color = (0, 0, 0, 255)

        # init vector of start positions
        start_positions: List[np.ndarray] = []
        start_rotations: List[float] = []

        # add fascicles bodies to space
        fascicles = [trace.pymunk_poly() for trace in contents]
        for body, shape in fascicles:
            shape.elasticity = 0.0
            space.add(body, shape)
            start_positions.append(np.array(body.position))
            start_rotations.append(body.angle)

        def add_boundary():
            for seg in morph_step:
                seg.elasticity = 0.0
                seg.group = 1
            space.add(morph_step)

        def step_physics(space: pymunk.Space, count: int):
            dt = 1.0 / 60.0
            for x in range(count):
                space.step(dt)

        running = True
        loop_count = morph_index_step
        morph_index = 0
        morph_step = morph_steps[morph_index]
        add_boundary()

        while running:
            # if the loop count is divisible by the index step, update morph
            if render:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        running = False
                    elif event.type == KEYDOWN and event.key == K_SPACE:
                        pass

            if loop_count % morph_index_step == 0:
                # print('PRINT PRINT PRINT')
                space.remove(morph_step)
                morph_index += 1
                Deformable.printProgressBar(morph_index,
                                            len(morph_steps),
                                            prefix='\t\tdeforming',
                                            suffix='complete',
                                            length=50)
                # print('\tmorph step {} of {}'.format(morph_index, len(morph_steps)))

                if morph_index == len(morph_steps):
                    running = False
                else:
                    morph_step = morph_steps[morph_index]
                    add_boundary()

            # update physics
            step_physics(space, 3)

            # draw screen
            if render:
                drawing_screen.fill(THECOLORS["white"])

                # draw the actual screen
                space.debug_draw(options)

                temp_surf = drawing_screen.copy()
                # drawing_screen.fill((0,0,0))  # here, you can fill the screen with whatever you want to take the place of what was there before
                # drawing_screen.blit(temp_surf, (width/2,-height/2))

                # pygame.display.update()


                # drawing_screen = pygame.transform.scale(drawing_screen, display_dimensions)#, screen)
                pygame.display.flip()
                pygame.display.set_caption('nerve morph step {} of {}'.format(morph_index, len(morph_steps)))

            loop_count += 1

        step_physics(space, 500)

        # get end positions
        end_positions: List[np.ndarray] = []
        end_rotations: List[float] = []
        for body, _ in fascicles:
            end_positions.append(np.array(body.position))
            end_rotations.append(body.angle)

        # return total movement vectors (dx, dy)
        movements = [tuple(end - start) for start, end in zip(start_positions, end_positions)]
        rotations = [end - start for start, end in zip(start_rotations, end_rotations)]
        return movements, rotations

    @staticmethod
    def deform_steps(start: Trace, end: Trace, count: int = 2, deform_ratio: float = 1.0, slide: Slide = None) -> List[Trace]:
        # TODO: map orientation point index to new index -> need to return this?

        # Find point along old_nerve that is closest to major axis of best fit ellipse
        (x, y), (a, b), angle = start.ellipse()  # returns degrees

        angle *= 2 * np.pi / 360  # converts to radians

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

        # Match pre and post-deformation nerve points. Increment one, decrement the other
        # to match rotation of trace points.
        while True:
            associated_points[start_i] = (start.points[start_i], end.points[end_i])

            # map slide.orientation_point_index
            if (slide is not None) and\
               (slide.orientation_point_index is not None) and\
               (slide.orientation_point_index == start_i):
                slide.orientation_point_index = end_i

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

        return traces[:int((deform_ratio if deform_ratio is not None else 1) * count)]

    @staticmethod
    def from_slide(slide: Slide, mode: ReshapeNerveMode, minimum_distance: float = 0.0, nerve_add: float = None) -> 'Deformable':
        # method in slide will pull out each trace and add to a list of contents, go through traces and build polygons

        bounds = slide.nerve.polygon().bounds
        width = int(1.5 * (bounds[2] - bounds[0])) / 2
        height = int(1.5 * (bounds[3] - bounds[1])) / 2

        slide.move_center(np.array([1.5 * width, 1.5 * height]))

        # get start boundary
        boundary_start = slide.nerve.deepcopy()

        # get end boundary
        if nerve_add is None:
            nerve_add = 0.0
        boundary_end = slide.reshaped_nerve(mode, buffer=minimum_distance + nerve_add).deepcopy()

        # get contents
        contents = [fascicle.outer.deepcopy() for fascicle in slide.fascicles]

        # exception configuration data
        exception_config_data = slide.configs[Config.EXCEPTIONS.value]

        slide.move_center(np.array([0, 0]))

        # return new object
        return Deformable(exception_config_data, boundary_start, boundary_end, contents)

    # copied from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    @staticmethod
    def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r{} |{}| {}% {}'.format(prefix, bar, percent, suffix), end='')
        # Print New Line on Complete
        if iteration == total:
            print()






