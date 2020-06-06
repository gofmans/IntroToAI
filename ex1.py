import search
import random
import math
from copy import deepcopy


class State:
    def __init__(self,_game,_boxes,_walls,_free_goals,_taken_goals,_ice,_gcount,_pos,_free):
        self.game = _game
        self.boxes = _boxes
        self.walls = _walls
        self.free_goals = _free_goals
        self.taken_goals =_taken_goals
        self.ice = _ice
        self.gcount = _gcount
        self.pos = _pos
        self.free = _free

    def __hash__(self):
        return hash(self.game)

    def __eq__(self, other):
        if(self.game == other.game):
            return True
        else:
            return False

    def __lt__(self, other):
        if len(self.free_goals) < len(other.free_goals):
            return True
        else:
            return False

#_____________________________________________________________________________
class SokobanProblem(search.Problem):
    def __init__(self, initial):
        self.game = initial
        self.boxes = []
        self.walls = []
        self.free_goals = []
        self.taken_goals = []
        self.ice = []
        self.gcount = 0
        self.free = []
        self.pos = (0,0)
        for (i, row) in enumerate(self.game):
            for (j, col) in enumerate(row):
                if col in (20,27): #find all goal places
                    self.free_goals.append((i,j))
                if col in (30,35,37): #find all ice places
                    self.ice.append((i,j))
                if col in (15,25,35): #find all boxes
                    self.boxes.append((i,j))
                if col in (17,27,37): #find player location
                    self.pos = (i,j)
                if col == 99: #find walls
                    self.walls.append((i,j))
                if col == 25: #goal reached
                    self.gcount += 1
                    self.taken_goals.append((i,j))
                if col == 10:
                    self.free.append((i,j))
        rowlen = len(self.game[0])
        collen = len(self.game)
        for i in range(rowlen):
            self.walls.append((-1, i))
            self.walls.append((collen, i))
        for j in range(collen):
            self.walls.append((j, -1))
            self.walls.append((j, rowlen))
        myState = State(self.game,self.boxes,self.walls,self.free_goals,self.taken_goals,self.ice,self.gcount,self.pos,self.free)
        search.Problem.__init__(self, myState)

#________________________________________________________________________________________________
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a tuple, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        dim_m = len(state.game)
        dim_n = len(state.game[0])
        if (len(state.boxes) - len(state.taken_goals)) < len(state.free_goals): #unsolvable problem
            return
        danger_boxes = set(state.boxes) - set(state.taken_goals) #check for dead end
        #print(danger_boxes)
        danger_count = 0
        if danger_boxes: #free boxes exist (not in goal)
            for box in danger_boxes:
                if self.dead_end(state, box,'no action'):
                    danger_count += 1
            if len(state.boxes) - danger_count < len(state.free_goals): #not enouth free boxs
                return

        tempPos = state.pos
        down = (tempPos[0] + 1, tempPos[1])
        up = (tempPos[0] - 1, tempPos[1])
        left = (tempPos[0], tempPos[1] - 1)
        right = (tempPos[0], tempPos[1] + 1)
        moves = {}

        moves['D'] = down
        moves['L'] = left
        moves['R'] = right
        moves['U'] = up

        approved = []
        for action, npos in moves.items():
            if npos in state.free or npos in state.free_goals: #free slot ahead
                approved.append(action)
            elif npos in state.ice: #ice ahead
                approved.append(action)
            elif npos in state.boxes:
                temp_next = self.get_next(npos, action)
                if temp_next in state.boxes or temp_next in state.walls : #we cant move that box!
                    continue
                if self.is_fatal(state, npos, action):
                    if len(state.boxes) - 1 >= len(state.free_goals) and (dim_m * dim_n < 30):
                        approved.append(action)  # if we have enought boxes we can still make it
                else: #not fatal
                    approved.append(action)  # dont make fatal moves


        for legal_action in approved:
            yield legal_action

#___________________________________________________________________________________________
    def is_fatal(self, state, box_pos, action):
        nextpos = self.get_next(box_pos, action)
        if nextpos not in state.walls and nextpos not in state.boxes and nextpos not in state.ice:
            if nextpos in state.free_goals:
                return False #legal action
            if self.dead_end(state, nextpos, action):
                return True
            else:
                return False #legal action
        if nextpos in state.ice:
            after_ice_pos = self.get_after_ice_pos(nextpos, action, state)
            if after_ice_pos in state.free_goals:
                return False
            elif self.dead_end(state, after_ice_pos, action):
                return True
            return False #legal action
        return False #fail safe

