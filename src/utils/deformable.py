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
from src.utils import Exceptionable, SetupMode


class Deformable(Exceptionable):

    def __init__(self, exception_config: list, boundary_start: Trace, boundary_end: Trace, contents: List[Trace]):

        # init superclass
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        # init space with default gravity (0, 0)
        self.space = pymunk.Space()


    def deform(self, boundary_step: int = 100, render: bool = True, render_step: int = 1) -> List[tuple]:
        pass

    @staticmethod
    def deform_steps(start: Trace, stop: Trace) -> List[Trace]:


    @staticmethod
    def from_slide(slide: Slide) -> 'Deformable':
        pass


