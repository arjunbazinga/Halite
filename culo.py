"""
This bot uses electromagnetic fields to play.
"""

import hlt
import logging
import math
from sys import argv


K = {"unowned planet": -1, "friendly planet": 0,
     "enemy planet": 0, "enemy ship": -1, "friendly ship":1}

D= 0

INF = 1000000000


def culoumb(entity, foreign_entity, K):
    epsilon = 1e-15
    xdiff = entity.x - foreign_entity.x
    ydiff = entity.y - foreign_entity.y
    temp = K * entity.radius * foreign_entity.radius

    temp2 = (epsilon + foreign_entity.calculate_distance_between(entity)**2)
    return xdiff * temp / temp2, ydiff * temp / temp2


def LJ(entity, foreign_entity, d):
    r0 = 1
    rc = 4 * (2**-(1 / 6)) * r0
    r = foreign_entity.calculate_distance_between(entity)
    if (r > rc):
        return 0, 0
    else:
        r0 = entity.radius + foreign_entity.radius
        xdiff = entity.x - foreign_entity.x
        ydiff = entity.y - foreign_entity.y
        r06 = r0**6
        r_8 = r**-8
        temp = 12 * d * ((r06**2) * ((r**2) * (r_8**2)) - r06 * r_8)
        return xdiff * temp, ydiff * temp


game = hlt.Game("culo")
logging.info("zap!")
while True:
    game_map = game.update_map()
    command_queue = []
    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        distance = INF
        for planet in game_map.all_planets():
            new_dist = ship.calculate_distance_between(planet)
            if(new_dist <= distance):
                closest_planet = planet
                distance = new_dist

        if ship.can_dock(closest_planet) and not closest_planet.is_full():
            command_queue.append(ship.dock(closest_planet))
        else:
            gradx = 0
            grady = 0
            distance = INF
            all_entities = game_map._all_ships() + game_map.all_planets()
            for foreign_entity in all_entities:
                if ship == foreign_entity:
                    continue

                if isinstance(foreign_entity, hlt.entity.Planet):
                    if foreign_entity.owner is None:
                        logging.info("empty planet found")
                        k = K["unowned planet"]
                        nav_point = ship.closest_point_to(foreign_entity)
                        x, y = culoumb(ship, nav_point, k)
                        gradx += x
                        grady += y

                        d = ship.calculate_distance_between(foreign_entity)
                        if(d <= distance):
                            distance = d

                    else:
                        if foreign_entity.owner == ship.owner:
                            k = K["friendly planet"]
                            nav_point = ship.closest_point_to(foreign_entity)
                            x, y = culoumb(ship, nav_point, k)

                            gradx += x
                            grady += y

                            d = ship.calculate_distance_between(foreign_entity)
                            if(d <= distance):
                                distance = d

                        else:
                            k = K["enemy planet"]
                            x, y = culoumb(ship, foreign_entity, k)
                            gradx += x
                            grady += y

                else:
                    if foreign_entity.owner == ship.owner:
                        # friendly ship

    #
                        x, y = LJ(ship, foreign_entity, D)
                        #gradx += x
                        #grady += y

                        #k = K["friendly ship"]
                        #x, y = culoumb(ship, foreign_entity, k)
                        #gradx += x
                        #grady += y

                    # ships became too slow when they got together.
                    #    d = ship.calculate_distance_between(foreign_entity)
                    #    if(d <= distance):
                    #        distance = d
                    else:
                        if foreign_entity.docking_status != ship.DockingStatus.UNDOCKED:
                            k = K["enemy ship"]
                            x, y = culoumb(ship, foreign_entity, k)
                            gradx += x
                            grady += y

            speed = int(hlt.constants.MAX_SPEED)
            angle = math.degrees(math.atan2(grady, gradx)) % 360

            speed = speed if (distance > speed) else distance

            command_queue.append(ship.thrust(speed, angle))

    game.send_command_queue(command_queue)
