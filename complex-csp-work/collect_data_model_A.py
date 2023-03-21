import math
import random
from graphics import *

#          DATA COLLECTION FOR path_creation_model_A           #
# Modify UNMOVABLE_MIN_DIST_APART to alter unmovable placement #
#   D_WIN_WIDTH limits unmovable spawn to inside that range    #
#   D_WIN_HEIGHT limits unmovable spawn to inside that range   #
#                                                              #
#     Change number of times to run the program in main()!     #
#           Change global variable values in main()!           #
#  Uncomment areas marked with '[D]' to re-enable the visuals  #

# Global variables [Important]
NUM_OF_AGENTS = 0
NUM_OF_UNMOVABLE_PICKUPS = 0
NUM_OF_MOVABLE_PICKUPS = 0
STOP_MOTION_PLACEMENTS = False  # Enables a stop-motion effect for case #1 if True

# Global variables [Window]
WIN_WIDTH, WIN_HEIGHT = 0, 0
NUM_OF_ITERATIONS = 0

# Global variables [Data Collection]
MAX_NUM_OF_ITERATIONS = 0
UNMOVABLE_MIN_DIST_APART = 0
D_WIN_WIDTH, D_WIN_HEIGHT = 0, 0
D_TOP_LEFT_X, D_TOP_LEFT_Y = WIN_WIDTH - D_WIN_WIDTH, WIN_HEIGHT - D_WIN_HEIGHT

# Global variables [Agents]
AGENT_RADIUS = 0
AGENT_VELOCITY = 0
TIME_BETWEEN_SET_DOWNS = 0
TIME_TO_NOT_PICK_UP = 0
FORCE_FACTOR = 0

NO_SPAWN_RANGE = 0  # X number of pixels away from the middle of the screen in all directions
FIND_PICKUPS_RANGE = 0
FIND_PICKUPS_RANGE_SQUARED = FIND_PICKUPS_RANGE ** 2
ATTRACTION_RANGE = 0
ATTRACTION_RANGE_SQUARED = ATTRACTION_RANGE ** 2
ATTRACTION_EXCLUSION_ZONE = 0
ATTRACTION_EXCLUSION_ZONE_SQUARED = ATTRACTION_EXCLUSION_ZONE ** 2

# Global variables [Pickups]
TOTAL_NUM_OF_PICKUPS = NUM_OF_UNMOVABLE_PICKUPS + NUM_OF_MOVABLE_PICKUPS
PICKUP_HEIGHT = 0
GRABBED_OBJECT_LIST = []
PLACED_PICKUP_POINTS = []

# Creates a white-colored screen for the agents to roam on that has dimensions divisible by 20.
# agents_window = 0  # [D]


class Agent(Circle):
    def __init__(self, point):
        Circle.__init__(self, center=point, radius=AGENT_RADIUS)
        Circle.setFill(self, color_rgb(255, 0, 0))  # Red
        self.dx = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)
        self.dy = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)

        if self.dx == 0:
            self.dx += AGENT_VELOCITY / 2

        if self.dy == 0:
            self.dy += AGENT_VELOCITY / 2

        self.is_holding = False
        self.just_picked_up = False

        self.set_down_cooldown = 0
        self.pick_up_cooldown = 0
        self.held_pickup_identity = ""


# All directions are open, but at most 1 can be open at a time.
class UnmovablePickup(Rectangle):
    def __init__(self, top_left, bottom_right):
        Rectangle.__init__(self, p1=top_left, p2=bottom_right)
        Rectangle.setFill(self, color_rgb(0, 0, 0))  # Black

        self.identity = "unmovable"
        self.line_id = 0  # A unique number assigned to each unmovable.
        self.on_path_id = "Z"  # A letter denoting the direction movables "branched" off of; "Z" for unmovables.
        self.on_path_counter = 0  # A number that increases by 1 each time a movable is attached to another (un)movable.
        self.on_correct_path = False
        self.score = -4

        self.north_open = True
        self.south_open = True
        self.east_open = True
        self.west_open = True


# All directions are open, but at most 2 can be open at a time.
class MovablePickup(Rectangle):
    def __init__(self, top_left, bottom_right):
        Rectangle.__init__(self, p1=top_left, p2=bottom_right)
        Rectangle.setFill(self, color_rgb(0, 0, 255))  # Blue

        self.identity = "movable"
        self.line_id = 0  # Number associated with the unmovable this movable is attached to.
        self.on_path_id = "Z"  # A letter denoting the direction movables "branched" off of; can be N/S/E/W.
        self.on_path_counter = 0  # A number that increases by 1 each time a movable is attached to another (un)movable.
        self.on_correct_path = False
        self.score = -2

        self.north_open = True
        self.south_open = True
        self.east_open = True
        self.west_open = True


def update_num_of_agents(num_agents_per_row):
    global NUM_OF_AGENTS
    NUM_OF_AGENTS = num_agents_per_row ** 2


def update_num_of_iterations():
    global NUM_OF_ITERATIONS
    NUM_OF_ITERATIONS += 1


def updated_placed_pickup_points(new_pickup_points):
    global PLACED_PICKUP_POINTS
    PLACED_PICKUP_POINTS = new_pickup_points


def create_pickups(x_low, x_high, y_low, y_high):
    list_of_pickups = []
    center = Point(0, 0)
    unmovable_counter = 1
    global PLACED_PICKUP_POINTS

    for _ in range(NUM_OF_UNMOVABLE_PICKUPS):
        overlapping_pickups = True

        while overlapping_pickups is True:
            center = Point(
                random.randint(1, int((WIN_WIDTH - PICKUP_HEIGHT) / PICKUP_HEIGHT)) * PICKUP_HEIGHT,
                random.randint(1, int((WIN_HEIGHT - PICKUP_HEIGHT) / PICKUP_HEIGHT)) * PICKUP_HEIGHT
            )

            overlapping_pickups = False

            # Unmovable is not inside bounding area specified by D_TOP_LEFT_X and D_TOP_LEFT_Y.
            if center.getX() <= D_TOP_LEFT_X or center.getY() <= D_TOP_LEFT_Y:
                overlapping_pickups = True
            # Unmovable is not inside bounding area specified by D_WIN_WIDTH and D_WIN_HEIGHT.
            if center.getX() >= D_WIN_WIDTH or center.getY() >= D_WIN_HEIGHT:
                overlapping_pickups = True

            if overlapping_pickups is False:
                for pickup in list_of_pickups:
                    # An unmovable would be placed on top of one that already is placed; this cannot happen.
                    if center.getX() in range(int(pickup.getCenter().getX() - (PICKUP_HEIGHT * 2)),
                                              int(pickup.getCenter().getX() + (PICKUP_HEIGHT * 2)) + 1) and \
                            center.getY() in range(int(pickup.getCenter().getY() - (PICKUP_HEIGHT * 2)),
                                                   int(pickup.getCenter().getY() + (PICKUP_HEIGHT * 2)) + 1):
                        overlapping_pickups = True

                    # An unmovable is too close to another unmovable; specified by UNMOVABLE_MIN_DIST_APART.
                    distance_squared = ((center.getX() - pickup.getCenter().getX()) ** 2) + \
                                       ((center.getY() - pickup.getCenter().getY()) ** 2)
                    if distance_squared < (UNMOVABLE_MIN_DIST_APART ** 2):
                        overlapping_pickups = True

        pickup_to_add = UnmovablePickup(Point(center.getX() - PICKUP_HEIGHT / 2, center.getY() - PICKUP_HEIGHT / 2),
                                        Point(center.getX() + PICKUP_HEIGHT / 2, center.getY() + PICKUP_HEIGHT / 2))

        if pickup_to_add.getCenter().getX() + PICKUP_HEIGHT >= WIN_WIDTH:
            pickup_to_add.east_open = False
        if pickup_to_add.getCenter().getX() - PICKUP_HEIGHT <= 0:
            pickup_to_add.west_open = False
        if pickup_to_add.getCenter().getY() + PICKUP_HEIGHT >= WIN_HEIGHT:
            pickup_to_add.south_open = False
        if pickup_to_add.getCenter().getY() - PICKUP_HEIGHT <= 0:
            pickup_to_add.north_open = False

        pickup_to_add.line_id = unmovable_counter
        # pickup_to_add.draw(agents_window)  # [D]
        list_of_pickups.append(pickup_to_add)
        PLACED_PICKUP_POINTS.append(pickup_to_add.getCenter())

        unmovable_counter += 1

    for _ in range(NUM_OF_MOVABLE_PICKUPS):
        overlapping_pickups = True

        while overlapping_pickups is True:
            center = get_random_point(x_low, x_high, y_low, y_high)

            if len(list_of_pickups) == 0:
                overlapping_pickups = False
            else:
                overlapping_pickups = False

                for pickup in list_of_pickups:
                    if (pickup.getCenter().getX() - PICKUP_HEIGHT < center.getX() <
                        pickup.getCenter().getX() + PICKUP_HEIGHT) and \
                            (pickup.getCenter().getY() - PICKUP_HEIGHT < center.getY() <
                             pickup.getCenter().getY() + PICKUP_HEIGHT):
                        overlapping_pickups = True

        pickup_to_add = MovablePickup(Point(center.getX() - PICKUP_HEIGHT / 2, center.getY() - PICKUP_HEIGHT / 2),
                                      Point(center.getX() + PICKUP_HEIGHT / 2, center.getY() + PICKUP_HEIGHT / 2))
        # pickup_to_add.draw(agents_window)  # [D]
        list_of_pickups.append(pickup_to_add)
        PLACED_PICKUP_POINTS.append(pickup_to_add.getCenter())

    return list_of_pickups


def create_agents():
    list_of_agents = []

    # The number of agents in a row is determined by the square root of the chosen number of agents.
    num_agents_per_row = round(math.sqrt(NUM_OF_AGENTS))

    # The number of agents variable will need to be altered to reflect this change.
    update_num_of_agents(num_agents_per_row)

    middle_of_window_x = WIN_WIDTH / 2
    middle_of_window_y = WIN_HEIGHT / 2

    # Calculate the top-left most point using the middle of the screen.
    start_top_left_x = middle_of_window_x - (num_agents_per_row * 10)
    start_top_left_y = middle_of_window_y - (num_agents_per_row * 10)

    # Calculate the bottom-right point of the top-left most pickup.
    start_bottom_right_x = start_top_left_x + 20
    start_bottom_right_y = start_top_left_y + 20

    # Variables to store all the x and y coordinates for the new points.
    new_top_left_x = start_top_left_x
    new_top_left_y = start_top_left_y
    new_bottom_right_x = new_top_left_x + 20
    new_bottom_right_y = new_top_left_y + 20

    # Systematically create a num_agents_per_row by num_agents_per_row "square" of NUM_OF_AGENTS (rounded) agents.
    for i in range(num_agents_per_row):
        for j in range(num_agents_per_row):
            agent_to_add = Agent(Point((new_top_left_x + new_bottom_right_x) / 2,
                                       (new_top_left_y + new_bottom_right_y) / 2))

            # agent_to_add.draw(agents_window)  # [D]
            list_of_agents.append(agent_to_add)

            new_top_left_x += 20
            new_bottom_right_x += 20

        new_top_left_x = start_top_left_x
        new_top_left_y = start_top_left_y + ((i + 1) * 20)

        new_bottom_right_x = start_bottom_right_x
        new_bottom_right_y = start_bottom_right_y + ((i + 1) * 20)

    return list_of_agents


