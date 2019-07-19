import os

from utils.Map import Map
from utils.ExceptionManager import ExceptionManager


my_exception_manager = ExceptionManager(os.path.join(os.getcwd(), '.config', 'exceptions.json'))

my_map = Map(False, 'a/', my_exception_manager)

