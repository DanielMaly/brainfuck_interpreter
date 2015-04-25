__author__ = 'Daniel Maly'

# Common PNG writer with pixels already ready

# Grid generator for given width, height and program

# Pixel generator for brainloller given a grid

# Pixel generator for braincopter given the source image and the grid

# Brainloller encoder: Program -> optimal width and height -> grid -> pixels -> write PNG
# Braincopter encoder: Program, source image -> grid -> source image + grid -> pixels -> write PNG


class PNGWriter:
    pass


class GridMaker:
    def __init__(self, program, width, height):
        self.program = program
        self.width = width
        self.height = height

    # This will return a grid of BRAINFUCK commands. Nop is represented by #.
    # Turns are represented by R,L
    # The grid is constructed from the top left
    def make_grid(self):

        program = self.program
        grid = []

        for row in range(self.height):
            assembled_row = []
            for column in range(self.width):
                if row > 0 and column == 0:
                    assembled_row.append('L')
                elif row < self.height - 1 and column == self.width - 1:
                    assembled_row.append('R')
                elif len(program) > 0:
                    if row % 2 == 0:
                        assembled_row.append(program[0])
                    else:
                        assembled_row.insert(1, program[0])
                    program = program[1:]
                else:
                    assembled_row.append('#')
            grid.append(assembled_row)

        return grid


class BrainlollerEncoder:
    def __init__(self, program, filename):
        self.program = program
        self.filename = filename

    def encode(self):
        # First we get the optimal width and height
        width, height = self.optimal_width_and_height()

        # Then we make the command grid (common part with braincopter)
        grid = GridMaker(self.program, width, height).make_grid()
        print(grid)

        # Then we convert the grid into pixels
        # Then we pass it to the PNG writer (common part with braincopter)
        pass

    def optimal_width_and_height(self):
        length = len(self.program)
        fits = lambda w, h: (w-2) * h + 2

        width, height = 3, 3
        while fits(width, height) < length:
            if width > height:
                height += 1
            else:
                width += 1

        print("Computed optimal width and height: {},{}".format(width, height))
        return width, height