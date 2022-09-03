import random
from BaseAI import BaseAI
import numpy as np
from Grid import Grid
from collections import deque
from Utils import manhattan_distance
# TO BE IMPLEMENTED
#
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.parent = None
        self.maxResult = {}
        self.minResult = {}
        self.chanceResult = {}
        self.heuristic = {}

        self.maxResult_trap = {}
        self.minResult_trap = {}
        self.chanceResult_trap = {}
        self.heuristic_trap = {}

        # new ver. of Game.py includes this
        # used in get_trap to identify enemy
        self.player_num = None

    # 1. the number of ways for this position to escape
    # 2. the number of critical cells for each directions, the more, the better
    def heuristicMove(self, grid):
        currX, currY = self.getPosition()
        prevX, prevY = self.getParent()
        key = "#".join([str(grid), str(self.getPosition()), str(self.getParent())])
        if key in self.heuristic:
            return self.heuristic[key]
        deltaX, deltaY = currX - prevX, currY - prevY
        # bfs to find out the avaiable cells toward the current direct
        # heursitic is the number of cells in this direction
        heuristic = -1
        visited = set([(currX, currY)])
        # diagonal
        if deltaX != 0:
            pass
        if deltaY != 0:
            pass
        queue = deque([(currX, currY)])
        while queue:
            x, y = queue.popleft()
            heuristic += 1
            for nx, ny in [(x + 1, y), (x + 1, y - 1), (x + 1, y + 1), (x, y - 1), (x, y + 1),\
                           (x - 1, y), (x - 1, y - 1), (x - 1, y + 1)]:
                limitx, limity = 0 <= nx < 7, 0 <= ny < 7
                if deltaX != 0:
                    limitx = prevX <= nx < 7 if deltaX > 0 else 0 <= nx <= prevX
                if deltaY != 0:
                    limity = prevY <= ny < 7 if deltaY > 0 else 0 <= ny <= prevY
                if limitx and limity and grid.map[(nx, ny)] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        self.heuristic[key] = heuristic
        return self.heuristic[key]

    def heuristicFast(self, grid):
        indices = np.where(grid.map == 0)
        currX, currY = self.getPosition()
        prevX, prevY = self.getParent()
        deltaX, deltaY = currX - prevX, currY - prevY
        count = 0
        for x, y in list(zip(indices[0], indices[1])):
            limitx = prevX <= x < 7 if deltaX > 0 else 0 <= x <= prevX
            limity = prevY <= y < 7 if deltaY > 0 else 0 <= y <= prevY
            if limitx and limity:
                count += 1
        return count

    def heuristicRandom(self, grid):
        return random.randint(0, 1)

    def chance(self, trapPos, remainDepth, grid, alpha, beta):
        key = str(grid.map) + '#' + str(trapPos) + '#' + str(remainDepth)
        if key in self.chanceResult:
            return self.chanceResult[key]
        traps = grid.get_neighbors(trapPos, only_available=True)
        alphaDis = manhattan_distance(self.getPosition(), trapPos)
        grid.setCellValue(trapPos, -1)
        h, dmy = self.maximzerMove(remainDepth, grid, alpha, beta)
        # if this trap cause me to lose
        if h == float('-inf'):
            self.chanceResult[key] = float('-inf')
        else:
            expectedHeuristic = (1 - 0.05 * (alphaDis - 1)) * h
            grid.setCellValue(trapPos, 0)
            for trap in traps:
                grid.setCellValue(trap, -1)
                h, move = self.maximzerMove(remainDepth, grid, alpha, beta)
                grid.setCellValue(trap, 0)
                if h == float('-inf'):
                    expectedHeuristic = float('-inf')
                    break
                expectedHeuristic += 0.05 * (alphaDis - 1) * h / len(traps)
            self.chanceResult[key] = expectedHeuristic
        return self.chanceResult[key]

    # minimizer min beta
    def minimizerThrow(self, remainDepth, grid, alpha, beta):
        if remainDepth == 0:
            return self.heuristicMove(grid)
        key = str(grid.map) + '#' + str(remainDepth)
        if key in self.minResult:
            return self.minResult[key]
        minHeurstic = float('inf')
        for trapPos in grid.get_neighbors(self.getPosition(), only_available=True):
            heuristic = self.chance(trapPos, remainDepth - 1, grid, alpha, beta)
            if heuristic < minHeurstic:
                minHeurstic = beta = heuristic
            # pruning
            if beta <= alpha:
                break
        self.minResult[key] = minHeurstic
        return self.minResult[key]

    # maximzer max alpha
    def maximzerMove(self, remainDepth, grid, alpha, beta):
        if remainDepth == 0:
            return self.heuristicMove(grid), None
        key = str(grid.map) + '#' + str(remainDepth)
        if key in self.maxResult:
            return self.maxResult[key]
        # backup the current position
        currPos = self.getPosition()
        # remove the current position on the grid
        grid.setCellValue(currPos, 0)
        maxHeuristic, bestMove = float('-inf'), -1
        for nextPos in grid.get_neighbors(currPos, only_available=True):
            # move to the new position
            self.setPosition(nextPos)
            grid.setCellValue(nextPos, 1)
            heuristic = self.minimizerThrow(remainDepth - 1, grid, alpha, beta)
            if heuristic >= maxHeuristic:
                maxHeuristic, alpha, bestMove = heuristic, heuristic, nextPos
            # move back
            grid.setCellValue(nextPos, 0)
            # pruning
            if beta <= alpha:
                break
        # set back
        grid.setCellValue(currPos, 1)
        self.setPosition(currPos)
        self.maxResult[key] = (maxHeuristic, bestMove)
        return self.maxResult[key]

    def IDS(self, grid, depth=4):
        # sync pos and parent
        pos = self.getPosition()
        self.setParent(pos)
        # IDS to find the optimal move
        alpha, beta = float("-inf"), float("inf")
        maxHeuristic, bestMove = self.maximzerMove(depth, grid, alpha, beta)
        return bestMove

    def getMove(self, grid: Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE
        The function should return a tuple of (x,y) coordinates to which the player moves.
        You may adjust the input variables as you wish but output has to be the coordinates.
        
        """
        
        """New ver. of Game.py take cares of moving the player.
        So only need to return the desired moving location.
        Game.py will call player's setPosition() to set """
        # self.setPosition(self.IDS(grid))
        # return self.getPosition()
        return self.IDS(grid)
   

    def getPosition(self):
        return self.pos

    def setPosition(self, new_pos: tuple):
        self.pos = new_pos

    def getParent(self):
        return self.parent

    def setParent(self, new_pos: tuple):
        self.parent = new_pos


    """New version of Game.py calls this in game initialization
        player_num will be used to identify opponent in get_trap """
    # added this
    def setPlayerNum(self, num):
        self.player_num = num


    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE
        The function should return a tuple of (x,y) coordinates to which the player *wants* 
        to throw the trap. 
        
        You do not need to account for probabilities. We've implemented that for you.
        You may adjust the input variables as you wish but output has to be the coordinates.
        
        """
        
        return self.IDS_trap(grid)

    
    def heuristic_simple_trap(self, grid: Grid):
        """simple version heuristic function
            returns (8 - num of cells the opponent can move)
        """

        # find opponent
        opponent = grid.find(3 - self.player_num)

        # find all available cells surrounding Opponent
        available_cells = grid.get_neighbors(opponent, only_available=True)

        return 8 - len(available_cells)


    def IDS_trap(self, grid, depth=4):

        pos = self.getPosition()
        self.setParent(pos)

        alpha, beta = float("-inf"), float("inf")
        _, bestThrow = self.maximizer_trap(depth, grid, alpha, beta)
        return bestThrow


    def chance_trap(self, trapPos, remainDepth, grid, alpha, beta):

        key = str(grid.map) + '#' + str(trapPos) + '#' + str(remainDepth)
        if key in self.chanceResult_trap:
            return self.chanceResult_trap[key]
        
        # find all available cells surrounding Opponent
        trap_neigbbors = grid.get_neighbors(trapPos, only_available=True)

        alphaDis = manhattan_distance(self.getPosition(), trapPos)

        grid.setCellValue(trapPos, -1)
        heuristic = self.minimizer_move(remainDepth, grid, alpha, beta)
        # no other options (heuristic stays at inf)
        if heuristic == float('inf'):
            self.chanceResult_trap[key] = float('inf')
            
        expectedHeuristic = (1 - 0.05 * (alphaDis - 1)) * heuristic
        grid.setCellValue(trapPos, 0)

        for trap in trap_neigbbors:

            grid.setCellValue(trap, -1)
            heuristic = self.minimizer_move(remainDepth, grid, alpha, beta)
            grid.setCellValue(trap, 0)

            if heuristic == float('inf'):
                expectedHeuristic = float('inf')
                break

            expectedHeuristic += 0.05 * (alphaDis - 1) * heuristic / len(trap_neigbbors)

        self.chanceResult_trap[key] = expectedHeuristic

        return self.chanceResult_trap[key]


    def maximizer_trap(self, remainDepth, grid, alpha, beta):

        if remainDepth == 0:
            # return utility (i.e., heuristic for this state)
            return self.heuristic_simple_trap(grid), None

        key = str(grid.map) + '#' + str(remainDepth)
        if key in self.maxResult_trap:
            return self.maxResult_trap[key]
        
        maxHeuristic, bestThrow = float('-inf'), -1

        # find opponent
        opponent = grid.find(3 - self.player_num)
        # find all available cells surrounding Opponent
        available_cells = grid.get_neighbors(opponent, only_available=True)

        for trapPos in available_cells:

            grid.setCellValue(trapPos, -1)
            # ignore chance node for now
            # heuristic = self.minimizer_move(remainDepth - 1, grid, alpha, beta)
            heuristic = self.chance_trap(trapPos, remainDepth - 1, grid, alpha, beta)
            grid.setCellValue(trapPos, 0)

            if heuristic >= maxHeuristic:
                maxHeuristic, alpha, bestThrow = heuristic, heuristic, trapPos
            # pruning
            if beta <= alpha:
                break

        self.maxResult_trap[key] = (maxHeuristic, bestThrow)

        return self.maxResult_trap[key]
        

    def minimizer_move(self, remainDepth, grid, alpha, beta):
        
        if remainDepth == 0:
            return self.heuristic_simple_trap(grid)
        
        key = str(grid.map) + '#' + str(remainDepth)
        if key in self.minResult_trap:
            return self.minResult_trap[key]
        
        # backup opponent's current position
        opponent = 3 - self.player_num
        currPos = grid.find(opponent)

        # remove the current position on the grid
        grid.setCellValue(currPos, 0)
        
        minHeurstic = float('inf')
        for nextPos in grid.get_neighbors(currPos, only_available=True):
            # move to the new position
            grid.setCellValue(nextPos, opponent)
            heuristic, throw = self.maximizer_trap(remainDepth - 1, grid, alpha, beta)

            if heuristic < minHeurstic:
                minHeurstic = beta = heuristic

            # move back
            grid.setCellValue(nextPos, 0)

            # pruning
            if beta <= alpha:
                break
        # set back
        grid.setCellValue(currPos, opponent)
        self.minResult_trap[key] = minHeurstic
        return self.minResult_trap[key]
        
        
        
        
        
        
        
        
        
        
        
        
        # original trial for minimax
        # if maxing:
        #     # get the best utility and trap location out of all possible throwing points
        #     # possible throing points: available cells around the opponent
        #     child_states = self.get_child_states()

        #     max_util = float('-inf')
        #     for child_state in child_states:
        #         # find the max
        #         utility = self.minimax_trap(child_state, depth - 1, maxing=False)
        #         if utility > max_util:
        #             max_util = utility

        #     return max_util
            
        # else:
        #     # minimizing (oponent's move)
        #     pass
        
        
