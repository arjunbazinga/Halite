import hlt
import logging
from collections import OrderedDict
game = hlt.Game("greedy")
logging.info("yum")

# TODO:  better navigation
# TODO:  make the ships form groups



while True:
    game_map = game.update_map()
    command_queue = []
    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        ebd = game_map.nearby_entities_by_distance(ship)
        ebd = OrderedDict(
            sorted(ebd.items(), key=lambda t: t[0]))

        team_ships = game_map.get_me().all_ships()


        interesting = []
        for distance in ebd:
            if  isinstance(ebd[distance][0], hlt.entity.Ship) and ebd[distance][0] not in team_ships and ebd[distance][0].docking_status != ship.DockingStatus.UNDOCKED:
                interesting.append(ebd[distance][0])
                break
            if isinstance(ebd[distance][0], hlt.entity.Planet) and not ebd[distance][0].is_owned():
                interesting.append(ebd[distance][0])
                break

        if len(interesting):
            target = interesting[0]
            if isinstance(target, hlt.entity.Ship):
                navigate_command = ship.navigate(
                            ship.closest_point_to(target),
                            game_map,
                            speed = int(hlt.constants.MAX_SPEED),
                            ignore_ships = False)
                if navigate_command:
                    command_queue.append(navigate_command)
            else:
                if ship.can_dock(target):
                    command_queue.append(ship.dock(target))
                else:
                    navigate_command=ship.navigate(
                                ship.closest_point_to(target),
                                game_map,
                                speed = int(hlt.constants.MAX_SPEED),
                                ignore_ships = False)
                    if navigate_command:
                        command_queue.append(navigate_command)
        else:
            # enemy ships flying about.
            pass



    game.send_command_queue(command_queue)
    # TURN END
# GAME END
