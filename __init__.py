__all__ = ["Yopmail"]

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
print(sys.path)
from .yopmail import Yopmail
