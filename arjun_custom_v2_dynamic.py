# This version also combines grouping, thanks to gvs.

# get k nearest ships/targets
import heapq
import random
from sys import argv
import hlt
import logging
from collections import OrderedDict
game = hlt.Game("New bot")
logging.info("yes")


# TODO:  timing out : better navigation
# TODO:  make the ships form groups
# TODO: Fix initial problem
#

def randomly(seq):
    shuffled = list(seq)
    random.shuffle(shuffled)
    return iter(shuffled)


initial_ships = game_map.get_me().all_ships()
game_map = game.update_map()

while True:
    game_map = game.update_map()
    command_queue = []


    my_ships = game_map.get_me().all_ships()
    my_undocked_ships = [s for s in my_ships if s.docking_status == s.DockingStatus.UNDOCKED]

    k = 5#int(len(my_undocked_ships)**0.75)# group of ships : attack same target.
    docked_enemy_ships = []
    unowned_planets = []
    friendly_planets = []
    for foreign_entity in game_map._all_ships() + game_map.all_planets():
        if  isinstance(foreign_entity, hlt.entity.Ship):
            if foreign_entity not in my_ships: #enemy ship
                if foreign_entity.docking_status != foreign_entity.DockingStatus.UNDOCKED :
                    docked_enemy_ships.append(foreign_entity)
        else:
            if foreign_entity.is_owned():
                if foreign_entity.owner == game_map.my_id:
                    friendly_planets.append(foreign_entity)
            else:
                unowned_planets.append(foreign_entity)



    # though using sets would make stuff faster.
    alloted_ship = set() #keeps track of ship already in a cluster.
    already_targeted =set() # keeps track of targeted entities

    for ship in randomly(my_undocked_ships):
        # If ship has already been alloted skip,it.
        if ship in alloted_ship:
            continue

        # get k nearest ships.
        poss_ships = [s for s in my_undocked_ships if s not in alloted_ship]


        k = k if (len(poss_ships)>k) else len(poss_ships)


        group = heapq.nsmallest(k,poss_ships,key = lambda s: ship.calculate_distance_between(s))

        # get k nearest targets.
        if foreign_entity in already_targeted:
            continue

        poss_targets = docked_enemy_ships
        if len(unowned_planets) > 2:
            poss_targets+=unowned_planets

        num_targets = k if len(poss_targets)>k else len(poss_targets)

        targets =  heapq.nsmallest(num_targets,poss_targets,key = lambda s: ship.calculate_distance_between(s))

        if len(targets):
            t = 0
            for s in group:
                target=targets[t%len(targets)]
                if isinstance(target, hlt.entity.Ship):
                    navigate_command = s.navigate(
                    s.closest_point_to(target),
                    game_map,
                    speed = int(hlt.constants.MAX_SPEED),
                    ignore_ships = False)
                    if navigate_command:
                        command_queue.append(navigate_command)
                else:
                    # how to send ship to unique planet
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
                already_targeted.add(target)
                alloted_ship.add(s) # adding this group to alloted_ship
        else:
            # empty attack list, help friendly_planets.
            target = max(friendly_planets, key = lambda s:ship.calculate_distance_between(s))
            for s in group:
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
                alloted_ship.add(s)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END
