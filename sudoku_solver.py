board = [[4,3,0,9,0,2,0,6,8],
         [0,5,0,0,0,0,0,0,0],
         [0,8,0,4,0,7,0,2,0],
         [9,0,7,0,1,0,0,0,0],
         [0,0,0,0,0,0,0,0,0],
         [0,0,0,0,6,0,5,0,9],
         [0,2,0,3,0,5,0,8,0],
         [0,0,0,0,0,0,0,5,0],
         [8,9,0,2,0,1,0,3,6]
         ]
class Sudoku:

    def __init__(self, board):
        self.board = board

        self.solved = False

        if self.isValidBoard() and self.isFilled():
            self.solved = self.solve()

    def isFilled(self):
        cnt=0
        for i in range(9):
            for j in range(9):
                if board[i][j]>0:
                    cnt+=1
        
        return cnt>15
    
    def isValidBoard(self):

        for i in range(9):
            freq = [0] * 10

            for j in range(9):
                if self.board[i][j] > 0:
                    freq[self.board[i][j]] += 1

            for cnt in freq:
                if cnt > 1:
                    return False

        for j in range(9):
            freq = [0] * 10

            for i in range(9):
                if self.board[i][j] > 0:
                    freq[self.board[i][j]] += 1

            for cnt in freq:
                if cnt > 1:
                    return False

        for x in range(0, 9, 3):
            for y in range(0, 9, 3):

                freq = [0] * 10

                for i in range(3):
                    for j in range(3):

                        val = self.board[x + i][y + j]

                        if val > 0:
                            freq[val] += 1

                for cnt in freq:
                    if cnt > 1:
                        return False

        return True

    def valid(self, row, col, num):

        for i in range(9):
            if self.board[row][i] == num:
                return False

        for i in range(9):
            if self.board[i][col] == num:
                return False

        sr = (row // 3) * 3
        sc = (col // 3) * 3

        for i in range(sr, sr + 3):
            for j in range(sc, sc + 3):
                if self.board[i][j] == num:
                    return False

        return True

    def solve(self):

        if not self.isValidBoard():
            return False

        for row in range(9):
            for col in range(9):

                if self.board[row][col] == 0:

                    for num in range(1, 10):

                        if self.valid(row, col, num):

                            self.board[row][col] = num

                            if self.solve():
                                return True

                            self.board[row][col] = 0

                    return False

        return True