# Generates a random Point object that is outside the range of any agent.
def get_random_point(x_low, x_high, y_low, y_high):
    extra_buffer = 20
    top_left_no_spawn_x = ((WIN_WIDTH / 2) - NO_SPAWN_RANGE) - extra_buffer
    top_left_no_spawn_y = ((WIN_HEIGHT / 2) - NO_SPAWN_RANGE) - extra_buffer
    bottom_right_no_spawn_x = ((WIN_WIDTH / 2) + NO_SPAWN_RANGE) + extra_buffer
    bottom_right_no_spawn_y = ((WIN_HEIGHT / 2) + NO_SPAWN_RANGE) + extra_buffer

    x = random.randint(*random.choice([(x_low, top_left_no_spawn_x), (bottom_right_no_spawn_x, x_high)]))
    y = random.randint(*random.choice([(y_low, top_left_no_spawn_y), (bottom_right_no_spawn_y, y_high)]))

    return Point(x, y)


# A process used to determine if two paths (with differing line_id's) are able to connect.
def shortcut_technique(agent, nearby_pickup_0, nearby_pickup_1, agents_list, pickups_list,
                       x_low, x_high, y_low, y_high):
    global PLACED_PICKUP_POINTS

    # Step #1: Find the agent's position relative to the nearest (un)movable.
    agent_0_is_north = agent.getCenter().getY() < nearby_pickup_0.getCenter().getY() and \
                       (int(agent.getCenter().getX()) in range(
                           int(nearby_pickup_0.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                           int(nearby_pickup_0.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                       ))

    agent_0_is_south = agent.getCenter().getY() > nearby_pickup_0.getCenter().getY() and \
                       (int(agent.getCenter().getX()) in range(
                           int(nearby_pickup_0.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                           int(nearby_pickup_0.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                       ))

    agent_0_is_west = agent.getCenter().getX() < nearby_pickup_0.getCenter().getX() and \
                      (int(agent.getCenter().getY()) in range(
                          int(nearby_pickup_0.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                          int(nearby_pickup_0.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                      ))

    agent_0_is_east = agent.getCenter().getX() > nearby_pickup_0.getCenter().getX() and \
                      (int(agent.getCenter().getY()) in range(
                          int(nearby_pickup_0.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                          int(nearby_pickup_0.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                      ))

    # Step #1.5: Find the agent's position relative to the second nearest (un)movable.
    agent_1_is_north = agent.getCenter().getY() < nearby_pickup_1.getCenter().getY() and \
                       (int(agent.getCenter().getX()) in range(
                           int(nearby_pickup_1.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                           int(nearby_pickup_1.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                       ))

    agent_1_is_south = agent.getCenter().getY() > nearby_pickup_1.getCenter().getY() and \
                       (int(agent.getCenter().getX()) in range(
                           int(nearby_pickup_1.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                           int(nearby_pickup_1.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                       ))

    agent_1_is_west = agent.getCenter().getX() < nearby_pickup_1.getCenter().getX() and \
                      (int(agent.getCenter().getY()) in range(
                          int(nearby_pickup_1.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                          int(nearby_pickup_1.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                      ))

    agent_1_is_east = agent.getCenter().getX() > nearby_pickup_1.getCenter().getX() and \
                      (int(agent.getCenter().getY()) in range(
                          int(nearby_pickup_1.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                          int(nearby_pickup_1.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                      ))

    # Step 2: Calculate the coordinates for the movable-to-place.
    # The agent is to the north (above) of the first pickup.
    if agent_0_is_north:
        agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT \
                     - (PICKUP_HEIGHT / 2)
        agent_0_y2 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
        relative_pos_found_0 = True

    # The agent is to the south (below) of the first pickup.
    elif agent_0_is_south:
        agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_0_y1 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
        agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT \
                     + (PICKUP_HEIGHT / 2)
        relative_pos_found_0 = True

    # The agent is to the west (left) of the first pickup.
    elif agent_0_is_west:
        agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT \
                     - (PICKUP_HEIGHT / 2)
        agent_0_x2 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
        agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
        relative_pos_found_0 = True

    # The agent is to the east (right) of the first pickup.
    elif agent_0_is_east:
        agent_0_x1 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT \
                     + (PICKUP_HEIGHT / 2)
        agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
        agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
        relative_pos_found_0 = True

    # The agent is neither north, south, east, nor west of the first pickup.
    else:
        return False

    # The agent is to the north (above) of the second pickup.
    if agent_1_is_north:
        agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT \
                     - (PICKUP_HEIGHT / 2)
        agent_1_y2 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
        relative_pos_found_1 = True

    # The agent is to the south (below) of the second pickup.
    elif agent_1_is_south:
        agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_1_y1 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
        agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT \
                     + (PICKUP_HEIGHT / 2)
        relative_pos_found_1 = True

    # The agent is to the west (left) of the second pickup.
    elif agent_1_is_west:
        agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT \
                     - (PICKUP_HEIGHT / 2)
        agent_1_x2 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
        agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
        agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
        relative_pos_found_1 = True

    # The agent is to the east (right) of the second pickup.
    elif agent_1_is_east:
        agent_1_x1 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
        agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT \
                     + (PICKUP_HEIGHT / 2)
        agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
        agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
        relative_pos_found_1 = True

    # The agent is neither north, south, east, nor west of the second pickup.
    else:
        return False

    # A movable should NOT be able to be placed outside the boundaries of the window.
    if agent_0_x1 >= WIN_WIDTH or agent_0_x2 >= WIN_WIDTH or \
            agent_0_y1 >= WIN_HEIGHT or agent_0_y2 >= WIN_HEIGHT:
        return False

    if agent_0_x1 <= 0 or agent_0_x2 <= 0 or agent_0_y1 <= 0 or agent_0_y2 <= 0:
        return False

    if agent_1_x1 >= WIN_WIDTH or agent_1_x2 >= WIN_WIDTH or \
            agent_1_y1 >= WIN_HEIGHT or agent_1_y2 >= WIN_HEIGHT:
        return False

    if agent_1_x1 <= 0 or agent_1_x2 <= 0 or agent_1_y1 <= 0 or agent_1_y2 <= 0:
        return False

    # Step 3: Are both of the newly-calculated points the same?
    if relative_pos_found_0 is True and relative_pos_found_1 is True:
        points_match = (agent_0_x1 == agent_1_x1) and (agent_0_y1 == agent_1_y1) and \
                       (agent_0_x2 == agent_1_x2) and (agent_0_y2 == agent_1_y2)
    else:
        return False

    # Step 4: Can the movable actually be placed in the desired location?
    if points_match is True:
        no_overlap = True

        for pickup in pickups_list:
            pickup_x1 = pickup.getCenter().getX() - PICKUP_HEIGHT / 2
            pickup_y1 = pickup.getCenter().getY() - PICKUP_HEIGHT / 2
            pickup_x2 = pickup.getCenter().getX() + PICKUP_HEIGHT / 2
            pickup_y2 = pickup.getCenter().getY() + PICKUP_HEIGHT / 2

            if (pickup_x1 == agent_0_x1) and (pickup_y1 == agent_0_y1) and \
                    (pickup_x2 == agent_0_x2) and (pickup_y2 == agent_0_y2):
                return False
    else:
        return False

    # Step 5: The movable can be placed, so let's place it down.
    # If this happened, then a successful path was created!
    if no_overlap is True:
        moved_pickup = MovablePickup(Point(agent_0_x1, agent_0_y1),
                                     Point(agent_0_x2, agent_0_y2))
        moved_pickup.setFill(color_rgb(0, 255, 0))  # Green
        moved_pickup.setOutline(color_rgb(0, 0, 0))  # Black
        moved_pickup.on_path_id = "CONNECTED"
        moved_pickup.line_id = nearby_pickup_0.line_id

        # moved_pickup.draw(agents_window)  # [D]
        pickups_list.append(moved_pickup)

        agent.setFill(color_rgb(255, 0, 0))  # Red
        agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
        agent.is_holding = False
        agent.just_picked_up = True
        agent.held_pickup_identity = ""

        # Step 6: Identify all the movables that were used and not used in the correct path.
        # Then, only free movables that have the same path_id's as the ones on the path.
        num_remaining_pickups = 0

        # Note: We do NOT want to remove any unmovables from the window.
        for pickup in pickups_list:
            if (pickup.line_id == nearby_pickup_0.line_id or
                pickup.line_id == nearby_pickup_1.line_id) and \
                    pickup.identity == "movable":
                if pickup.score != -2 and pickup.line_id == nearby_pickup_0.line_id and \
                        pickup.on_path_id == nearby_pickup_0.on_path_id and \
                        pickup.on_path_counter <= nearby_pickup_0.on_path_counter:
                    pickup.setFill(color_rgb(0, 255, 255))  # Light Blue
                    pickup.on_correct_path = True

                    pickup.identity = "permanent"
                    pickup.north_open = False
                    pickup.south_open = False
                    pickup.west_open = False
                    pickup.east_open = False

                elif pickup.score != -2 and pickup.line_id == nearby_pickup_1.line_id and \
                        pickup.on_path_id == nearby_pickup_1.on_path_id \
                        and pickup.on_path_counter <= nearby_pickup_1.on_path_counter:
                    pickup.setFill(color_rgb(0, 255, 255))  # Light Blue
                    pickup.on_correct_path = True

                    pickup.identity = "permanent"
                    pickup.north_open = False
                    pickup.south_open = False
                    pickup.west_open = False
                    pickup.east_open = False

                elif pickup.on_path_id == "CONNECTED":
                    pickup.setFill(color_rgb(0, 0, 100))  # Dark Blue
                    pickup.on_correct_path = True

                    pickup.identity = "permanent"
                    pickup.north_open = False
                    pickup.south_open = False
                    pickup.west_open = False
                    pickup.east_open = False

                elif pickup.on_path_id == nearby_pickup_0.on_path_id and \
                        pickup.on_path_counter > nearby_pickup_0.on_path_counter and \
                        pickup.line_id == nearby_pickup_0.line_id:
                    num_remaining_pickups += 1

                    pickup.identity = "gone"
                    pickup.undraw()

                elif pickup.on_path_id == nearby_pickup_1.on_path_id and \
                        pickup.on_path_counter > nearby_pickup_1.on_path_counter and \
                        pickup.line_id == nearby_pickup_1.line_id:
                    num_remaining_pickups += 1

                    pickup.identity = "gone"
                    pickup.undraw()

        # Commented out for data collection purposes.
        # agents_window.getMouse()

        # Step 7: Update the agents and randomize the locations of the remaining movables.
        for maybe_holding_agent in agents_list:
            if maybe_holding_agent.is_holding is True:
                maybe_holding_agent.setFill(color_rgb(255, 0, 0))  # Red
                maybe_holding_agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                maybe_holding_agent.pick_up_cooldown = 0
                maybe_holding_agent.is_holding = False
                maybe_holding_agent.just_picked_up = False
                maybe_holding_agent.held_pickup_identity = ""

                num_remaining_pickups += 1

        if len(pickups_list) + num_remaining_pickups > TOTAL_NUM_OF_PICKUPS:
            difference = (len(pickups_list) + num_remaining_pickups) - TOTAL_NUM_OF_PICKUPS
            num_remaining_pickups -= difference

        PLACED_PICKUP_POINTS = []

        while num_remaining_pickups != 0:
            center = get_random_point(x_low, x_high, y_low, y_high)
            pickup_to_add = MovablePickup(Point(center.getX() - PICKUP_HEIGHT / 2,
                                                center.getY() - PICKUP_HEIGHT / 2),
                                          Point(center.getX() + PICKUP_HEIGHT / 2,
                                                center.getY() + PICKUP_HEIGHT / 2))

            # pickup_to_add.draw(agents_window)  # [D]
            pickups_list.append(pickup_to_add)
            PLACED_PICKUP_POINTS.append(pickup_to_add.getCenter())

            num_remaining_pickups -= 1

        # Commented out for data collection purposes.
        # agents_window.getMouse()
        return True


def agent_animation(agents_list, pickups_list, x_low, x_high, y_low, y_high):
    continue_experiment = True
    num_successful_paths = 0
    num_iterations_per_path = []
    new_pickup_points = []
    global PLACED_PICKUP_POINTS
    global NUM_OF_ITERATIONS

    while continue_experiment:
        for agent in agents_list:
            agent.just_picked_up = False

            # The agent is holding a movable.
            if agent.is_holding is True:
                new_agent_dx = agent.dx
                new_agent_dy = agent.dy

                # There is a 1/100 chance that the agent's movement will be randomized.
                randomize_movement = random.randrange(0, 100)
                if randomize_movement == 0:
                    new_agent_dx = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)
                    new_agent_dy = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)

                    if new_agent_dx == 0:
                        randomize_sign = random.randrange(0, 2)
                        if randomize_sign == 0:
                            new_agent_dx = AGENT_VELOCITY / 2
                        else:
                            new_agent_dx = -AGENT_VELOCITY / 2

                    if new_agent_dy == 0:
                        randomize_sign = random.randrange(0, 2)
                        if randomize_sign == 0:
                            new_agent_dy = AGENT_VELOCITY / 2
                        else:
                            new_agent_dy = -AGENT_VELOCITY / 2

                # ATTRACT cases if the agent is HOLDING a movable:
                # Any movable with a score of -1.
                # Any unmovable with a score from -4 to -1.
                for pickup in pickups_list:
                    if (pickup.identity == "movable" and pickup.score == -1) or \
                            (pickup.identity == "unmovable" and pickup.score in range(-4, 0)):
                        distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                           ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                        if ATTRACTION_EXCLUSION_ZONE_SQUARED <= distance_squared <= ATTRACTION_RANGE_SQUARED:
                            attract_force_x = 1 - (FORCE_FACTOR * math.sqrt(distance_squared))
                            attract_force_y = 1 - (FORCE_FACTOR * math.sqrt(distance_squared))

                            # Calculates the component of the force in each direction.
                            attract_force_x = attract_force_x * \
                                              (math.fabs(agent.getCenter().getX() - pickup.getCenter().getX())
                                               / math.sqrt(distance_squared))
                            attract_force_y = attract_force_y * \
                                              (math.fabs(agent.getCenter().getY() - pickup.getCenter().getY())
                                               / math.sqrt(distance_squared))

                            if agent.getCenter().getX() > pickup.getCenter().getX():
                                attract_force_x = -attract_force_x
                            if agent.getCenter().getY() > pickup.getCenter().getY():
                                attract_force_y = -attract_force_y

                            new_agent_dx += attract_force_x
                            new_agent_dy += attract_force_y

                # If the agent is moving too slow (with a positive x velocity), it needs a boost...
                if 0 < new_agent_dx < 1:
                    new_agent_dx += 1

                # If the agent is moving too slow (with a negative x velocity), it needs a boost...
                if -1 > new_agent_dx > 0:
                    new_agent_dx -= 1

                # If the agent is moving too slow (with a positive y velocity), it needs a boost...
                if 0 < new_agent_dy < 1:
                    new_agent_dy += 1

                # If the agent is moving too slow (with a negative y velocity), it needs a boost...
                if -1 > new_agent_dy > 0:
                    new_agent_dy -= 1

                # If the agent hits the left side of the screen...
                if agent.getCenter().getX() < x_low:
                    if new_agent_dx < 0:
                        new_agent_dx = -new_agent_dx

                # If the agent hits the right side of the screen...
                if agent.getCenter().getX() > x_high:
                    if new_agent_dx > 0:
                        new_agent_dx = -new_agent_dx

                # If the agent hits the top of the screen...
                if agent.getCenter().getY() < y_low:
                    if new_agent_dy < 0:
                        new_agent_dy = -new_agent_dy

                # If the agent hits the bottom of the screen...
                if agent.getCenter().getY() > y_high:
                    if new_agent_dy > 0:
                        new_agent_dy = -new_agent_dy

                # Ensuring that the final velocities will not exceed a certain threshold...
                if new_agent_dx > AGENT_VELOCITY:
                    new_agent_dx = AGENT_VELOCITY
                if new_agent_dx < -AGENT_VELOCITY:
                    new_agent_dx = -AGENT_VELOCITY
                if new_agent_dy > AGENT_VELOCITY:
                    new_agent_dy = AGENT_VELOCITY
                if new_agent_dy < -AGENT_VELOCITY:
                    new_agent_dy = -AGENT_VELOCITY

                agent.dx = new_agent_dx
                agent.dy = new_agent_dy

                agent.move(agent.dx, agent.dy)

                # Reduces an agent's cooldown to pick up another pickup, if applicable.
                if agent.pick_up_cooldown > 0:
                    agent.pick_up_cooldown -= 1

                # Determines if an agent should drop a pickup, if it is holding one.
                elif agent.pick_up_cooldown == 0:
                    nearby_pickup_indices = []
                    index_to_add = 0
                    case_number = 0

                    for pickup in pickups_list:
                        distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                           ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                        # Agents should be able to place their movable near movables with a score of -1 or 0.
                        if distance_squared < FIND_PICKUPS_RANGE_SQUARED and pickup.identity == "movable" and \
                                pickup.score != -2:
                            nearby_pickup_indices.append(index_to_add)

                        # Agents should be able to place their movable near unmovables with a score between -4 and -1.
                        elif distance_squared < FIND_PICKUPS_RANGE_SQUARED and pickup.identity == "unmovable" and \
                                pickup.score in range(-4, 0):
                            nearby_pickup_indices.append(index_to_add)

                        index_to_add += 1

                    if len(nearby_pickup_indices) >= 3:
                        length_indicator = len(nearby_pickup_indices)
                        sorted_pickup_indices = []

                        while length_indicator > 0:
                            smallest_distance = FIND_PICKUPS_RANGE_SQUARED
                            smallest_distance_index = -1

                            for index in nearby_pickup_indices:
                                distance_squared = \
                                    ((agent.getCenter().getX() - pickups_list[index].getCenter().getX()) ** 2) \
                                    + ((agent.getCenter().getY() - pickups_list[index].getCenter().getY()) ** 2)

                                if distance_squared < smallest_distance:
                                    smallest_distance = distance_squared
                                    smallest_distance_index = index

                            sorted_pickup_indices.append(smallest_distance_index)
                            nearby_pickup_indices.remove(smallest_distance_index)
                            length_indicator -= 1

                        nearby_pickup_indices = sorted_pickup_indices

                    # If there are no pickups nearby, do not continue.
                    if len(nearby_pickup_indices) == 0:
                        drop_pickup = False

                    # If there is only one pickup nearby, enter case #1.
                    elif len(nearby_pickup_indices) == 1:
                        case_number = 1
                        drop_pickup = True

                    # If there are 2 or more pickups nearby, enter case #2.
                    else:
                        case_number = 2
                        drop_pickup = True

                    if drop_pickup is True:
                        # Setting booleans that will be used for case #1 and case #2.
                        relative_pos_found = False
                        pickup_was_placed = False
                        placed_pickups_list = []

                        # ~~~~~ Case 2: ~~~~~ #
                        if case_number == 2:
                            nearby_one_score = pickups_list[nearby_pickup_indices[0]].score
                            nearby_one_identity = pickups_list[nearby_pickup_indices[0]].identity
                            nearby_two_score = pickups_list[nearby_pickup_indices[1]].score
                            nearby_two_identity = pickups_list[nearby_pickup_indices[1]].identity

                            if nearby_one_identity == "unmovable" and nearby_two_identity == "unmovable":
                                allow_shortcut = (nearby_one_score in range(-4, 0) and
                                                  nearby_two_score in range(-4, 0)) and \
                                                 (pickups_list[nearby_pickup_indices[0]].line_id !=
                                                  pickups_list[nearby_pickup_indices[1]].line_id)
                            elif nearby_one_identity == "unmovable" and nearby_two_identity == "movable":
                                allow_shortcut = (nearby_one_score in range(-4, 0) and
                                                  nearby_two_score in range(-1, 1)) and \
                                                 (pickups_list[nearby_pickup_indices[0]].line_id !=
                                                  pickups_list[nearby_pickup_indices[1]].line_id)
                            elif nearby_one_identity == "movable" and nearby_two_identity == "unmovable":
                                allow_shortcut = (nearby_one_score in range(-1, 1) and
                                                  nearby_two_score in range(-4, 0)) and \
                                                 (pickups_list[nearby_pickup_indices[0]].line_id !=
                                                  pickups_list[nearby_pickup_indices[1]].line_id)
                            # Both nearby pickups are movables.
                            else:
                                if nearby_one_identity == "permanent" or nearby_one_identity == "gone":
                                    allow_shortcut = False
                                else:
                                    allow_shortcut = (nearby_one_score in range(-1, 1) and
                                                      nearby_two_score in range(-1, 1)) and \
                                                     (pickups_list[nearby_pickup_indices[0]].line_id !=
                                                      pickups_list[nearby_pickup_indices[1]].line_id)

                            # The "shortcut" case is special from the normal behavior, so it is separated.
                            # Two movables with differing line_id's and scores of -1 or 0 are valid for shortcutting.
                            if allow_shortcut is True:
                                shortcut_success = shortcut_technique(agent, pickups_list[nearby_pickup_indices[0]],
                                                                      pickups_list[nearby_pickup_indices[1]],
                                                                      agents_list, pickups_list,
                                                                      x_low, x_high, y_low, y_high)
                                if shortcut_success is True:
                                    num_successful_paths += 1
                                    num_iterations_per_path.append(NUM_OF_ITERATIONS + 1)
                            else:
                                shortcut_success = False

                            # =---= Step 2: =---= #
                            # Check both nearby (un)movable's scores; if either one is 0, do not proceed.
                            # Otherwise, proceed.

                            if allow_shortcut is True and shortcut_success is True:
                                valid_score = False
                            elif allow_shortcut is True and shortcut_success is False:
                                valid_score = True
                            elif nearby_one_identity == "permanent" or nearby_one_identity == "gone":
                                valid_score = False
                            elif nearby_one_score == 0 or nearby_two_score == 0:
                                valid_score = False
                            else:
                                valid_score = True

                            # =---= Step 3: =---= #
                            # Set the "open" statuses for the two nearest (un)movables.

                            if valid_score is True:
                                nearby_north_status_0 = pickups_list[nearby_pickup_indices[0]].north_open
                                nearby_south_status_0 = pickups_list[nearby_pickup_indices[0]].south_open
                                nearby_east_status_0 = pickups_list[nearby_pickup_indices[0]].east_open
                                nearby_west_status_0 = pickups_list[nearby_pickup_indices[0]].west_open

                                nearby_north_status_1 = pickups_list[nearby_pickup_indices[1]].north_open
                                nearby_south_status_1 = pickups_list[nearby_pickup_indices[1]].south_open
                                nearby_east_status_1 = pickups_list[nearby_pickup_indices[1]].east_open
                                nearby_west_status_1 = pickups_list[nearby_pickup_indices[1]].west_open

                                all_statuses_set = True

                            else:
                                nearby_north_status_0 = False
                                nearby_south_status_0 = False
                                nearby_east_status_0 = False
                                nearby_west_status_0 = False

                                nearby_north_status_1 = False
                                nearby_south_status_1 = False
                                nearby_east_status_1 = False
                                nearby_west_status_1 = False

                                all_statuses_set = False

                            # =---= Step 4: =---= #
                            # Find the agent's position relative to the nearest (un)movables.
                            if all_statuses_set is True:
                                nearby_pickup_0 = pickups_list[nearby_pickup_indices[0]]

                                agent_0_is_north = agent.getCenter().getY() < nearby_pickup_0.getCenter().getY() and \
                                                   (int(agent.getCenter().getX()) in range(
                                                       int(nearby_pickup_0.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                       int(nearby_pickup_0.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                   ))

                                agent_0_is_south = agent.getCenter().getY() > nearby_pickup_0.getCenter().getY() and \
                                                   (int(agent.getCenter().getX()) in range(
                                                       int(nearby_pickup_0.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                       int(nearby_pickup_0.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                   ))

                                agent_0_is_west = agent.getCenter().getX() < nearby_pickup_0.getCenter().getX() and \
                                                  (int(agent.getCenter().getY()) in range(
                                                      int(nearby_pickup_0.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                      int(nearby_pickup_0.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                  ))

                                agent_0_is_east = agent.getCenter().getX() > nearby_pickup_0.getCenter().getX() and \
                                                  (int(agent.getCenter().getY()) in range(
                                                      int(nearby_pickup_0.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                      int(nearby_pickup_0.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                  ))

                                num_choices = 0

                                if agent_0_is_north is True:
                                    num_choices += 1
                                if agent_0_is_south is True:
                                    num_choices += 1
                                if agent_0_is_east is True:
                                    num_choices += 1
                                if agent_0_is_west is True:
                                    num_choices += 1

                                if num_choices >= 2:
                                    if agent_0_is_north is True and nearby_pickup_0.north_open is True:
                                        agent_0_is_north = True
                                        agent_0_is_south = False
                                        agent_0_is_east = False
                                        agent_0_is_west = False

                                    elif agent_0_is_south is True and nearby_pickup_0.south_open is True:
                                        agent_0_is_north = False
                                        agent_0_is_south = True
                                        agent_0_is_east = False
                                        agent_0_is_west = False

                                    elif agent_0_is_east is True and nearby_pickup_0.east_open is True:
                                        agent_0_is_north = False
                                        agent_0_is_south = False
                                        agent_0_is_east = True
                                        agent_0_is_west = False

                                    elif agent_0_is_west is True and nearby_pickup_0.west_open is True:
                                        agent_0_is_north = False
                                        agent_0_is_south = False
                                        agent_0_is_east = False
                                        agent_0_is_west = True

                                    else:
                                        if nearby_pickup_0.north_open is True:
                                            agent_0_is_north = True
                                            agent_0_is_south = False
                                            agent_0_is_east = False
                                            agent_0_is_west = False
                                        elif nearby_pickup_0.south_open is True:
                                            agent_0_is_north = False
                                            agent_0_is_south = True
                                            agent_0_is_east = False
                                            agent_0_is_west = False
                                        elif nearby_pickup_0.east_open is True:
                                            agent_0_is_north = False
                                            agent_0_is_south = False
                                            agent_0_is_east = True
                                            agent_0_is_west = False
                                        elif nearby_pickup_0.west_open is True:
                                            agent_0_is_north = False
                                            agent_0_is_south = False
                                            agent_0_is_east = False
                                            agent_0_is_west = True

                                # The agent is to the north (above) of the first pickup.
                                if agent_0_is_north and nearby_pickup_0.north_open is True:
                                    agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT \
                                                 - (PICKUP_HEIGHT / 2)
                                    agent_0_y2 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
                                    relative_pos_0 = "N"
                                    relative_pos_found_0 = True

                                # The agent is to the south (below) of the first pickup.
                                elif agent_0_is_south and nearby_pickup_0.south_open is True:
                                    agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_0_y1 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
                                    agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT \
                                                 + (PICKUP_HEIGHT / 2)
                                    relative_pos_0 = "S"
                                    relative_pos_found_0 = True

                                # The agent is to the west (left) of the first pickup.
                                elif agent_0_is_west and nearby_pickup_0.west_open is True:
                                    agent_0_x1 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT \
                                                 - (PICKUP_HEIGHT / 2)
                                    agent_0_x2 = nearby_pickup_0.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
                                    agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos_0 = "W"
                                    relative_pos_found_0 = True

                                # The agent is to the east (right) of the first pickup.
                                elif agent_0_is_east and nearby_pickup_0.east_open is True:
                                    agent_0_x1 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_0_x2 = nearby_pickup_0.getCenter().getX() + PICKUP_HEIGHT \
                                                 + (PICKUP_HEIGHT / 2)
                                    agent_0_y1 = nearby_pickup_0.getCenter().getY() - PICKUP_HEIGHT / 2
                                    agent_0_y2 = nearby_pickup_0.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos_0 = "E"
                                    relative_pos_found_0 = True

                                # The agent is neither north, south, east, nor west of the first pickup.
                                else:
                                    relative_pos_0 = "N/A"
                                    agent_0_x1, agent_0_y1, agent_0_x2, agent_0_y2 = -1, -1, -1, -1
                                    relative_pos_found_0 = False

                                # A movable should NOT be able to be placed outside the boundaries of the window.
                                if agent_0_x1 >= WIN_WIDTH or agent_0_x2 >= WIN_WIDTH or \
                                        agent_0_y1 >= WIN_HEIGHT or agent_0_y2 >= WIN_HEIGHT:
                                    if relative_pos_0 == "N":
                                        nearby_pickup_0.north_open = False
                                    elif relative_pos_0 == "S":
                                        nearby_pickup_0.south_open = False
                                    elif relative_pos_0 == "W":
                                        nearby_pickup_0.west_open = False
                                    elif relative_pos_0 == "E":
                                        nearby_pickup_0.east_open = False

                                    relative_pos_found_0 = False

                                if agent_0_x1 <= 0 or agent_0_x2 <= 0 or agent_0_y1 <= 0 or agent_0_y2 <= 0:
                                    if relative_pos_0 == "N":
                                        nearby_pickup_0.north_open = False
                                    elif relative_pos_0 == "S":
                                        nearby_pickup_0.south_open = False
                                    elif relative_pos_0 == "W":
                                        nearby_pickup_0.west_open = False
                                    elif relative_pos_0 == "E":
                                        nearby_pickup_0.east_open = False

                                    relative_pos_found_0 = False

                                nearby_pickup_1 = pickups_list[nearby_pickup_indices[1]]

                                agent_1_is_north = agent.getCenter().getY() < nearby_pickup_1.getCenter().getY() and \
                                                   (int(agent.getCenter().getX()) in range(
                                                       int(nearby_pickup_1.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                       int(nearby_pickup_1.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                   ))

                                agent_1_is_south = agent.getCenter().getY() > nearby_pickup_1.getCenter().getY() and \
                                                   (int(agent.getCenter().getX()) in range(
                                                       int(nearby_pickup_1.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                       int(nearby_pickup_1.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                   ))

                                agent_1_is_west = agent.getCenter().getX() < nearby_pickup_1.getCenter().getX() and \
                                                  (int(agent.getCenter().getY()) in range(
                                                      int(nearby_pickup_1.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                      int(nearby_pickup_1.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                  ))

                                agent_1_is_east = agent.getCenter().getX() > nearby_pickup_1.getCenter().getX() and \
                                                  (int(agent.getCenter().getY()) in range(
                                                      int(nearby_pickup_1.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                      int(nearby_pickup_1.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                  ))

                                num_choices = 0

                                if agent_1_is_north is True:
                                    num_choices += 1
                                if agent_1_is_south is True:
                                    num_choices += 1
                                if agent_1_is_east is True:
                                    num_choices += 1
                                if agent_1_is_west is True:
                                    num_choices += 1

                                if num_choices >= 2:
                                    if agent_1_is_north is True and nearby_pickup_1.north_open is True:
                                        agent_1_is_north = True
                                        agent_1_is_south = False
                                        agent_1_is_east = False
                                        agent_1_is_west = False

                                    elif agent_1_is_south is True and nearby_pickup_1.south_open is True:
                                        agent_1_is_north = False
                                        agent_1_is_south = True
                                        agent_1_is_east = False
                                        agent_1_is_west = False

                                    elif agent_1_is_east is True and nearby_pickup_1.east_open is True:
                                        agent_1_is_north = False
                                        agent_1_is_south = False
                                        agent_1_is_east = True
                                        agent_1_is_west = False

                                    elif agent_1_is_west is True and nearby_pickup_1.west_open is True:
                                        agent_1_is_north = False
                                        agent_1_is_south = False
                                        agent_1_is_east = False
                                        agent_1_is_west = True

                                    else:
                                        if nearby_pickup_1.north_open is True:
                                            agent_1_is_north = True
                                            agent_1_is_south = False
                                            agent_1_is_east = False
                                            agent_1_is_west = False
                                        elif nearby_pickup_1.south_open is True:
                                            agent_1_is_north = False
                                            agent_1_is_south = True
                                            agent_1_is_east = False
                                            agent_1_is_west = False
                                        elif nearby_pickup_1.east_open is True:
                                            agent_1_is_north = False
                                            agent_1_is_south = False
                                            agent_1_is_east = True
                                            agent_1_is_west = False
                                        elif nearby_pickup_1.west_open is True:
                                            agent_1_is_north = False
                                            agent_1_is_south = False
                                            agent_1_is_east = False
                                            agent_1_is_west = True

                                # The agent is to the north (above) of the second pickup.
                                if agent_1_is_north and nearby_pickup_1.north_open is True:
                                    agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT \
                                                 - (PICKUP_HEIGHT / 2)
                                    agent_1_y2 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
                                    relative_pos_1 = "N"
                                    relative_pos_found_1 = True

                                # The agent is to the south (below) of the second pickup.
                                elif agent_1_is_south and nearby_pickup_1.south_open is True:
                                    agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_1_y1 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
                                    agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT \
                                                 + (PICKUP_HEIGHT / 2)
                                    relative_pos_1 = "S"
                                    relative_pos_found_1 = True

                                # The agent is to the west (left) of the second pickup.
                                elif agent_1_is_west and nearby_pickup_1.west_open is True:
                                    agent_1_x1 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT \
                                                 - (PICKUP_HEIGHT / 2)
                                    agent_1_x2 = nearby_pickup_1.getCenter().getX() - PICKUP_HEIGHT / 2
                                    agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
                                    agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos_1 = "W"
                                    relative_pos_found_1 = True

                                # The agent is to the east (right) of the second pickup.
                                elif agent_1_is_east and nearby_pickup_1.east_open is True:
                                    agent_1_x1 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT / 2
                                    agent_1_x2 = nearby_pickup_1.getCenter().getX() + PICKUP_HEIGHT \
                                                 + (PICKUP_HEIGHT / 2)
                                    agent_1_y1 = nearby_pickup_1.getCenter().getY() - PICKUP_HEIGHT / 2
                                    agent_1_y2 = nearby_pickup_1.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos_1 = "E"
                                    relative_pos_found_1 = True

                                # The agent is neither north, south, east, nor west of the second pickup.
                                else:
                                    relative_pos_1 = "N/A"
                                    agent_1_x1, agent_1_y1, agent_1_x2, agent_1_y2 = -1, -1, -1, -1
                                    relative_pos_found_1 = False

                                # A movable should NOT be able to be placed outside the boundaries of the window.
                                if agent_1_x1 >= WIN_WIDTH or agent_1_x2 >= WIN_WIDTH or \
                                        agent_1_y1 >= WIN_HEIGHT or agent_1_y2 >= WIN_HEIGHT:
                                    if relative_pos_1 == "N":
                                        nearby_pickup_1.north_open = False
                                    elif relative_pos_1 == "S":
                                        nearby_pickup_1.south_open = False
                                    elif relative_pos_1 == "W":
                                        nearby_pickup_1.west_open = False
                                    elif relative_pos_1 == "E":
                                        nearby_pickup_1.east_open = False

                                    if (nearby_pickup_1.score - 1) == 0 and nearby_pickup_1.identity == "movable":
                                        nearby_pickup_1.score = 0
                                        nearby_pickup_1.setFill(color_rgb(128, 0, 128))  # Purple

                                    relative_pos_found_1 = False

                                if agent_1_x1 <= 0 or agent_1_x2 <= 0 or agent_1_y1 <= 0 or agent_1_y2 <= 0:
                                    if relative_pos_1 == "N":
                                        nearby_pickup_1.north_open = False
                                    elif relative_pos_1 == "S":
                                        nearby_pickup_1.south_open = False
                                    elif relative_pos_1 == "W":
                                        nearby_pickup_1.west_open = False
                                    elif relative_pos_1 == "E":
                                        nearby_pickup_1.east_open = False

                                    if (nearby_pickup_1.score - 1) == 0 and nearby_pickup_1.identity == "movable":
                                        nearby_pickup_1.score = 0
                                        nearby_pickup_1.setFill(color_rgb(128, 0, 128))  # Purple

                                    relative_pos_found_1 = False

                                # A movable should NOT be able to be placed on top of a "permanent" movable.
                                for pickup in pickups_list:
                                    if pickup.identity == "permanent":
                                        # First, we check in relation to the nearest (un)movable, "0".
                                        if relative_pos_0 == "N":
                                            if pickup.getCenter().getX() == agent_0_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_0_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_0 = False
                                                break
                                        elif relative_pos_0 == "S":
                                            if pickup.getCenter().getX() == agent_0_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_0_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_0 = False
                                                break
                                        elif relative_pos_0 == "W":
                                            if pickup.getCenter().getX() == agent_0_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_0_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_0 = False
                                                break
                                        elif relative_pos_0 == "E":
                                            if pickup.getCenter().getX() == agent_0_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_0_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_0 = False
                                                break

                                        # Second, we check in relation to the second nearest (un)movable, "1".
                                        if relative_pos_1 == "N":
                                            if pickup.getCenter().getX() == agent_1_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_1_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_1 = False
                                                break
                                        elif relative_pos_1 == "S":
                                            if pickup.getCenter().getX() == agent_1_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_1_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_1 = False
                                                break
                                        elif relative_pos_1 == "W":
                                            if pickup.getCenter().getX() == agent_1_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_1_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_1 = False
                                                break
                                        elif relative_pos_1 == "E":
                                            if pickup.getCenter().getX() == agent_1_x1 + (PICKUP_HEIGHT / 2) and \
                                                    pickup.getCenter().getY() == agent_1_y1 + (PICKUP_HEIGHT / 2):
                                                relative_pos_found_1 = False
                                                break
                            else:
                                relative_pos_0 = "N/A"
                                relative_pos_1 = "N/A"

                                relative_pos_found_0 = False
                                relative_pos_found_1 = False

                                agent_0_x1, agent_0_y1, agent_0_x2, agent_0_y2 = -1, -1, -1, -1
                                agent_1_x1, agent_1_y1, agent_1_x2, agent_1_y2 = -1, -1, -1, -1

                            # =---= Step 5: =---= #
                            # Can the agent set down its movable?
                            # Are both of the newly-calculated points the same?
                            points_match = (agent_0_x1 == agent_1_x1) and (agent_0_y1 == agent_1_y1) and \
                                           (agent_0_x2 == agent_1_x2) and (agent_0_y2 == agent_1_y2)

                            # =---= Step 5.5: =---= #
                            # Can the movable actually be placed in the desired location?
                            if relative_pos_found_0 is True and relative_pos_found_1 is True and points_match is True:
                                no_overlap = True

                                for pickup in pickups_list:
                                    pickup_x1 = pickup.getCenter().getX() - PICKUP_HEIGHT / 2
                                    pickup_y1 = pickup.getCenter().getY() - PICKUP_HEIGHT / 2
                                    pickup_x2 = pickup.getCenter().getX() + PICKUP_HEIGHT / 2
                                    pickup_y2 = pickup.getCenter().getY() + PICKUP_HEIGHT / 2

                                    if (pickup_x1 == agent_0_x1) and (pickup_y1 == agent_0_y1) and \
                                            (pickup_x2 == agent_0_x2) and (pickup_y2 == agent_0_y2):
                                        no_overlap = False
                            else:
                                no_overlap = False

                            if no_overlap is True:
                                # The relative_pos direction and corresponding "open" status must match.
                                can_set_north_0 = nearby_north_status_0 is True and relative_pos_0 == "N"
                                can_set_south_0 = nearby_south_status_0 is True and relative_pos_0 == "S"
                                can_set_east_0 = nearby_east_status_0 is True and relative_pos_0 == "E"
                                can_set_west_0 = nearby_west_status_0 is True and relative_pos_0 == "W"
                                able_to_set_0 = can_set_north_0 or can_set_south_0 or can_set_east_0 or can_set_west_0

                                can_set_north_1 = nearby_north_status_1 is True and relative_pos_1 == "N"
                                can_set_south_1 = nearby_south_status_1 is True and relative_pos_1 == "S"
                                can_set_east_1 = nearby_east_status_1 is True and relative_pos_1 == "E"
                                can_set_west_1 = nearby_west_status_1 is True and relative_pos_1 == "W"
                                able_to_set_1 = can_set_north_1 or can_set_south_1 or can_set_east_1 or can_set_west_1

                                if able_to_set_0 is True and able_to_set_1 is True:
                                    moved_pickup = MovablePickup(Point(agent_0_x1, agent_0_y1),
                                                                 Point(agent_0_x2, agent_0_y2))
                                    moved_pickup.setFill(color_rgb(255, 255, 0))  # Yellow
                                    moved_pickup.setOutline(color_rgb(0, 0, 0))  # Black

                                    # Smart detection if the new movable is placed right on the edge of the screen.
                                    # Used to help avoid clustering cases on the edges of the screen.
                                    if moved_pickup.getCenter().getX() + PICKUP_HEIGHT >= WIN_WIDTH:
                                        moved_pickup.east_open = False
                                    if moved_pickup.getCenter().getX() - PICKUP_HEIGHT <= 0:
                                        moved_pickup.west_open = False
                                    if moved_pickup.getCenter().getY() + PICKUP_HEIGHT >= WIN_HEIGHT:
                                        moved_pickup.south_open = False
                                    if moved_pickup.getCenter().getY() - PICKUP_HEIGHT <= 0:
                                        moved_pickup.north_open = False

                                    # The nearest pickup was a movable.
                                    if nearby_one_identity == "movable":
                                        # We need to update the new movable's appropriate status and score.
                                        if can_set_north_0 is True:
                                            moved_pickup.south_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_south_0 is True:
                                            moved_pickup.north_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_east_0 is True:
                                            moved_pickup.west_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_west_0 is True:
                                            moved_pickup.east_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        else:
                                            print(f"Loop was entered although able_to_set_0 was {able_to_set_0} "
                                                  f"and able_to_set_1 was {able_to_set_1}.")
                                            print("Impossible case; exiting the program. [7]")
                                            exit(1)

                                    # The nearest pickup was an unmovable.
                                    elif nearby_one_identity == "unmovable":
                                        # We need to update the new movable's appropriate status and score.
                                        if can_set_north_0 is True:
                                            moved_pickup.south_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_south_0 is True:
                                            moved_pickup.north_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_east_0 is True:
                                            moved_pickup.west_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        elif can_set_west_0 is True:
                                            moved_pickup.east_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = pickups_list[nearby_pickup_indices[0]].line_id
                                            moved_pickup.on_path_id = pickups_list[nearby_pickup_indices[0]].on_path_id
                                            moved_pickup.on_path_counter = \
                                                pickups_list[nearby_pickup_indices[0]].on_path_counter + 1
                                        else:
                                            print(f"Loop was entered although able_to_set_0 was {able_to_set_0} "
                                                  f"and able_to_set_1 was {able_to_set_1}.")
                                            print("Impossible case; exiting the program. [8]")
                                            exit(1)

                                    else:
                                        print(
                                            f"The nearby pickup's identity was invalid; it was {nearby_one_identity}.")
                                        print("Impossible case; exiting the program. [9]")
                                        exit(1)

                                    # moved_pickup.draw(agents_window)  # [D]
                                    pickups_list.append(moved_pickup)
                                    pickup_was_placed = True
                                    placed_pickups_list.append(moved_pickup)

                                    agent.setFill(color_rgb(255, 0, 0))  # Red
                                    agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                                    agent.is_holding = False
                                    agent.just_picked_up = True
                                    agent.held_pickup_identity = ""

                                    # =---= Step 6: =---= #
                                    # Update the status and score of the nearest (un)movable.
                                    if nearby_one_identity == "movable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if can_set_north_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].north_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                            pickups_list[nearby_pickup_indices[0]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[0]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_south_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].south_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                            pickups_list[nearby_pickup_indices[0]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[0]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_east_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].east_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                            pickups_list[nearby_pickup_indices[0]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[0]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_west_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].west_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                            pickups_list[nearby_pickup_indices[0]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[0]].setFill(color_rgb(128, 0, 128))
                                        else:
                                            print(f"Loop was entered although able_to_set_0 was {able_to_set_0}.")
                                            print("Impossible case; exiting the program. [10]")
                                            exit(1)

                                    elif nearby_one_identity == "unmovable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if can_set_north_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].north_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                        elif can_set_south_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].south_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                        elif can_set_east_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].east_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                        elif can_set_west_0 is True:
                                            pickups_list[nearby_pickup_indices[0]].west_open = False
                                            pickups_list[nearby_pickup_indices[0]].score += 1
                                        else:
                                            print(f"Loop was entered although able_to_set_0 was {able_to_set_0}.")
                                            print("Impossible case; exiting the program. [11]")
                                            exit(1)

                                    else:
                                        print(
                                            f"The nearby pickup's identity was invalid; it was {nearby_one_identity}.")
                                        print("Impossible case; exiting the program. [12]")
                                        exit(1)

                                    if nearby_two_identity == "movable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if can_set_north_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].north_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                            pickups_list[nearby_pickup_indices[1]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[1]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_south_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].south_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                            pickups_list[nearby_pickup_indices[1]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[1]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_east_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].east_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                            pickups_list[nearby_pickup_indices[1]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[1]].setFill(color_rgb(128, 0, 128))
                                        elif can_set_west_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].west_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                            pickups_list[nearby_pickup_indices[1]].line_id = moved_pickup.line_id
                                            # Purple
                                            pickups_list[nearby_pickup_indices[1]].setFill(color_rgb(128, 0, 128))
                                        else:
                                            print(f"Loop was entered although able_to_set_1 was {able_to_set_1}.")
                                            print("Impossible case; exiting the program. [13]")
                                            exit(1)

                                    elif nearby_two_identity == "unmovable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if can_set_north_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].north_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                        elif can_set_south_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].south_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                        elif can_set_east_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].east_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                        elif can_set_west_1 is True:
                                            pickups_list[nearby_pickup_indices[1]].west_open = False
                                            pickups_list[nearby_pickup_indices[1]].score += 1
                                        else:
                                            print(f"Loop was entered although able_to_set_1 was {able_to_set_1}.")
                                            print("Impossible case; exiting the program. [14]")
                                            exit(1)

                                    else:
                                        print(
                                            f"The nearby pickup's identity was invalid; it was {nearby_two_identity}.")
                                        print("Impossible case; exiting the program. [15]")
                                        exit(1)
                            else:
                                case_number = 1

                        # ~~~~~ Case 1: ~~~~~ #

                        if case_number == 1:
                            # =---= Step 2: =---= #
                            # Check the nearby unmovable's score; it must be between -4 and -1 in order to proceed.
                            # Check the nearby movable's score; it must be -1 in order to proceed.
                            # Otherwise, do not proceed.

                            nearby_one_identity = pickups_list[nearby_pickup_indices[0]].identity
                            nearby_one_score = pickups_list[nearby_pickup_indices[0]].score

                            if nearby_one_identity == "unmovable" and nearby_one_score in range(-4, 0):
                                valid_score = True
                            elif nearby_one_identity == "movable" and nearby_one_score == -1:
                                valid_score = True
                            elif nearby_one_identity == "permanent" or nearby_one_identity == "gone":
                                valid_score = False
                            else:
                                valid_score = False

                            # =---= Step 3: =---= #
                            # Set the "open" statuses for the nearest (un)movable.

                            if valid_score is True:
                                nearby_north_status = pickups_list[nearby_pickup_indices[0]].north_open
                                nearby_south_status = pickups_list[nearby_pickup_indices[0]].south_open
                                nearby_east_status = pickups_list[nearby_pickup_indices[0]].east_open
                                nearby_west_status = pickups_list[nearby_pickup_indices[0]].west_open
                                all_statuses_set = True
                            else:
                                nearby_north_status = False
                                nearby_south_status = False
                                nearby_east_status = False
                                nearby_west_status = False
                                all_statuses_set = False

                            # =---= Step 4: =---= #
                            # Find the agent's position relative to the nearest (un)movable.
                            nearby_pickup = pickups_list[nearby_pickup_indices[0]]

                            if all_statuses_set is True:
                                agent_is_north = agent.getCenter().getY() < nearby_pickup.getCenter().getY() and \
                                                 (int(agent.getCenter().getX()) in range(
                                                     int(nearby_pickup.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                     int(nearby_pickup.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                 ))

                                agent_is_south = agent.getCenter().getY() > nearby_pickup.getCenter().getY() and \
                                                 (int(agent.getCenter().getX()) in range(
                                                     int(nearby_pickup.getCenter().getX() - (PICKUP_HEIGHT / 2)),
                                                     int(nearby_pickup.getCenter().getX() + (PICKUP_HEIGHT / 2) + 1)
                                                 ))

                                agent_is_west = agent.getCenter().getX() < nearby_pickup.getCenter().getX() and \
                                                (int(agent.getCenter().getY()) in range(
                                                     int(nearby_pickup.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                     int(nearby_pickup.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                 ))

                                agent_is_east = agent.getCenter().getX() > nearby_pickup.getCenter().getX() and \
                                                (int(agent.getCenter().getY()) in range(
                                                     int(nearby_pickup.getCenter().getY() - (PICKUP_HEIGHT / 2)),
                                                     int(nearby_pickup.getCenter().getY() + (PICKUP_HEIGHT / 2) + 1)
                                                 ))

                                num_choices = 0

                                if agent_is_north is True:
                                    num_choices += 1
                                if agent_is_south is True:
                                    num_choices += 1
                                if agent_is_east is True:
                                    num_choices += 1
                                if agent_is_west is True:
                                    num_choices += 1

                                if num_choices >= 2:
                                    if agent_is_north is True and nearby_pickup.north_open is True:
                                        agent_is_north = True
                                        agent_is_south = False
                                        agent_is_east = False
                                        agent_is_west = False

                                    elif agent_is_south is True and nearby_pickup.south_open is True:
                                        agent_is_north = False
                                        agent_is_south = True
                                        agent_is_east = False
                                        agent_is_west = False

                                    elif agent_is_east is True and nearby_pickup.east_open is True:
                                        agent_is_north = False
                                        agent_is_south = False
                                        agent_is_east = True
                                        agent_is_west = False

                                    elif agent_is_west is True and nearby_pickup.west_open is True:
                                        agent_is_north = False
                                        agent_is_south = False
                                        agent_is_east = False
                                        agent_is_west = True

                                # The agent is to the north (above) of the pickup.
                                if agent_is_north and nearby_pickup.north_open is True:
                                    new_x1 = nearby_pickup.getCenter().getX() - PICKUP_HEIGHT / 2
                                    new_x2 = nearby_pickup.getCenter().getX() + PICKUP_HEIGHT / 2
                                    new_y1 = nearby_pickup.getCenter().getY() - PICKUP_HEIGHT - (PICKUP_HEIGHT / 2)
                                    new_y2 = nearby_pickup.getCenter().getY() - PICKUP_HEIGHT / 2
                                    relative_pos = "N"
                                    relative_pos_found = True

                                # The agent is to the south (below) of the pickup.
                                elif agent_is_south and nearby_pickup.south_open is True:
                                    new_x1 = nearby_pickup.getCenter().getX() - PICKUP_HEIGHT / 2
                                    new_x2 = nearby_pickup.getCenter().getX() + PICKUP_HEIGHT / 2
                                    new_y1 = nearby_pickup.getCenter().getY() + PICKUP_HEIGHT / 2
                                    new_y2 = nearby_pickup.getCenter().getY() + PICKUP_HEIGHT + (PICKUP_HEIGHT / 2)
                                    relative_pos = "S"
                                    relative_pos_found = True

                                # The agent is to the west (left) of the pickup.
                                elif agent_is_west and pickups_list[nearby_pickup_indices[0]].west_open is True:
                                    new_x1 = nearby_pickup.getCenter().getX() - PICKUP_HEIGHT - (PICKUP_HEIGHT / 2)
                                    new_x2 = nearby_pickup.getCenter().getX() - PICKUP_HEIGHT / 2
                                    new_y1 = nearby_pickup.getCenter().getY() - PICKUP_HEIGHT / 2
                                    new_y2 = nearby_pickup.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos = "W"
                                    relative_pos_found = True

                                # The agent is to the east (right) of the pickup.
                                elif agent_is_east and pickups_list[nearby_pickup_indices[0]].east_open is True:
                                    new_x1 = nearby_pickup.getCenter().getX() + PICKUP_HEIGHT / 2
                                    new_x2 = nearby_pickup.getCenter().getX() + PICKUP_HEIGHT + (PICKUP_HEIGHT / 2)
                                    new_y1 = nearby_pickup.getCenter().getY() - PICKUP_HEIGHT / 2
                                    new_y2 = nearby_pickup.getCenter().getY() + PICKUP_HEIGHT / 2
                                    relative_pos = "E"
                                    relative_pos_found = True

                                # The agent is neither north, south, east, nor west of the pickup.
                                else:
                                    relative_pos = "N/A"
                                    new_x1, new_y1, new_x2, new_y2 = -1, -1, -1, -1
                                    relative_pos_found = False
                            else:
                                relative_pos = "N/A"
                                new_x1, new_y1, new_x2, new_y2 = -1, -1, -1, -1

                            # A movable should NOT be able to be placed on top of a "permanent" movable.
                            for pickup in pickups_list:
                                if pickup.identity == "permanent":
                                    if relative_pos == "N":
                                        if pickup.getCenter().getX() == new_x1 + (PICKUP_HEIGHT / 2) and \
                                                pickup.getCenter().getY() == new_y1 + (PICKUP_HEIGHT / 2):
                                            relative_pos_found = False
                                            break
                                    elif relative_pos == "S":
                                        if pickup.getCenter().getX() == new_x1 + (PICKUP_HEIGHT / 2) and \
                                                pickup.getCenter().getY() == new_y1 + (PICKUP_HEIGHT / 2):
                                            relative_pos_found = False
                                            break
                                    elif relative_pos == "W":
                                        if pickup.getCenter().getX() == new_x1 + (PICKUP_HEIGHT / 2) and \
                                                pickup.getCenter().getY() == new_y1 + (PICKUP_HEIGHT / 2):
                                            relative_pos_found = False
                                            break
                                    elif relative_pos == "E":
                                        if pickup.getCenter().getX() == new_x1 + (PICKUP_HEIGHT / 2) and \
                                                pickup.getCenter().getY() == new_y1 + (PICKUP_HEIGHT / 2):
                                            relative_pos_found = False
                                            break

                            # A movable should NOT be able to be placed outside the boundaries of the window.
                            if new_x1 >= WIN_WIDTH or new_x2 >= WIN_WIDTH or \
                                    new_y1 >= WIN_HEIGHT or new_y2 >= WIN_HEIGHT:
                                if relative_pos == "N":
                                    nearby_pickup.north_open = False
                                elif relative_pos == "S":
                                    nearby_pickup.south_open = False
                                elif relative_pos == "W":
                                    nearby_pickup.west_open = False
                                elif relative_pos == "E":
                                    nearby_pickup.east_open = False

                                relative_pos_found = False

                            if new_x1 <= 0 or new_x2 <= 0 or new_y1 <= 0 or new_y2 <= 0:
                                if relative_pos == "N":
                                    nearby_pickup.north_open = False
                                elif relative_pos == "S":
                                    nearby_pickup.south_open = False
                                elif relative_pos == "W":
                                    nearby_pickup.west_open = False
                                elif relative_pos == "E":
                                    nearby_pickup.east_open = False

                                relative_pos_found = False

                            # =---= Step 5: =---= #
                            # Can the movable actually be placed in the desired location?
                            if relative_pos_found is True:
                                no_overlap = True

                                for pickup in pickups_list:
                                    pickup_x1 = pickup.getCenter().getX() - PICKUP_HEIGHT / 2
                                    pickup_y1 = pickup.getCenter().getY() - PICKUP_HEIGHT / 2
                                    pickup_x2 = pickup.getCenter().getX() + PICKUP_HEIGHT / 2
                                    pickup_y2 = pickup.getCenter().getY() + PICKUP_HEIGHT / 2

                                    if (pickup_x1 == new_x1) and (pickup_y1 == new_y1) and \
                                            (pickup_x2 == new_x2) and (pickup_y2 == new_y2):
                                        no_overlap = False
                            else:
                                no_overlap = False

                            # =---= Step 5.5: =---= #
                            # Can the agent set down its movable?
                            # The relative_pos direction and corresponding "open" status must match.
                            if no_overlap is True:
                                able_to_set_north = nearby_north_status is True and relative_pos == "N"
                                able_to_set_south = nearby_south_status is True and relative_pos == "S"
                                able_to_set_east = nearby_east_status is True and relative_pos == "E"
                                able_to_set_west = nearby_west_status is True and relative_pos == "W"
                                able_to_set = able_to_set_north or able_to_set_south or \
                                              able_to_set_east or able_to_set_west

                                if STOP_MOTION_PLACEMENTS is True:
                                    agent.setFill(color_rgb(0, 0, 100))  # Dark Blue
                                    if nearby_pickup.identity == "movable":
                                        nearby_pickup.setFill(color_rgb(0, 0, 100))  # Dark Blue
                                    # Commented out for data collection purposes.
                                    # agents_window.getMouse()

                                if able_to_set:
                                    moved_pickup = MovablePickup(Point(new_x1, new_y1), Point(new_x2, new_y2))
                                    moved_pickup.setFill(color_rgb(255, 255, 0))  # Yellow
                                    moved_pickup.setOutline(color_rgb(0, 0, 0))  # Black

                                    # Smart detection if the new movable is placed right on the edge of the screen.
                                    # Used to help avoid clustering cases on the edges of the screen.
                                    if moved_pickup.getCenter().getX() + PICKUP_HEIGHT >= WIN_WIDTH:
                                        moved_pickup.east_open = False
                                    if moved_pickup.getCenter().getX() - PICKUP_HEIGHT <= 0:
                                        moved_pickup.west_open = False
                                    if moved_pickup.getCenter().getY() + PICKUP_HEIGHT >= WIN_HEIGHT:
                                        moved_pickup.south_open = False
                                    if moved_pickup.getCenter().getY() - PICKUP_HEIGHT <= 0:
                                        moved_pickup.north_open = False

                                    # The nearest pickup was a movable.
                                    if nearby_one_identity == "movable":
                                        # We need to update the new movable's appropriate status and score.
                                        if able_to_set_north is True:
                                            moved_pickup.south_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = nearby_pickup.on_path_id
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_south is True:
                                            moved_pickup.north_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = nearby_pickup.on_path_id
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_east is True:
                                            moved_pickup.west_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = nearby_pickup.on_path_id
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_west is True:
                                            moved_pickup.east_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = nearby_pickup.on_path_id
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        else:
                                            print(f"Loop was entered although able_to_set was {able_to_set}.")
                                            print("Impossible case; exiting the program. [1]")
                                            exit(1)

                                    # The nearest pickup was an unmovable.
                                    elif nearby_one_identity == "unmovable":
                                        # We need to update the new movable's appropriate status and score.
                                        if able_to_set_north is True:
                                            moved_pickup.south_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = "N"
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_south is True:
                                            moved_pickup.north_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = "S"
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_east is True:
                                            moved_pickup.west_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = "E"
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        elif able_to_set_west is True:
                                            moved_pickup.east_open = False
                                            moved_pickup.score += 1
                                            moved_pickup.line_id = nearby_pickup.line_id
                                            moved_pickup.on_path_id = "W"
                                            moved_pickup.on_path_counter = nearby_pickup.on_path_counter + 1
                                        else:
                                            print(f"Loop was entered although able_to_set was {able_to_set}.")
                                            print("Impossible case; exiting the program. [2]")
                                            exit(1)

                                    else:
                                        print(
                                            f"The nearby pickup's identity was invalid; it was {nearby_one_identity}.")
                                        print("Impossible case; exiting the program. [3]")
                                        exit(1)

                                    # moved_pickup.draw(agents_window)  # [D]
                                    pickups_list.append(moved_pickup)
                                    pickup_was_placed = True
                                    placed_pickups_list.append(moved_pickup)

                                    agent.setFill(color_rgb(255, 0, 0))  # Red
                                    agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                                    agent.is_holding = False
                                    agent.just_picked_up = True
                                    agent.held_pickup_identity = ""

                                    # =---= Step 6: =---= #
                                    nearby_pickup = pickups_list[nearby_pickup_indices[0]]

                                    # Update the status and score of the nearest (un)movable.
                                    if nearby_one_identity == "movable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if able_to_set_north is True:
                                            nearby_pickup.north_open = False
                                            nearby_pickup.score += 1
                                            nearby_pickup.setFill(color_rgb(128, 0, 128))  # Purple
                                        elif able_to_set_south is True:
                                            nearby_pickup.south_open = False
                                            nearby_pickup.score += 1
                                            nearby_pickup.setFill(color_rgb(128, 0, 128))  # Purple
                                        elif able_to_set_east is True:
                                            nearby_pickup.east_open = False
                                            nearby_pickup.score += 1
                                            nearby_pickup.setFill(color_rgb(128, 0, 128))  # Purple
                                        elif able_to_set_west is True:
                                            nearby_pickup.west_open = False
                                            nearby_pickup.score += 1
                                            nearby_pickup.setFill(color_rgb(128, 0, 128))  # Purple
                                        else:
                                            print(f"Loop was entered although able_to_set was {able_to_set}.")
                                            print("Impossible case; exiting the program. [4]")
                                            exit(1)

                                    elif nearby_one_identity == "unmovable":
                                        # We need to update the nearby movable's appropriate status and score.
                                        if able_to_set_north is True:
                                            nearby_pickup.north_open = False
                                            nearby_pickup.score += 1
                                        elif able_to_set_south is True:
                                            nearby_pickup.south_open = False
                                            nearby_pickup.score += 1
                                        elif able_to_set_east is True:
                                            nearby_pickup.east_open = False
                                            nearby_pickup.score += 1
                                        elif able_to_set_west is True:
                                            nearby_pickup.west_open = False
                                            nearby_pickup.score += 1
                                        else:
                                            print(f"Loop was entered although able_to_set was {able_to_set}.")
                                            print("Impossible case; exiting the program. [5]")
                                            exit(1)

                                    else:
                                        print(
                                            f"The nearby pickup's identity was invalid; it was {nearby_one_identity}.")
                                        print("Impossible case; exiting the program. [6]")
                                        exit(1)

                        if pickup_was_placed is True:
                            for placed_pickup in placed_pickups_list:
                                moved_pickup_north = Point(placed_pickup.getCenter().getX(),
                                                           placed_pickup.getCenter().getY() - PICKUP_HEIGHT)
                                moved_pickup_south = Point(placed_pickup.getCenter().getX(),
                                                           placed_pickup.getCenter().getY() + PICKUP_HEIGHT)
                                moved_pickup_east = Point(placed_pickup.getCenter().getX() + PICKUP_HEIGHT,
                                                          placed_pickup.getCenter().getY())
                                moved_pickup_west = Point(placed_pickup.getCenter().getX() - PICKUP_HEIGHT,
                                                          placed_pickup.getCenter().getY())

                                total_number_true = 0
                                pickup_counter = 0

                                list_of_line_ids = []
                                list_of_indices = []
                                list_of_directions = []

                                for pickup in pickups_list:
                                    if (pickup.identity == "movable" and pickup.score in range(-1, 1)) or \
                                            (pickup.identity == "unmovable" and pickup.score in range(-4, 0)):
                                        if pickup.getCenter().getX() == moved_pickup_north.getX() and \
                                                pickup.getCenter().getY() == moved_pickup_north.getY():
                                            total_number_true += 1
                                            list_of_line_ids.append(pickup.line_id)
                                            list_of_indices.append(pickup_counter)
                                            list_of_directions.append("N")

                                        elif pickup.getCenter().getX() == moved_pickup_south.getX() and \
                                                pickup.getCenter().getY() == moved_pickup_south.getY():
                                            total_number_true += 1
                                            list_of_line_ids.append(pickup.line_id)
                                            list_of_indices.append(pickup_counter)
                                            list_of_directions.append("S")

                                        elif pickup.getCenter().getX() == moved_pickup_east.getX() and \
                                                pickup.getCenter().getY() == moved_pickup_east.getY():
                                            total_number_true += 1
                                            list_of_line_ids.append(pickup.line_id)
                                            list_of_indices.append(pickup_counter)
                                            list_of_directions.append("E")

                                        elif pickup.getCenter().getX() == moved_pickup_west.getX() and \
                                                pickup.getCenter().getY() == moved_pickup_west.getY():
                                            total_number_true += 1
                                            list_of_line_ids.append(pickup.line_id)
                                            list_of_indices.append(pickup_counter)
                                            list_of_directions.append("W")

                                    pickup_counter += 1

                                if total_number_true >= 2:
                                    # If list_of_line_ids does NOT have all identical elements...
                                    if len(set(list_of_line_ids)) != 1:
                                        nearby_pickup_0 = pickups_list[list_of_indices[0]]
                                        nearby_pickup_1 = pickups_list[list_of_indices[1]]

                                        for index in list_of_indices:
                                            if pickups_list[index].identity == "unmovable":
                                                nearby_pickup_0 = pickups_list[index]

                                        if nearby_pickup_0.line_id != nearby_pickup_1.line_id and \
                                                total_number_true == 3:
                                            nearby_pickup_1 = pickups_list[list_of_indices[2]]

                                        placed_pickup.on_path_id = "CONNECTED"
                                        placed_pickup.line_id = nearby_pickup_0.line_id

                                        agent.setFill(color_rgb(255, 0, 0))  # Red
                                        agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                                        agent.is_holding = False
                                        agent.just_picked_up = True
                                        agent.held_pickup_identity = ""

                                        # Step 6: Identify all the movables that were used/not used in the correct path.
                                        # Then, only free movables that have the same path_id's as the ones on the path.
                                        num_remaining_pickups = 0

                                        # Note: We do NOT want to remove any unmovables from the window.
                                        for pickup in pickups_list:
                                            if (pickup.line_id == nearby_pickup_0.line_id or
                                                pickup.line_id == nearby_pickup_1.line_id) and \
                                                    pickup.identity == "movable":
                                                if pickup.score != -2 and pickup.line_id == nearby_pickup_0.line_id \
                                                        and pickup.on_path_id == nearby_pickup_0.on_path_id and \
                                                        pickup.on_path_counter <= nearby_pickup_0.on_path_counter:
                                                    pickup.setFill(color_rgb(0, 255, 255))  # Light Blue
                                                    pickup.on_correct_path = True

                                                    pickup.identity = "permanent"
                                                    pickup.north_open = False
                                                    pickup.south_open = False
                                                    pickup.west_open = False
                                                    pickup.east_open = False

                                                elif pickup.score != -2 and pickup.line_id == nearby_pickup_1.line_id \
                                                        and pickup.on_path_id == nearby_pickup_1.on_path_id \
                                                        and pickup.on_path_counter <= nearby_pickup_1.on_path_counter:
                                                    pickup.setFill(color_rgb(0, 255, 255))  # Light Blue
                                                    pickup.on_correct_path = True

                                                    pickup.identity = "permanent"
                                                    pickup.north_open = False
                                                    pickup.south_open = False
                                                    pickup.west_open = False
                                                    pickup.east_open = False

                                                elif pickup.on_path_id == "CONNECTED":
                                                    pickup.setFill(color_rgb(0, 0, 100))  # Dark Blue
                                                    pickup.on_correct_path = True

                                                    pickup.identity = "permanent"
                                                    pickup.north_open = False
                                                    pickup.south_open = False
                                                    pickup.west_open = False
                                                    pickup.east_open = False

                                                elif pickup.on_path_id == nearby_pickup_0.on_path_id and \
                                                        pickup.on_path_counter > nearby_pickup_0.on_path_counter and \
                                                        pickup.line_id == nearby_pickup_0.line_id:
                                                    num_remaining_pickups += 1

                                                    pickup.identity = "gone"
                                                    pickup.undraw()

                                                elif pickup.on_path_id == nearby_pickup_1.on_path_id and \
                                                        pickup.on_path_counter > nearby_pickup_1.on_path_counter and \
                                                        pickup.line_id == nearby_pickup_1.line_id:
                                                    num_remaining_pickups += 1

                                                    pickup.identity = "gone"
                                                    pickup.undraw()

                                        # Commented out for data collection purposes.
                                        # agents_window.getMouse()

                                        # Step 7: Update the agents & randomize the locations of the remaining movables.
                                        for maybe_holding_agent in agents_list:
                                            if maybe_holding_agent.is_holding is True:
                                                maybe_holding_agent.setFill(color_rgb(255, 0, 0))  # Red
                                                maybe_holding_agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                                                maybe_holding_agent.pick_up_cooldown = 0
                                                maybe_holding_agent.is_holding = False
                                                maybe_holding_agent.just_picked_up = False
                                                maybe_holding_agent.held_pickup_identity = ""

                                                num_remaining_pickups += 1

                                        if len(pickups_list) + num_remaining_pickups > TOTAL_NUM_OF_PICKUPS:
                                            difference = (len(pickups_list) + num_remaining_pickups) - \
                                                         TOTAL_NUM_OF_PICKUPS
                                            num_remaining_pickups -= difference

                                        PLACED_PICKUP_POINTS = []

                                        while num_remaining_pickups != 0:
                                            center = get_random_point(x_low, x_high, y_low, y_high)
                                            pickup_to_add = MovablePickup(Point(center.getX() - PICKUP_HEIGHT / 2,
                                                                                center.getY() - PICKUP_HEIGHT / 2),
                                                                          Point(center.getX() + PICKUP_HEIGHT / 2,
                                                                                center.getY() + PICKUP_HEIGHT / 2))

                                            # pickup_to_add.draw(agents_window)  # [D]
                                            pickups_list.append(pickup_to_add)
                                            PLACED_PICKUP_POINTS.append(pickup_to_add.getCenter())

                                            num_remaining_pickups -= 1

                                        num_successful_paths += 1
                                        num_iterations_per_path.append(NUM_OF_ITERATIONS + 1)

                                        # Commented out for data collection purposes.
                                        # agents_window.getMouse()

            # The agent is NOT holding a movable.
            elif agent.is_holding is False and agent.just_picked_up is False:
                new_agent_dx = agent.dx
                new_agent_dy = agent.dy

                # There is a 1/100 chance that the agent's movement will be randomized.
                randomize_movement = random.randrange(0, 100)
                if randomize_movement == 0:
                    new_agent_dx = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)
                    new_agent_dy = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY + 1)

                    if new_agent_dx == 0:
                        randomize_sign = random.randrange(0, 2)
                        if randomize_sign == 0:
                            new_agent_dx = AGENT_VELOCITY / 2
                        else:
                            new_agent_dx = -AGENT_VELOCITY / 2

                    if new_agent_dy == 0:
                        randomize_sign = random.randrange(0, 2)
                        if randomize_sign == 0:
                            new_agent_dy = AGENT_VELOCITY / 2
                        else:
                            new_agent_dy = -AGENT_VELOCITY / 2

                # ATTRACT cases if the agent is NOT HOLDING a movable:
                # Any movable with a score of -2.
                for pickup in pickups_list:
                    if pickup.identity == "movable" and pickup.score == -2:
                        distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                           ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                        if ATTRACTION_EXCLUSION_ZONE_SQUARED <= distance_squared <= ATTRACTION_RANGE_SQUARED:
                            attract_force_x = 1 - (FORCE_FACTOR * math.sqrt(distance_squared))
                            attract_force_y = 1 - (FORCE_FACTOR * math.sqrt(distance_squared))

                            # Calculates the component of the force in each direction.
                            attract_force_x = attract_force_x * \
                                              (math.fabs(agent.getCenter().getX() - pickup.getCenter().getX())
                                               / math.sqrt(distance_squared))
                            attract_force_y = attract_force_y * \
                                              (math.fabs(agent.getCenter().getY() - pickup.getCenter().getY())
                                               / math.sqrt(distance_squared))

                            if agent.getCenter().getX() > pickup.getCenter().getX():
                                attract_force_x = -attract_force_x
                            if agent.getCenter().getY() > pickup.getCenter().getY():
                                attract_force_y = -attract_force_y

                            new_agent_dx += attract_force_x
                            new_agent_dy += attract_force_y

                # If the agent is moving too slow (with a positive x velocity), it needs a boost...
                if 0 < new_agent_dx < 1:
                    new_agent_dx += 1

                # If the agent is moving too slow (with a negative x velocity), it needs a boost...
                if -1 > new_agent_dx > 0:
                    new_agent_dx -= 1

                # If the agent is moving too slow (with a positive y velocity), it needs a boost...
                if 0 < new_agent_dy < 1:
                    new_agent_dy += 1

                # If the agent is moving too slow (with a negative y velocity), it needs a boost...
                if -1 > new_agent_dy > 0:
                    new_agent_dy -= 1

                # If the agent hits the left side of the screen...
                if agent.getCenter().getX() < x_low:
                    if new_agent_dx < 0:
                        new_agent_dx = -new_agent_dx

                # If the agent hits the right side of the screen...
                if agent.getCenter().getX() > x_high:
                    if new_agent_dx > 0:
                        new_agent_dx = -new_agent_dx

                # If the agent hits the top of the screen...
                if agent.getCenter().getY() < y_low:
                    if new_agent_dy < 0:
                        new_agent_dy = -new_agent_dy

                # If the agent hits the bottom of the screen...
                if agent.getCenter().getY() > y_high:
                    if new_agent_dy > 0:
                        new_agent_dy = -new_agent_dy

                # Ensuring that the final velocities will not exceed a certain threshold...
                if new_agent_dx > AGENT_VELOCITY:
                    new_agent_dx = AGENT_VELOCITY
                if new_agent_dx < -AGENT_VELOCITY:
                    new_agent_dx = -AGENT_VELOCITY
                if new_agent_dy > AGENT_VELOCITY:
                    new_agent_dy = AGENT_VELOCITY
                if new_agent_dy < -AGENT_VELOCITY:
                    new_agent_dy = -AGENT_VELOCITY

                agent.dx = new_agent_dx
                agent.dy = new_agent_dy

                agent.move(agent.dx, agent.dy)

            # Reduces an agent's cooldown to set down another pickup, if applicable.
            if agent.set_down_cooldown > 0:
                agent.set_down_cooldown -= 1

            # Detects if an agent is able to grab a pickup.
            elif agent.is_holding is False and agent.set_down_cooldown == 0:
                index = 0

                for pickup in pickups_list:
                    distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                       ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                    # Agents should only be able to pick up movables with a score of -2.
                    if pickup.identity == "movable" and pickup.score == -2:
                        # The extra check to ensure the agent is not holding any pickups is necessary to
                        # ensure the agent doesn't grab two pickups at the same time.
                        if distance_squared <= ((agent.radius + (PICKUP_HEIGHT / 2)) ** 2) and \
                                agent.is_holding is False:

                            if pickup not in GRABBED_OBJECT_LIST:
                                GRABBED_OBJECT_LIST.append(pickup)

                                if pickup.identity == "movable":
                                    pickup.score = -2
                                    pickup.north_open = True
                                    pickup.south_open = True
                                    pickup.east_open = True
                                    pickup.west_open = True
                                else:
                                    print("Pickup has an invalid identity when picked up; Impossible case. [16]")
                                    print(f"pickup.identity = {pickup.identity}")
                                    exit(1)

                                agent.setFill(color_rgb(0, 255, 0))  # Green
                                agent.is_holding = True
                                agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                                agent.held_pickup_identity = pickup.identity

                                pickups_list.remove(pickup)
                                pickup.undraw()

                    index += 1

        # One iteration/cycle of the program has occurred, so update the counter.
        update_num_of_iterations()

        # We need to update the list that contains the points of all the placed pickups.
        num_pickups_remaining = 0

        for pickup in pickups_list:
            new_pickup_points.append(pickup.getCenter())

            if num_pickups_remaining == 0:
                if pickup.identity == "movable" and pickup.score == -2:
                    num_pickups_remaining += 1
            else:
                break

        updated_placed_pickup_points(new_pickup_points)

        # If no agents are holding and all movables do NOT have a score of -2, the agents have run out of
        # movables to create paths with. Therefore, the program should stop.
        if num_pickups_remaining == 0:
            num_agents_holding = 0

            for agent in agents_list:
                if num_agents_holding == 0:
                    if agent.is_holding is True:
                        num_agents_holding += 1
                else:
                    break

            if num_agents_holding == 0:
                print("The agents ran out of movables to place.")
                print("Number of iterations:", NUM_OF_ITERATIONS)
                print("Number of successful paths created:", num_successful_paths)

                if len(num_iterations_per_path) > 0:
                    for num_iterations in num_iterations_per_path:
                        print(f"{num_iterations}")

                # We want to free any movables that are NOT being used for the paths.
                # We do NOT want to free any unmovables, just update relevant scores.
                num_remaining_pickups = 0
                pickup_index = 0
                pickups_to_remove = []
                list_of_unmovable_indices = []

                for pickup in pickups_list:
                    if pickup.identity == "movable":
                        num_remaining_pickups += 1

                        pickup.identity = "gone"
                        pickup.undraw()
                        pickups_to_remove.append(pickup)

                    if pickup.identity == "unmovable":
                        pickup.score = -4
                        pickup.north_open = True
                        pickup.south_open = True
                        pickup.east_open = True
                        pickup.west_open = True

                        list_of_unmovable_indices.append(pickup_index)

                    pickup_index += 1

                continue_experiment = False

                # Commented out for data collection purposes.
                # agents_window.getMouse()

        # If the program has been going on for too long, then it should stop running.
        if NUM_OF_ITERATIONS >= MAX_NUM_OF_ITERATIONS:
            continue_experiment = False
            print(f"Agents exceeded the maximum number of {MAX_NUM_OF_ITERATIONS} iterations; stopping the program.")

    # Commented out for data collection purposes.
    # agents_window.getMouse()


def main():
    times_to_run = 1

    for _ in range(times_to_run):
        # Ensure that all global variables are set to their defaults before starting.
        global NUM_OF_AGENTS, NUM_OF_UNMOVABLE_PICKUPS, NUM_OF_MOVABLE_PICKUPS, STOP_MOTION_PLACEMENTS
        global WIN_WIDTH, WIN_HEIGHT, NUM_OF_ITERATIONS
        global MAX_NUM_OF_ITERATIONS, UNMOVABLE_MIN_DIST_APART, D_WIN_WIDTH, D_WIN_HEIGHT, D_TOP_LEFT_X, D_TOP_LEFT_Y
        global AGENT_RADIUS, AGENT_VELOCITY, TIME_BETWEEN_SET_DOWNS, TIME_TO_NOT_PICK_UP, FORCE_FACTOR
        global NO_SPAWN_RANGE, FIND_PICKUPS_RANGE, FIND_PICKUPS_RANGE_SQUARED, ATTRACTION_RANGE, \
            ATTRACTION_RANGE_SQUARED, ATTRACTION_EXCLUSION_ZONE, ATTRACTION_EXCLUSION_ZONE_SQUARED
        global TOTAL_NUM_OF_PICKUPS, PICKUP_HEIGHT, GRABBED_OBJECT_LIST, PLACED_PICKUP_POINTS
        # global agents_window  # [D]

        # Global variables [Important]
        NUM_OF_AGENTS = 20
        NUM_OF_UNMOVABLE_PICKUPS = 4
        NUM_OF_MOVABLE_PICKUPS = 100
        STOP_MOTION_PLACEMENTS = False  # Enables a stop-motion effect for case #1 if True

        # Global variables [Window]
        WIN_WIDTH, WIN_HEIGHT = 650, 500
        NUM_OF_ITERATIONS = 0

        # Global variables [Data Collection]
        MAX_NUM_OF_ITERATIONS = 7500
        UNMOVABLE_MIN_DIST_APART = 80
        D_WIN_WIDTH, D_WIN_HEIGHT = 500, 350
        D_TOP_LEFT_X, D_TOP_LEFT_Y = WIN_WIDTH - D_WIN_WIDTH, WIN_HEIGHT - D_WIN_HEIGHT

        # Global variables [Agents]
        AGENT_RADIUS = 7.5
        AGENT_VELOCITY = 5
        TIME_BETWEEN_SET_DOWNS = 20
        TIME_TO_NOT_PICK_UP = 20
        FORCE_FACTOR = 0.01

        NO_SPAWN_RANGE = 60  # X number of pixels away from the middle of the screen in all directions; movables only
        FIND_PICKUPS_RANGE = 35
        FIND_PICKUPS_RANGE_SQUARED = FIND_PICKUPS_RANGE ** 2
        ATTRACTION_RANGE = 100
        ATTRACTION_RANGE_SQUARED = ATTRACTION_RANGE ** 2
        ATTRACTION_EXCLUSION_ZONE = 19
        ATTRACTION_EXCLUSION_ZONE_SQUARED = ATTRACTION_EXCLUSION_ZONE ** 2

        # Global variables [Pickups]
        TOTAL_NUM_OF_PICKUPS = NUM_OF_UNMOVABLE_PICKUPS + NUM_OF_MOVABLE_PICKUPS
        PICKUP_HEIGHT = 20
        GRABBED_OBJECT_LIST = []
        PLACED_PICKUP_POINTS = []

        # Creates a white-colored screen for the agents to roam on that has dimensions divisible by 20.
        WIN_WIDTH = round(WIN_WIDTH / 20) * 20
        WIN_HEIGHT = round(WIN_HEIGHT / 20) * 20
        # agents_window = GraphWin('Pathfinding Model', WIN_WIDTH, WIN_HEIGHT)  # [D]

        x_low = AGENT_RADIUS * 2
        x_high = WIN_WIDTH - AGENT_RADIUS * 2
        y_low = AGENT_RADIUS * 2
        y_high = WIN_HEIGHT - AGENT_RADIUS * 2

        agents_list = create_agents()
        pickups_list = create_pickups(x_low, x_high, y_low, y_high)

        agent_animation(agents_list, pickups_list, x_low, x_high, y_low, y_high)

        print("=-= A run has finished. =-=")

        # agents_window.close()  # [D]

    print(f"==--== All runs have finished; total number of runs: {times_to_run}. ==--==")


if __name__ == "__main__":
    main()
