import math
import random
from graphics import *

# ALGORITHM #1 -- PICKUPS PLACED ARE PLACED PERMANENTLY #

# Global variables [Window]
WIN_WIDTH, WIN_HEIGHT = 1000, 750
NUM_OF_ITERATIONS = 0

# Global variables [Agents]
NUM_OF_AGENTS = 30
NUM_OF_PICKUPS = 36
AGENT_RADIUS = 7.5
AGENT_VELOCITY = 10
TIME_BETWEEN_SET_DOWNS = 40
TIME_TO_NOT_PICK_UP = 40
FIND_PICKUPS_RANGE = 50
NO_SPAWN_RANGE = 60  # X number of pixels away from the middle of the screen in all directions

# Global variables [Pickups]
PICKUP_HEIGHT = 20
DIST_BETWEEN_PICKUPS = 100
GRABBED_OBJECT_LIST = []

# Creates a white-colored screen for the agents to roam on.
# For data collection, comment out lines of code with a "[1] data collection" next to it.
agents_window = GraphWin('Basic Swarm Application', WIN_WIDTH, WIN_HEIGHT)  # [1] data collection


class Agent(Circle):
    def __init__(self, point):
        Circle.__init__(self, center=point, radius=7.5)
        Circle.setFill(self, color_rgb(255, 255, 0))  # Yellow
        self.dx = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY)
        self.dy = random.randrange(-AGENT_VELOCITY, AGENT_VELOCITY)

        if self.dx == 0:
            self.dx += AGENT_VELOCITY / 2

        if self.dy == 0:
            self.dy += AGENT_VELOCITY / 2

        self.is_holding = False
        self.just_picked_up = False

        self.set_down_cooldown = 0
        self.pick_up_cooldown = 0


class Pickup(Rectangle):
    def __init__(self, top_left, bottom_right):
        Rectangle.__init__(self, p1=top_left, p2=bottom_right)
        Rectangle.setFill(self, color_rgb(0, 0, 255))  # Blue


def update_num_of_pickups(num_pickups_per_row):
    global NUM_OF_PICKUPS
    NUM_OF_PICKUPS = num_pickups_per_row ** 2


def update_num_of_iterations():
    global NUM_OF_ITERATIONS
    NUM_OF_ITERATIONS += 1


def create_agents(x_low, x_high, y_low, y_high):
    list_of_agents = []

    for _ in range(NUM_OF_AGENTS):
        center = get_random_point(x_low, x_high, y_low, y_high)

        agent_to_add = Agent(center)
        agent_to_add.draw(agents_window)  # [1] data collection
        list_of_agents.append(agent_to_add)

    return list_of_agents


def create_pickups():
    list_of_pickups = []

    # The number of pickups in a row is determined by the square root of the chosen number of pickups.
    num_pickups_per_row = round(math.sqrt(NUM_OF_PICKUPS))

    # The number of pickups variable will need to be altered to reflect this change.
    update_num_of_pickups(num_pickups_per_row)

    middle_of_window_x = WIN_WIDTH / 2
    middle_of_window_y = WIN_HEIGHT / 2

    # Calculate the top-left most point using the middle of the screen.
    start_top_left_x = middle_of_window_x - (num_pickups_per_row * 10)
    start_top_left_y = middle_of_window_y - (num_pickups_per_row * 10)

    # Calculate the bottom-right point of the top-left most pickup.
    start_bottom_right_x = start_top_left_x + 20
    start_bottom_right_y = start_top_left_y + 20

    # Variables to store all the x and y coordinates for the new points.
    new_top_left_x = start_top_left_x
    new_top_left_y = start_top_left_y
    new_bottom_right_x = new_top_left_x + 20
    new_bottom_right_y = new_top_left_y + 20

    # Systematically create a num_pickups_per_row by num_pickups_per_row square of NUM_OF_PICKUPS (rounded) pickups.
    for i in range(num_pickups_per_row):
        for j in range(num_pickups_per_row):
            pickup_to_add = Pickup(Point(new_top_left_x, new_top_left_y), Point(new_bottom_right_x, new_bottom_right_y))
            pickup_to_add.draw(agents_window)  # [1] data collection
            list_of_pickups.append(pickup_to_add)

            new_top_left_x += 20
            new_bottom_right_x += 20

        new_top_left_x = start_top_left_x
        new_top_left_y = start_top_left_y + ((i + 1) * 20)

        new_bottom_right_x = start_bottom_right_x
        new_bottom_right_y = start_bottom_right_y + ((i + 1) * 20)

    return list_of_pickups


