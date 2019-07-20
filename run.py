import os

from src.core import *
from src.utils.exceptions import ExceptionManager


my_exception_manager = ExceptionManager(os.path.join(os.getcwd(), '.config', 'exceptions.json'))

my_map = SlideMap(False, 'a/', my_exception_manager)

