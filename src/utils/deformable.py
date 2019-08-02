# builtin
from typing import List

# physics
import pymunk.pygame_util

# rendering
import pygame
from pygame.locals import *
from pygame.camera import *

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

        # init space with default gravity (0, 0)
        self.space = pymunk.Space()

    def deform(self, boundary_step: int = 100, render: bool = True, render_step: int = 1) -> List[tuple]:
        pass

    def deform_steps(self, start: Trace, end: Trace, count: int) -> List[Trace]:
        pass

        # Find point along old_nerve that is closest to major axis of best fit ellipse
        (x, y), (a, b), angle = Trace.ellipse(self)

        # Use point on major axis as the first point on old_nerve, find closest point on new_nerve
        # and assign as first point
        

        # Sweep CW assigning consecutive points

        # Find vector between old_nerve and new_nerve associated points

        # Save incremental steps of nerve



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