#_________________________________________________________________________________
    def get_next(self, pos, action):
        if action == 'U':
            res = (pos[0] - 1, pos[1])
        if action == 'D':
            res = (pos[0] + 1, pos[1])
        if action == 'L':
            res = (pos[0], pos[1] - 1)
        if action == 'R':
            res = (pos[0], pos[1] + 1)
        return res

# _________________________________________________________________________________________
    def dead_end(self, state, npos, action):
        tempPos = npos
        down = (tempPos[0] + 1, tempPos[1])
        up = (tempPos[0] - 1, tempPos[1])
        left = (tempPos[0], tempPos[1] - 1)
        right = (tempPos[0], tempPos[1] + 1)

        danger_group = set(state.walls)
        if (down in danger_group and right in danger_group):
            return True
        elif (down in danger_group and left in danger_group):
            return True
        elif (up in danger_group and left in danger_group):
            return True
        elif (up in danger_group and right in danger_group):
            return True
        if action=='no action':
            return False
        #check if next to wall and we will die
        if action == 'U':
            if up in danger_group:#next to wall
                right_dead_end = True
                temp_right = deepcopy(right)
                while temp_right not in danger_group:
                    temp_above = self.get_next(temp_right,'U')#if above is wall
                    if temp_above not in danger_group or temp_right in state.free_goals: #found a breach, no dead end
                        right_dead_end = False
                        break
                    temp_right = self.get_next(temp_right,'R')

                left_dead_end = True
                temp_left = deepcopy(left)
                while temp_left not in danger_group:
                    temp_above = self.get_next(temp_left,'U')#if above is wall
                    if temp_above not in danger_group or temp_left in state.free_goals: #found a breach, no dead end
                        left_dead_end = False
                        break
                    temp_left = self.get_next(temp_left,'L')
                if left_dead_end and right_dead_end:
                    return True
        if action == 'D':
            if down in danger_group:  # next to wall
                right_dead_end = True
                temp_right = deepcopy(right)
                while temp_right not in danger_group:
                    temp_below = self.get_next(temp_right, 'D')  # if below is wall
                    if temp_below not in danger_group or temp_right in state.free_goals:  # found a breach, no dead end
                        right_dead_end = False
                        break
                    temp_right = self.get_next(temp_right, 'R')

                left_dead_end = True
                temp_left = deepcopy(left)
                while temp_left not in danger_group:
                    temp_below = self.get_next(temp_left, 'D')  # if above is wall
                    if temp_below not in danger_group or temp_left in state.free_goals:  # found a breach, no dead end
                        left_dead_end = False
                        break
                    temp_left = self.get_next(temp_left, 'L')
                if left_dead_end and right_dead_end:
                    return True
        if action == 'L':
            if left in danger_group:  # next to wall
                up_dead_end = True
                temp_up = deepcopy(up)
                while temp_up not in danger_group:
                    temp_lefty = self.get_next(temp_up, 'L')  # if left side is wall
                    if temp_lefty not in danger_group or temp_up in state.free_goals:  # found a breach, no dead end
                        up_dead_end = False
                        break
                    temp_up = self.get_next(temp_up, 'U')

                down_dead_end = True
                temp_down = deepcopy(down)
                while temp_down not in danger_group:
                    temp_lefty = self.get_next(temp_down, 'L')  # if left side is wall
                    if temp_lefty not in danger_group or temp_down in state.free_goals:  # found a breach, no dead end
                        down_dead_end = False
                        break
                    temp_down = self.get_next(temp_down, 'D')
                if up_dead_end and down_dead_end:
                    return True
        if action == 'R':
            if right in danger_group:  # next to wall
                up_dead_end = True
                temp_up = deepcopy(up)
                while temp_up not in danger_group:
                    temp_righty = self.get_next(temp_up, 'R')  # if right side is wall
                    if temp_righty not in danger_group or temp_up in state.free_goals:  # found a breach, no dead end
                        up_dead_end = False
                        break
                    temp_up = self.get_next(temp_up, 'U')

                down_dead_end = True
                temp_down = deepcopy(down)
                while temp_down not in danger_group:
                    temp_righty = self.get_next(temp_down, 'R')  # if left side is wall
                    if temp_righty not in danger_group or temp_down in state.free_goals:  # found a breach, no dead end
                        down_dead_end = False
                        break
                    temp_down = self.get_next(temp_down, 'D')
                if up_dead_end and down_dead_end:
                    return True
        return False