# Generates a random Point object that is outside the range of any pickup.
def get_random_point(x_low, x_high, y_low, y_high):
    extra_buffer = 20
    top_left_no_spawn_x = ((WIN_WIDTH / 2) - NO_SPAWN_RANGE) - extra_buffer
    top_left_no_spawn_y = ((WIN_HEIGHT / 2) - NO_SPAWN_RANGE) - extra_buffer
    bottom_right_no_spawn_x = ((WIN_WIDTH / 2) + NO_SPAWN_RANGE) + extra_buffer
    bottom_right_no_spawn_y = ((WIN_HEIGHT / 2) + NO_SPAWN_RANGE) + extra_buffer

    x = random.randint(*random.choice([(x_low, top_left_no_spawn_x), (bottom_right_no_spawn_x, x_high)]))
    y = random.randint(*random.choice([(y_low, top_left_no_spawn_y), (bottom_right_no_spawn_y, y_high)]))

    return Point(x, y)


def agent_animation(agents_list, pickups_list, x_low, x_high, y_low, y_high):
    continue_experiment = True
    prior_successful_placements = 0

    altered_pickups_list = []

    while continue_experiment:
        for agent in agents_list:
            agent.just_picked_up = False

            # The agent is holding a pickup.
            if agent.is_holding is True:
                new_agent_dx = agent.dx
                new_agent_dy = agent.dy

                # altered_pickups should REPEL agents.
                for altered_pickup in altered_pickups_list:
                    distance_squared = ((agent.getCenter().getX() - altered_pickup.getCenter().getX()) ** 2) + \
                                       ((agent.getCenter().getY() - altered_pickup.getCenter().getY()) ** 2)

                    if distance_squared <= (FIND_PICKUPS_RANGE ** 2):
                        repel_force_x = 1 - (0.01 * math.sqrt(distance_squared))
                        repel_force_y = 1 - (0.01 * math.sqrt(distance_squared))

                        if agent.getCenter().getX() < altered_pickup.getCenter().getX():
                            repel_force_x = -repel_force_x
                        if agent.getCenter().getY() < altered_pickup.getCenter().getY():
                            repel_force_y = -repel_force_y

                        new_agent_dx += repel_force_x
                        new_agent_dy += repel_force_y

                # pickups should REPEL agents.
                for pickup in pickups_list:
                    distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                       ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                    if distance_squared <= (FIND_PICKUPS_RANGE ** 2):
                        repel_force_x = 1 - (0.01 * math.sqrt(distance_squared))
                        repel_force_y = 1 - (0.01 * math.sqrt(distance_squared))

                        if agent.getCenter().getX() < pickup.getCenter().getX():
                            repel_force_x = -repel_force_x
                        if agent.getCenter().getY() < pickup.getCenter().getY():
                            repel_force_y = -repel_force_y

                        new_agent_dx += repel_force_x
                        new_agent_dy += repel_force_y

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

                drop_pickup = True

                # Reduces an agent's cooldown to pick up another pickup, if applicable.
                if agent.pick_up_cooldown > 0:
                    agent.pick_up_cooldown -= 1

                # Determines if an agent should drop a pickup, if it is holding one.
                elif agent.pick_up_cooldown == 0:
                    for pickup in pickups_list:
                        distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                           ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                        if distance_squared < (DIST_BETWEEN_PICKUPS ** 2):
                            drop_pickup = False
                            break

                    for altered_pickup in altered_pickups_list:
                        alt_distance_squared = ((agent.getCenter().getX() - altered_pickup.getCenter().getX()) ** 2) + \
                                               ((agent.getCenter().getY() - altered_pickup.getCenter().getY()) ** 2)

                        if alt_distance_squared < (DIST_BETWEEN_PICKUPS ** 2):
                            drop_pickup = False
                            break

                    if drop_pickup is True:
                        altered_pickup = Pickup(agent.getP1(), agent.getP2())
                        altered_pickup.setFill(color_rgb(120, 81, 169))  # Purple
                        altered_pickup.setOutline(color_rgb(0, 0, 0))  # Black

                        altered_pickup.draw(agents_window)  # [1] data collection
                        altered_pickups_list.append(altered_pickup)

                        agent.setFill(color_rgb(255, 255, 0))  # Yellow
                        agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS
                        agent.is_holding = False
                        agent.just_picked_up = True

            # The agent is NOT holding a pickup.
            elif agent.is_holding is False and agent.just_picked_up is False:
                new_agent_dx = agent.dx
                new_agent_dy = agent.dy

                # pickups should ATTRACT agents.
                for pickup in pickups_list:
                    distance_squared = ((agent.getCenter().getX() - pickup.getCenter().getX()) ** 2) + \
                                       ((agent.getCenter().getY() - pickup.getCenter().getY()) ** 2)

                    if distance_squared <= (FIND_PICKUPS_RANGE ** 2):
                        attract_force_x = 1 - (0.01 * math.sqrt(distance_squared))
                        attract_force_y = 1 - (0.01 * math.sqrt(distance_squared))

                        if agent.getCenter().getX() > pickup.getCenter().getX():
                            attract_force_x = -attract_force_x
                        if agent.getCenter().getY() > pickup.getCenter().getY():
                            attract_force_y = -attract_force_y

                        new_agent_dx += attract_force_x
                        new_agent_dy += attract_force_y

                # altered_pickups should REPEL agents.
                for altered_pickup in altered_pickups_list:
                    distance_squared = ((agent.getCenter().getX() - altered_pickup.getCenter().getX()) ** 2) + \
                                       ((agent.getCenter().getY() - altered_pickup.getCenter().getY()) ** 2)

                    if distance_squared <= (FIND_PICKUPS_RANGE ** 2):
                        repel_force_x = 1 - (0.01 * math.sqrt(distance_squared))
                        repel_force_y = 1 - (0.01 * math.sqrt(distance_squared))

                        if agent.getCenter().getX() < altered_pickup.getCenter().getX():
                            repel_force_x = -repel_force_x
                        if agent.getCenter().getY() < altered_pickup.getCenter().getY():
                            repel_force_y = -repel_force_y

                        new_agent_dx += repel_force_x
                        new_agent_dy += repel_force_y

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

                    # The extra check to ensure the agent is not holding any pickups is necessary to
                    # ensure the agent doesn't grab two pickups at the same time.
                    if distance_squared <= ((agent.radius + (PICKUP_HEIGHT / 2)) ** 2) and agent.is_holding is False:
                        if pickup not in GRABBED_OBJECT_LIST:
                            GRABBED_OBJECT_LIST.append(pickup)

                            agent.setFill(color_rgb(0, 255, 0))  # Green
                            agent.is_holding = True
                            agent.set_down_cooldown = TIME_BETWEEN_SET_DOWNS

                            pickups_list.remove(pickup)
                            pickup.undraw()  # [1] data collection

                    index += 1

        # One iteration/cycle of the program has occurred, so update the counter.
        update_num_of_iterations()

        # Now, we need to check to see if the agents have fulfilled their mission.
        num_successful_placements = len(altered_pickups_list)

        # Comment this entire if statement out for # [1] data collection.
        if num_successful_placements != prior_successful_placements:
            print("Progress towards completion: ", num_successful_placements / NUM_OF_PICKUPS)

        if num_successful_placements == NUM_OF_PICKUPS:
            continue_experiment = False
            print("Number of iterations: ", NUM_OF_ITERATIONS)

        prior_successful_placements = num_successful_placements


def main():
    x_low = AGENT_RADIUS * 2
    x_high = WIN_WIDTH - AGENT_RADIUS * 2
    y_low = AGENT_RADIUS * 2
    y_high = WIN_HEIGHT - AGENT_RADIUS * 2

    agents_list = create_agents(x_low, x_high, y_low, y_high)
    pickups_list = create_pickups()

    agent_animation(agents_list, pickups_list, x_low, x_high, y_low, y_high)

    # After the agents stop moving after 'runFor' seconds, the user clicks again to exit the program.
    agents_window.getMouse()  # [1] data collection
    agents_window.close()  # [1] data collection


if __name__ == "__main__":
    main()
