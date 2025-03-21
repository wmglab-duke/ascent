#!/usr/bin/env python3.7

"""Defines the Deformable class.

The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing
instructions. The source code can be found on the following GitHub
repository: https://github.com/wmglab-duke/ascent
"""

import sys

import numpy as np
import pygame
import pymunk.pygame_util
from pygame.colordict import THECOLORS
from pygame.locals import DOUBLEBUF, HWSURFACE, K_ESCAPE, KEYDOWN, QUIT, RESIZABLE
from shapely.geometry import LineString, Point
from tqdm import tqdm

from src.core import Slide, Trace
from src.utils import ReshapeNerveMode


class Deformable:
    """Deforms a nerve cross-section."""

    def __init__(
        self,
        boundary_start: Trace,
        boundary_end: Trace,
        contents: list[Trace],
    ):
        """Initialize the class.

        :param boundary_start: original start trace
        :param boundary_end: end trace
        :param contents: list of traces assumed to be within boundary start, not required to be within boundary end.
            Assumes boundary end will be able to hold all contents.
        """
        # initialize instance variables
        self.start = boundary_start
        self.end = boundary_end
        self.contents = contents

        # init vector of start and end positions
        self.start_positions: list[np.ndarray] = []
        self.start_rotations: list[float] = []
        self.end_positions: list[np.ndarray] = []
        self.end_rotations: list[float] = []

    def setup_pygame_render(self):
        """Initialize the debug render mediated by pygame.

        :return: pygame surface, pymunk space, pygame draw options, pygame screen, image ratio
        """
        bounds = self.start.polygon().bounds
        width = int(1 * (bounds[2] + bounds[0]))
        height = int(1 * (bounds[3] + bounds[1]))
        im_ratio = height / width

        # Initialize screen and surface which each frame will be drawn on
        screen = pygame.display.set_mode((800, int(800 * im_ratio)), HWSURFACE | DOUBLEBUF | RESIZABLE)
        drawsurf = pygame.Surface((width, height))
        # pygame debug draw options
        options = pymunk.pygame_util.DrawOptions(drawsurf)
        options.shape_outline_color = (0, 0, 0, 255)
        options.shape_static_color = (0, 0, 0, 255)

        return options, drawsurf, screen, im_ratio

    @staticmethod
    def draw_pygame(drawsurf, space, options, screen, im_ratio, morph_index, morph_steps):
        """Draws the current morphology state onto the pygame render surface.

        :param drawsurf: pygame surface to draw on
        :param space: pymunk space to draw from
        :param options: pygame draw options
        :param screen: pygame screen to draw on
        :param im_ratio: image ratio
        :param morph_index: current morph index
        :param morph_steps: list of morph steps
        """
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit()

        # add white fill and draw objects on surface
        drawsurf.fill(THECOLORS["white"])
        space.debug_draw(options)
        # resize surface and project on screen
        screen.blit(
            pygame.transform.flip(
                pygame.transform.scale(drawsurf, (800, int(800 * im_ratio))),
                False,
                True,
            ),
            (0, 0),
        )
        pygame.display.flip()
        pygame.display.set_caption(f'nerve morph step {morph_index} of {len(morph_steps)}')

    def deform_initialize(self, minimum_distance, morph_count, ratio):
        """Set up the necessary variables for deformation.

        :param minimum_distance: minimum distance between fascicles.
        :param morph_count: number of morph steps to use.
        :param ratio: deform ratio.
        :return: morph steps (list of pymunk segments), pymunk space, fascicle polygons
        """
        contents = [trace.deepcopy() for trace in self.contents]

        # offset all the traces to provide for an effective minimum distance for original fascicles
        for trace in contents:
            trace.offset(distance=minimum_distance / 2.0)

        # initialize the physics space (gravity is 0)
        space = pymunk.Space()

        # referencing the deform_steps method below
        morph_steps = [
            step.pymunk_segments(space) for step in Deformable.deform_steps(self.start, self.end, morph_count, ratio)
        ]

        # add fascicles bodies to space
        fascicles = [trace.pymunk_poly() for trace in contents]
        for body, shape in fascicles:
            shape.elasticity = 0.0
            space.add(body, shape)
            self.start_positions.append(np.array(body.position))
            self.start_rotations.append(body.angle)

        return morph_steps, space, fascicles

    def deform(
        self,
        morph_count: int = 100,
        morph_index_step: int = 10,
        render: bool = True,
        minimum_distance: float = 0.0,
        ratio: float = None,
        progress_bar: bool = True,
    ) -> tuple[list[tuple], list[float]]:
        """Run the main deformation algorithm.

        :param morph_count: number of incremental traces including the start and end of boundary
        :param morph_index_step: steps between loops of updating outer boundary, i.e. 1 is every loop,
            2 is every other loop...
        :param render: True if you care to see it happen... makes this method WAY slower
        :param minimum_distance: separation between original inputs
        :param ratio: deform ratio
        :param progress_bar: whether to print a progress bar during deformation
        :return: tuple of a list of total movement vectors and total angle rotated for each fascicle
        """
        # copy the "contents" so multiple deformations are possible

        def add_boundary(space, morph_step):
            for seg in morph_step:
                seg.elasticity = 0.0
                seg.group = 1
            space.add(*morph_step)

        def step_physics(space: pymunk.Space, count: int):
            dt = 1.0 / 60.0
            for _ in range(count):
                space.step(dt)

        # setup
        morph_steps, space, fascicles = self.deform_initialize(minimum_distance, morph_count, ratio)

        # draw the deformation
        if render:
            options, drawsurf, screen, im_ratio = self.setup_pygame_render()

        # MORPHING LOOP
        for morph_index, morph_step in tqdm(
            enumerate(morph_steps),
            total=len(morph_steps),
            dynamic_ncols=True,
            disable=(not progress_bar),
            desc='deforming',
        ):

            # add new nerve trace
            add_boundary(space, morph_step)

            # update physics
            for _ in range(morph_index_step):
                step_physics(space, 3)

            # draw screen
            if render:
                self.draw_pygame(drawsurf, space, options, screen, im_ratio, morph_index, morph_steps)

            # don't remove if this is the last morph step for later stepping of physics
            if morph_index != len(morph_steps) - 1:
                space.remove(*morph_step)

        step_physics(space, 500)
        # get end positions
        for body, _ in fascicles:
            self.end_positions.append(np.array(body.position))
            self.end_rotations.append(body.angle)

        # return total movement vectors (dx, dy)
        movements = [tuple(end - start) for start, end in zip(self.start_positions, self.end_positions)]
        rotations = [end - start for start, end in zip(self.start_rotations, self.end_rotations)]
        return movements, rotations

    @staticmethod
    def deform_steps(
        start: Trace,
        end: Trace,
        count: int = 2,
        deform_ratio: float = 1.0,
    ) -> list[Trace]:
        """Calculate morph steps between two traces.

        :param start: start trace
        :param end: end trace
        :param count: number of morph steps
        :param deform_ratio: deform ratio
        :return: list of morph steps
        """
        # Find point along old_nerve that is closest to major axis of best fit ellipse
        (x, y), (a, b), angle = start.ellipse()  # returns degrees

        angle *= 2 * np.pi / 360  # converts to radians

        ray = LineString([(x, y), (x + (2 * a * np.cos(angle)), y + (2 * a * np.sin(angle)))])

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
        if deform_ratio == 0:  # still need fascicle sep physics with deform_ratio = 0, so pass starting trace only
            return [traces[0]]
        return traces[: int((deform_ratio if deform_ratio is not None else 1) * count)]

    @staticmethod
    def from_slide(slide: Slide, mode: ReshapeNerveMode, sep_nerve: float = None) -> 'Deformable':
        """Create a Deformable object from a Slide object.

        :param slide: Slide object
        :param mode: ReshapeNerveMode enum
        :param sep_nerve: separation between nerve and fascicles
        :return: Deformable object
        """
        # method in slide will pull out each trace and add to a list of contents, go through traces and build polygons

        bounds = slide.nerve.polygon().bounds
        width = int(1.5 * (bounds[2] - bounds[0])) / 2
        height = int(1.5 * (bounds[3] - bounds[1])) / 2

        slide.move_center(np.array([1.5 * width, 1.5 * height]))

        # get start boundary
        boundary_start = slide.nerve.deepcopy()

        # get end boundary
        if sep_nerve is None:
            sep_nerve = 0.0
        boundary_end = slide.reshaped_nerve(mode, buffer=sep_nerve).deepcopy()

        # get contents
        contents = [fascicle.outer.deepcopy() for fascicle in slide.fascicles]

        slide.move_center(np.array([0, 0]))

        # return new object
        return Deformable(boundary_start, boundary_end, contents)