#___________________________________________________________________________________________
    def get_after_ice_pos(self, nextpos, action, state):
        after_ice_pos = self.get_next(nextpos, action)
        prev_pos = nextpos
        if prev_pos in state.boxes:
            return
        while after_ice_pos in state.ice and after_ice_pos not in state.boxes:
            prev_pos = after_ice_pos
            after_ice_pos = self.get_next(after_ice_pos, action)
        if after_ice_pos in state.walls or after_ice_pos in state.boxes:  # end of ice path isnt clear, we will stop on ice
            return prev_pos
        return after_ice_pos
#_____________________________________________________________________________________________
    def man_dist(self,pos1,pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ________________________________________________________________________________________________
    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        temp_state = deepcopy(state)
        old_grid = [list(i) for i in temp_state.game]
        grid = [list(i) for i in temp_state.game]  # make our game mutable
        old = temp_state.pos
        if action == 'U':  # find new position for player
            new_pos = (old[0] - 1, old[1])
        if action == 'D':
            new_pos = (old[0] + 1, old[1])
        if action == 'L':
            new_pos = (old[0], old[1] - 1)
        if action == 'R':
            new_pos = (old[0], old[1] + 1)
        taken_flag = False
        if new_pos in temp_state.free or new_pos in temp_state.free_goals:
            grid[old[0]][old[1]] = grid[old[0]][old[1]] - 7  # update old place
            if grid[old[0]][old[1]] == 10:
                temp_state.free.append(old) #left empty space
            grid[new_pos[0]][new_pos[1]] = grid[new_pos[0]][new_pos[1]] + 7 #update new place
            temp_state.pos = new_pos
            if new_pos in temp_state.free:
                temp_state.free.remove(new_pos) #that place isn't free anymore
        elif new_pos in temp_state.ice and new_pos not in temp_state.boxes:
            grid[old[0]][old[1]] = grid[old[0]][old[1]] - 7  # update old place
            if grid[old[0]][old[1]] == 10:
                temp_state.free.append(old) #left empty space
            after_ice_pos = self.get_after_ice_pos(new_pos, action, temp_state)
            if after_ice_pos in temp_state.free or after_ice_pos in temp_state.free_goals: #road ahead is free!
                if after_ice_pos in temp_state.free:
                    temp_state.free.remove(after_ice_pos)
                grid[after_ice_pos[0]][after_ice_pos[1]] = grid[after_ice_pos[0]][after_ice_pos[1]] + 7 # player new location
                temp_state.pos = after_ice_pos
            else: # road ahead is blocked!
                grid[after_ice_pos[0]][after_ice_pos[1]] = grid[after_ice_pos[0]][after_ice_pos[1]] + 7
                temp_state.pos = after_ice_pos
        elif new_pos in temp_state.boxes:
            grid[old[0]][old[1]] = grid[old[0]][old[1]] - 7  # update old place
            ice_flag = True #player started on ice
            if grid[old[0]][old[1]] == 10:
                temp_state.free.append(old)  # left empty space
                ice_flag = False
            temp_state.pos = new_pos
            if new_pos in temp_state.taken_goals:
                taken_flag = True
            temp_next = self.get_next(new_pos, action)
            if temp_next in temp_state.walls or temp_next in temp_state.boxes: # can't move!
                grid[old[0]][old[1]] = grid[old[0]][old[1]] + 7
                if not ice_flag:
                    temp_state.free.remove(old)  # back to normal
                temp_state.pos = old # nothing changed
            elif temp_next in temp_state.free: # box can move to new place
                grid[new_pos[0]][new_pos[1]] = grid[new_pos[0]][new_pos[1]] + 7 - 5  # update new place
                grid[temp_next[0]][temp_next[1]] = grid[temp_next[0]][temp_next[1]] + 5 # box in new place
                temp_state.boxes.remove(new_pos) #remove old box's place
                temp_state.boxes.append(temp_next)
                temp_state.free.remove(temp_next) #that place is taken now!
                if taken_flag: #we just moved a box away from it's goal
                    temp_state.taken_goals.remove(new_pos)
                    temp_state.free_goals.append(new_pos)
            elif temp_next in temp_state.free_goals:
                grid[new_pos[0]][new_pos[1]] = grid[new_pos[0]][new_pos[1]] + 7 - 5   # player is now on this spot
                grid[temp_next[0]][temp_next[1]] = grid[temp_next[0]][temp_next[1]] + 5  # box in new place
                temp_state.boxes.remove(new_pos)  # remove old box's place
                temp_state.boxes.append(temp_next)

                temp_state.free_goals.remove(temp_next)  # that place is taken now!
                temp_state.taken_goals.append(temp_next) #new goal reached
                if taken_flag: #we just moved a box away from it's goal
                    temp_state.taken_goals.remove(new_pos)
                    temp_state.free_goals.append(new_pos)
            elif temp_next in temp_state.ice:
                grid[new_pos[0]][new_pos[1]] = grid[new_pos[0]][new_pos[1]] + 7 - 5  # player is now on this spot instead of box
                final_pos = self.get_after_ice_pos(temp_next, action, temp_state) #get box new place

                if taken_flag: #we just moved a box away from it's goal
                    temp_state.taken_goals.remove(new_pos)
                    temp_state.free_goals.append(new_pos)
                if final_pos in temp_state.ice: #road ahead of ice path is blocked
                    grid[final_pos[0]][final_pos[1]] = grid[final_pos[0]][final_pos[1]] + 5 #box with ice now
                    temp_state.boxes.remove(new_pos) #remove old box's place
                    temp_state.boxes.append(final_pos) #add to boxs list
                elif final_pos in temp_state.free_goals:
                    grid[final_pos[0]][final_pos[1]] = grid[final_pos[0]][final_pos[1]] + 5  # box in new place
                    temp_state.boxes.remove(new_pos)  # remove old box's place
                    temp_state.boxes.append(final_pos)
                    temp_state.free_goals.remove(final_pos)  # that place is taken now!
                    temp_state.taken_goals.append(final_pos)  # new goal reached
                elif final_pos in temp_state.free:
                    grid[final_pos[0]][final_pos[1]] = grid[final_pos[0]][final_pos[1]] + 5  # box in new place
                    temp_state.boxes.remove(new_pos)  # remove old box's place
                    temp_state.boxes.append(final_pos)
                    temp_state.free.remove(final_pos)  # that place is taken now!

        temp_state.game = tuple(tuple(i) for i in grid) #update game board
        # for (i, row) in enumerate(temp_state.game):
        #     for (j, col) in enumerate(row):
        #         if col not in [10,15,99,17,20,25,27,30,35,37]: #iligal board
        #             print('old grid: ')
        #             for row1 in old_grid:
        #                 print(row1)
        #             print('illigal grid: ')
        #             for rowe in temp_state.game:
        #                 print(rowe)
        #             print('-----------------------------')
        #         continue
        return temp_state


# ________________________________________________________________________________________________
    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        if len(state.free_goals) == 0: #no free goals
            return True
        return False

# ________________________________________________________________________________________________
    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        temp_state = deepcopy(node.state)
        if len(temp_state.free_goals) == 0:
            return 0
        my_pos = temp_state.pos
        target_boxes = set(temp_state.boxes) - set(temp_state.taken_goals)
        temp_goals = deepcopy(temp_state.free_goals)

        total = 0
        if not target_boxes:
            return 0
        else:
            boxes = list(target_boxes)
            while boxes:
                if not temp_goals:
                    break
                box_dic = {}
                for box in boxes:
                    box_dic[box] = min(self.man_dist(box, fgoal) for fgoal in temp_goals)
                closest_box = [box for box, dis in box_dic.items() if dis == min(box_dic.values())][0]

                min_dis = box_dic[closest_box]
                for fgoal in temp_goals:
                    if self.man_dist(closest_box, fgoal) == min_dis:  # found closest goal to box
                        total += min_dis
                        temp_goals.remove(fgoal)
                        break
                boxes.remove(closest_box)
            small_addition = self.man_dist(my_pos, list(target_boxes)[0])
            return total + small_addition

        # total_dist = 0
        # if target_boxes:
        #     for box in target_boxes:
        #         if not temp_goals:  # no more goals
        #             break
        #         temp_min = min(self.man_dist(box, fgoal) for fgoal in temp_goals)
        #         temp_len = len(temp_goals)+1
        #         for fgoal in temp_goals:
        #             if self.man_dist(box, fgoal) == temp_min:  # found closest goal to box
        #                 total_dist += temp_min/(temp_len - len(temp_goals))
        #                 temp_goals.remove(fgoal)
        #                 break
        # else:
        #     return 0
        # small_addition = self.man_dist(my_pos,list(target_boxes)[0])
        # return total_dist + small_addition



def create_sokoban_problem(game):
    return SokobanProblem(game)



