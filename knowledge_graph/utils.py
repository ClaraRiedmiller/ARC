from enum import Enum
import numpy as np

class StructuringElementMode(Enum):
    """
    An enumeration to represent different modes of structuring elements used in image processing.

    Attributes:
    -----------
    DIRECT : Enum
        Represents a direct (cross-shaped) structuring element.
    DIAGONAL : Enum
        Represents a diagonal (X-shaped) structuring element.
    EIGHT_WAY : Enum
        Represents an 8-way (3x3 all ones) structuring element.

    Methods:
    --------
    get_structuring_element():
        Returns the corresponding structuring element as a numpy array based on the mode.
        Raises a ValueError if the mode is unknown.
    """
    DIRECT = "direct"
    DIAGONAL = "diagonal"
    EIGHT_WAY = "8-way"

    def get_structuring_element(self):
        if self == StructuringElementMode.DIRECT:
            return np.array([[0, 1, 0],
                             [1, 1, 1],
                             [0, 1, 0]], dtype=bool)
        elif self == StructuringElementMode.DIAGONAL:
            return np.array([[1, 0, 1],
                             [0, 0, 0],
                             [1, 0, 1]], dtype=bool)
        elif self == StructuringElementMode.EIGHT_WAY:
            return np.ones((3, 3), dtype=bool)
        else:
            raise ValueError(f"Unknown mode='{self.value}'. Must be \"direct\", \"diagonal\", or \"8-way\".")