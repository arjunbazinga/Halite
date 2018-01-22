"""
This bot is inspired by arjunvis's writeup., written from scratch.
"""

import hlt
import logging
import math
from sys import argv



A = {"unowned planet": -1, "friendly planet": 1,
     "enemy planet": -0.5, "enemy ship": -1, "friendly ship": 1}
B = {"unowned planet": float(1), "friendly planet": float(1),
     "enemy planet": float(1), "enemy ship": float(1), "friendly ship": float(1)}

INF = 1000000000


def _gauss_grad(entity, foreign_entity, a, b):
    xdiff = entity.x - foreign_entity.x
    ydiff = entity.y - foreign_entity.y
    temp = 2 * a * b * \
        math.exp(-b * foreign_entity.calculate_distance_between(entity)**2)
    return xdiff * temp, ydiff * temp


def gauss_grad(entity, foreign_entity, a, b):
    epsilon = 1e-13
    xdiff = entity.x - foreign_entity.x
    ydiff = entity.y - foreign_entity.y
    temp = a / (epsilon + foreign_entity.calculate_distance_between(entity)**3)
    temp2 = entity.radius * foreign_entity.radius
    return xdiff * temp * temp2, ydiff * temp * temp2


game = hlt.Game("oppo")
logging.info("To infinity, and beyond!")
while True:
    game_map = game.update_map()
    command_queue = []
    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue
        distance = INF
        for planet in game_map.all_planets():
            if(ship.calculate_distance_between(planet) <= distance):
                closest_planet = planet
                distance = ship.calculate_distance_between(planet)

        if ship.can_dock(closest_planet) and not closest_planet.is_full():
            command_queue.append(ship.dock(closest_planet))
        else:
            gradx = 0
            grady = 0
            distance = INF
            for foreign_entity in game_map._all_ships() + game_map.all_planets():
                if ship == foreign_entity:
                    continue
                if isinstance(foreign_entity, hlt.entity.Planet):
                    if foreign_entity.owner is None:
                        a, b = A["unowned planet"], B["unowned planet"]
                        x, y = gauss_grad(ship, foreign_entity, a, b)
                        gradx += x
                        grady += y
                        if(ship.calculate_distance_between(foreign_entity) <= distance):
                            distance = ship.calculate_distance_between(
                                foreign_entity)
                    else:
                        if foreign_entity.owner == ship.owner:
                            a, b = A["friendly planet"], B["friendly planet"]
                            x, y = gauss_grad(ship, ship.closest_point_to(foreign_entity), a, b)
                            gradx += x
                            grady += y
                            if(ship.calculate_distance_between(foreign_entity) <= distance):
                                distance = ship.calculate_distance_between(
                                    foreign_entity)
                        else:
                            a, b = A["enemy planet"], B["enemy planet"]
                            x, y = gauss_grad(ship, foreign_entity, a, b)
                            gradx += x
                            grady += y
                else:
                    if foreign_entity.owner == ship.owner:
                        a, b = A["friendly ship"], B["friendly ship"]
                        x, y = gauss_grad(ship, foreign_entity, a, b)
                        gradx += x
                        grady += y
                        if(ship.calculate_distance_between(foreign_entity) <= distance):
                            distance = ship.calculate_distance_between(
                                foreign_entity)
                    else:
                        a, b = A["enemy ship"], B["enemy ship"]
                        x, y = gauss_grad(ship, foreign_entity, a, b)
                        gradx += x
                        grady += y
            speed = int(hlt.constants.MAX_SPEED)
            angle = math.degrees(math.atan2(grady, gradx)) % 360
            speed = speed if (distance > speed) else distance
            command_queue.append(ship.thrust(speed, angle))
    game.send_command_queue(command_queue)
