import numpy as np


## CONSTANT PARAMS
TOLERANCE_MEAN = 0.5
TOLERANCE_STD = 0.1

QUALITY_MEAN = 0.5
QUALITY_STD = 0.1

## SCORE PARAMS
STYLE_CONSTANT = 0.1
PATIENCE_CONSTANT = 0.5
QUALITY_CONSTANT = 1.0


# enum of painting styles
class Style:
    BAROQUE = 0
    IMPRESSIONIST = 1
    MODERN = 2
    ABSTRACT = 3

    @staticmethod
    def random():
        return np.random.randint(0, 4)

class Painting:
    def __init__(self, id: int, style: Style):
        self.id = id
        self.style = style
        self.num_viewers = 0
        self.quality: float = np.random.normal(QUALITY_MEAN, QUALITY_STD)


class Customer:
    def __init__(self, id: int):
        self.id: int = id
        self.favorite_style: Style = Style.random()
        self.tolerance: float = np.random.normal(TOLERANCE_MEAN, TOLERANCE_STD)
        
    def scorePainting(self, painting: Painting) -> float:
        sameStyle = 1 if painting.style == self.favorite_style else 0

        # uses the tolerance and the number of viewers to calculate a score, 
        # score is increased by a multiple if the painting is the same style as the customer's favorite style
        return ((painting.num_viewers * 1/self.tolerance * PATIENCE_CONSTANT) + \
                (painting.quality * QUALITY_CONSTANT)) * \
                (sameStyle * STYLE_CONSTANT + 1)





