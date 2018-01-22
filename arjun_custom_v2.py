# This version also combines grouping, thanks to gvs.

# get k nearest ships/targets
import heapq

from sys import argv
import hlt
import logging
from collections import OrderedDict
game = hlt.Game("Army greedy"+argv[1])
logging.info("yes")



# TODO:  timing out : better navigation
# TODO:  make the ships form groups
# TODO: Fix initial problem
#

def nearby_entities_by_distance(game_map, ship):
    """
    :param entity: The source entity to find distances from
    :return: Dict containing all entities with their designated distances
    :rtype: dict
    """


while True:
    game_map = game.update_map()
    command_queue = []

    my_ships = game_map.get_me().all_ships()
    my_undocked_ships = [s for s in my_ships if s.docking_status == s.DockingStatus.UNDOCKED]

    alloted_ship = [] #keeps track of ship already in a cluster.
    k = int(argv[1])# group of ships : attack same target.

    for ship in my_undocked_ships:
        # If ship has already been alloted skip,it.
        if ship in alloted_ship:
            continue

        # get k nearest ships.
        poss_ships = [s for s in my_undocked_ships if s not in alloted_ship]
        k = k if (len(poss_ships)>k) else len(poss_ships)
        group = heapq.nsmallest(k,poss_ships,key = lambda s: ship.calculate_distance_between(s))

        # get target.
        poss_targets = []
        for foreign_entity in game_map._all_ships() + game_map.all_planets():
            if  isinstance(foreign_entity, hlt.entity.Ship) and foreign_entity not in my_ships and foreign_entity.docking_status != ship.DockingStatus.UNDOCKED or isinstance(foreign_entity, hlt.entity.Planet) and not foreign_entity.is_owned():
                poss_targets.append(foreign_entity)

        targets =  heapq.nsmallest(k,poss_targets,key = lambda s: ship.calculate_distance_between(s))


        t = 0
        for s in group:
            target=targets[t]
            if isinstance(target, hlt.entity.Ship):
                navigate_command = s.navigate(
                s.closest_point_to(target),
                game_map,
                speed = int(hlt.constants.MAX_SPEED),
                ignore_ships = False)
                if navigate_command:
                    command_queue.append(navigate_command)
            else:
                t+=1
                # send ship to unique planet
                # check if docking at the same time kills them.
                if s.can_dock(target):
                    command_queue.append(s.dock(target))
                else:
                    navigate_command=s.navigate(
                    s.closest_point_to(target),
                    game_map,
                    speed = int(hlt.constants.MAX_SPEED),
                    ignore_ships = False)
                    if navigate_command:
                        command_queue.append(navigate_command)
        alloted_ship+=group # adding this group to alloted_ship

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
