import os

from utils.SlideMap import SlideMap
from utils.ExceptionManager import ExceptionManager


my_exception_manager = ExceptionManager(os.path.join(os.getcwd(), '.config', 'exceptions.json'))

my_map = SlideMap(False, 'a/', my_exception_manager)

