import numpy as np
import splaytree as SplayTree


## RANDOM GEN PARAMS
TOLERANCE_MEAN = 0.5
TOLERANCE_STD = 0.1

QUALITY_MEAN = 0.5
QUALITY_STD = 0.1
        
INTERARRIVAL_TIME_MEAN = 1
INTERARRIVAL_TIME_STD = 0.1

VIEWING_TIME_MEAN = 1
VIEWING_TIME_STD = 0.1


## SCORE PARAMS
## Adjustes relativve weight of each score.
## all between 0 and 1
STYLE_CONSTANT = 1.0
PATIENCE_CONSTANT = 1.0
QUALITY_CONSTANT = 1.0

# enum of event types
class EventType:
    ARRIVAL = 0
    DEPARTURE = 1
    MOVE = 2

    def __str__(self):
        if self == EventType.ARRIVAL:
            return "ARRIVAL"
        elif self == EventType.DEPARTURE:
            return "DEPARTURE"
        elif self == EventType.MOVE:
            return "MOVE"
        else:
            return "UNKNOWN"

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
    
class Event:
    def __init__(self, type: EventType, time: float, customer: Customer):
        self.time = time
        self.customer = customer
        self.event_type = type
    
    def get_time(self):
        return self.time

    def __lt__(self, other):
        return self.time < other.get_time()

    def __eq__(self, other):
        return self.time == other.get_time()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

### EVENT LIST CODE ###
class EventList:

    def __init__(self):
        self.splaytree = SplayTree()

    def enqueue(self, n):
        self.splaytree.insert(n)

    def getMin(self):
        return self.splaytree.findMin()
    
    def dequeue(self):
        return self.splaytree.remove(self.splaytree.findMin())

class Customer:
    def __init__(self, id: int, num_paintings: int):
        self.id: int = id
        self.favorite_style: Style = Style.random()

        # positive number, higher the tolerance the less affectec the customer is by the number of viewers
        self.tolerance: float = np.random.normal(TOLERANCE_MEAN, TOLERANCE_STD)

        self.arrival_time: float = np.random.normal(INTERARRIVAL_TIME_MEAN, INTERARRIVAL_TIME_STD)

        self.viewedPaintings = np.full(num_paintings, False)

    def beginViewing(self, painting: Painting, time: float):
        painting.num_viewers += 1
        self.viewing_time: float = np.random.normal(VIEWING_TIME_MEAN, VIEWING_TIME_STD)
        return self.viewing_time

    def calcViewerScore(self, num_viewers):
        return 1/(max(math.sqrt(num_viewers) * 1/self.tolerance, 1)) * PATIENCE_CONSTANT * 100
    
    def calcQualityScore(self, quality):
        # Higher this is the lower the slope in the middle
        SLOPE_CONSTANT = 10
        ## SHouldn't edit this, the midpoint of the inverse sigmoid is 0.5 at MIDPOINT_HEIGHT of 1. Instead adjust the QUALITY_CONSTANT
        ## Like you can edit this but you shouldn't need to unless you're doing fancy stuff
        MIDPOINT_HEIGHT = 1

        ## For quality we want to have low quality paintings be very undesirable and high quality very desirable but 25-75 should have less of an effect
        ## We can do this by using an inverse sigmoid function
        return (0.5 - math.log((1-quality)/(quality * MIDPOINT_HEIGHT))) * QUALITY_CONSTANT * 100
    
    def calcStyleScore(self, style):
        return 1 * STYLE_CONSTANT if style == self.favorite_style else 0

    def scorePainting(self, painting: Painting) -> float:
        if self.viewedPaintings[painting.id]:
            return -1

        # uses the tolerance and the number of viewers to calculate a score, 
        # score is increased by a multiple if the painting is the same style as the customer's favorite style
        qualityScore = self.calcQualityScore(painting.quality)
        viewerScore = self.calcViewerScore(painting.num_viewers)
        styleScore = self.calcStyleScore(painting.style)

        return qualityScore + viewerScore + styleScore

class SimStats:
    def __init__(self, num_customers: int, num_paintings: int):
        self.num_customers = num_customers
        self.num_paintings = num_paintings

        self.total_viewing_time = 0.0




class GallerySim:
    def __init__(self, num_paintings: int, num_customers: int):
        self.CustomersLeft = num_customers

        self.num_paintings = num_paintings
        self.num_customers = num_customers

        self.paintings = [Painting(i, Style.random()) for i in range(num_paintings)]

        self.time = 0.0
        self.FutureEventList = EventList()



    def processMove(self, customer: Customer):
        # get the painting with the highest score
        best_painting = max(self.paintings, key=lambda p: customer.scorePainting(p))

        # begin viewing the painting
        viewing_time = customer.beginViewing(best_painting, self.time)

        # add the future event



