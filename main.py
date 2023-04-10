import numpy as np
import splaytree as SplayTree
import math


## RANDOM GEN PARAMS
TOLERANCE_MEAN = 0.5
TOLERANCE_STD = 0.1

QUALITY_MEAN = 0.5
QUALITY_STD = 0.1
        
INTERARRIVAL_TIME_MEAN = 1
INTERARRIVAL_TIME_STD = 0.1 
#note (sarah): for the exponential distribution, standard deviation=mean

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

class Customer:

    CurrentID = 0

    def __init__(self, num_paintings: int, rng):
        self.id: int = Customer.CurrentID
        Customer.CurrentID += 1

        self.favorite_style: Style = Style.random()

        # positive number, higher the tolerance the less affectec the customer is by the number of viewers
        self.tolerance: float = rng.normal(TOLERANCE_MEAN, TOLERANCE_STD)

        self.viewedPaintings = np.full(num_paintings, False)


        self.stats = CustomerStats()
       


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


    
class Event:
    def __init__(self, type: EventType, time: float, customer: Customer):
        self.time = time
        self.customer = customer
        self.type = type
    
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
        self.splaytree = SplayTree.SplayTree() #sarah: have to call .splaytree()

    def enqueue(self, n):
        self.splaytree.insert(n)

    def getMin(self):
        return self.splaytree.findMin()
    
    def dequeue(self):
        return self.splaytree.remove(self.splaytree.findMin())

class CustomerStats:
    def __init__(self):
        self.arrival_time = 0.0
        self.departure_time = 0.0
        self.num_paintings_viewed = 0
        self.total_viewing_time = 0.0
        self.score_history = []

#sarah: this is where customer class used to be
class SimStats:
    def __init__(self, num_customers, num_paintings):
        self.num_customers = num_customers
        self.num_paintings = num_paintings

        self.total_viewing_time = 0.0
        self.num_arrived = 0
        self.num_departed = 0
        self.num_paintings_viewed = 0
        self.num_leave_early = 0



    def printStats(self):
        average_viewing_time = self.total_viewing_time / self.num_paintings_viewed
        average_paintings_viewed = self.num_paintings_viewed / self.num_customers

        print("Average Viewing Time: " + str(average_viewing_time))
        print("Average Paintings Viewed: " + str(average_paintings_viewed))
        print("Number of Customers Arrived: " + str(self.num_arrived))
        print("Number of Customers Departed: " + str(self.num_departed))
        print("Number of Customers Left Early: " + str(self.num_leave_early))
        






class GallerySim:
    def __init__(self, num_paintings: int, num_customers: int, DEBUG=False):
        self.CustomersLeft = num_customers

        self.num_paintings = num_paintings
        self.num_customers = num_customers

        self.paintings = [Painting(i, Style.random()) for i in range(num_paintings)]

        self.stats = SimStats(self.num_customers, self.num_paintings)

        self.time = 0.0
        self.FutureEventList = EventList()

        self.rng = np.random.default_rng()
        self.customer = []

        # Schedule the first arrival
        self.ScheduleArrival()

        #THIS is our main loop (processes all events)
        while(self.stats.num_departed < self.num_customers):
            # get next event
            next_event = self.FutureEventList.dequeue()
            self.time = next_event.time

            if(DEBUG):
                print("Event Type: " + str(next_event.type) + " Time: " + str(self.time))

            # process event
            if next_event.type == EventType.ARRIVAL:
                print()
                self.ProcessArrival(next_event)
            elif next_event.type == EventType.DEPARTURE:
                self.ProcessDeparture(next_event)
            elif next_event.type == EventType.VIEWING:
                self.ProcessViewing(next_event)
            else:
                raise Exception("Invalid Event Type")
                


    def generateInterArrivalTime(self):
        return self.rng.exponential(INTERARRIVAL_TIME_MEAN)#, INTERARRIVAL_TIME_STD)
        #sarah: rng.exponential takes parameters scale: float, and size: (int or tuple of ints).
        #   doesn't take a parameter for std dev because it is calculated from the rate (ie. std=mean)

    def generateViewingTime(self):
        return self.rng.normal(VIEWING_TIME_MEAN, VIEWING_TIME_STD)

    def generateTolerance(self):
        return self.rng.normal(TOLERANCE_MEAN, TOLERANCE_STD)

    

    def Start(self):
        ## TODO, implement the while loop thing used in A3
        #this is our 'main' function, processes all our events
        

        pass


    def ProcessArrival(self, evt: Event):
        # So when the customer first arrives we basically just want to record the arrival then "move" them to their first painting
        evt.customer.stats.arrived = True
        self.stats.num_arrived += 1


        # Schedule the next arrival
        self.ScheduleArrival()




        pass


    def ScheduleArrival(self):
        # Scheduling the next arrival        
        
        next_arrival_time = self.time + self.generateInterArrivalTime()

        new_cust = Customer(self.num_paintings, self.rng) #sarah: added rng
        new_cust.arrival_time = next_arrival_time

        # create the next arrival event
        arrival_event = Event(EventType().ARRIVAL, next_arrival_time, new_cust)

        self.customer.append(new_cust)

        ## add the arrival to the future event list
        self.FutureEventList.enqueue(arrival_event)

    def ProcessDeparture(self, evt: Event):
        self.stats.num_departed += 1



    def ProcessMove(self, evt: Event):
        # Min score at which point the customer will leave instead of going to the next painting
        MIN_SCORE = 100

        customer = evt.customer

        # get the painting with the highest score
        painting_scores = np.array([customer.scorePainting(p) for p in self.paintings])
        best_painting: Painting #placeholder to define variable (fix!!)

        bestIndex = np.argmax(painting_scores)

        if(painting_scores[bestIndex] < MIN_SCORE):
            # If the person is leaving early
            if(customer.stats.num_paintings_viewed < self.num_paintings):
                self.stats.num_leave_early += 1

            # EVent is now a departure
            evt.type = EventType.DEPARTURE
            self.ProcessDeparture(evt)


        # begin viewing the painting
        viewing_time = customer.beginViewing(best_painting, self.time)
        customer.viewedPaintings[bestIndex] = True

        self.stats.total_viewing_time += viewing_time

        # Schedule the next MOVE
        self.FutureEventList.enqueue(Event(EventType.MOVE, self.time + viewing_time))

        customer.stats.total_viewing_time += viewing_time

        return


def main():
    '''Produce data for multiple scenarios (for scenario run simulation w/ 5 different random seeds)
        and process collected data.'''
    test = GallerySim(4,10, True)
    

if __name__ == '__main__':
    main()

