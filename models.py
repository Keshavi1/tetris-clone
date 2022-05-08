import pygame as pg
from pygame.locals import K_LEFT, K_RIGHT

class Block(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y, size, color):
        super(Block, self).__init__()
        self.size = size
        self.image = pg.Surface((self.size, self.size))
        self.image.fill(color)
        self.rect = self.image.get_rect(
            topleft = (self.size*pos_x, 0 - (self.size*pos_y)))

        self.vel = self.size
        #key movements
    def check_collision(self, scr, others, side) -> bool:
        if side == 'L':
            for block in others:
                if self.rect.topleft == block.rect.topright:
                    return True
            if self.rect.left == 0:
                return True
        if side == 'R':
            for block in others:
                if self.rect.topright == block.rect.topleft:
                    return True
            if self.rect.right == scr[0]:
                return True
        if side == 'D':
            for b in others:
                if self.rect.bottomleft == b.rect.topleft:
                    return True
            if self.rect.bottom == scr[1]:
                return True
        return False
    def move(self, side):
        if side == 'L':
            self.rect.move_ip(-self.size, 0)    
        if side == 'R':
            self.rect.move_ip(self.size, 0) 
        if side == 'D':
            self.rect.move_ip(0, self.size)       


class Tetromino():
    def __init__(self, pos, size, type = 0):
        self.center_index = 0
        self.type = type
        self.blocks = self._create(pos, size, type)
    def _create(self, pos, scr_w, type):
        blocks = []
        if type == 0:
            blocks = [Block(pos+i, 1, scr_w, "blue") for i in range(4)]
            self.center_index = 1
        elif type == 1:
            blocks = [Block(pos, 2, scr_w, "red")]
            for i in range(3):
                blocks.append(Block(pos+i, 1, scr_w, "red"))
            self.center_index = 2
        elif type == 2:
            blocks = [Block(pos+i, 1, scr_w, "yellow") for i in range(3)]
            blocks.append(Block(pos+2, 2, scr_w, "yellow"))
            self.center_index = 1
        elif type == 3:
            blocks = [Block(pos+i, 2, scr_w, "orange") for i in range(2)]
            for i in range(2):
                blocks.append(Block(pos+i, 1, scr_w, "orange"))
            self.center_index = 2
        elif type == 4:
            blocks = [Block(pos+i, 1, scr_w, "green") for i in range(2)]
            for i in range(1, 3):
                blocks.append(Block(pos+i, 2, scr_w, "green"))
            self.center_index = 1
        elif type == 5:
            blocks = [Block(pos+i, 2, scr_w, "purple") for i in range(2)]
            for i in range(1,3):
                blocks.append(Block(pos+i, 1, scr_w, "purple"))
            self.center_index = 2
        elif type == 6:
            blocks = [Block(pos+i, 1, scr_w, "light blue") for i in range(3)]
            blocks.append(Block(pos+1, 2, scr_w, "light blue"))
            self.center_index = 1
        return blocks
    #left and right movement
    def move(self, scr, others, key = None):
        collided = False
        side = 'L' if key == K_LEFT else 'R' if key == K_RIGHT else 'D'

        for b in self.blocks:
            if b.check_collision(scr, others, side):
                collided = True
                break
        if not collided:
            for b in self.blocks:
                b.move(side)

    #rotation for blocks int the horizantal and verical axis of the center block is done.
    #need to work on the coners now
    #also checks for collision so you can rotate if it clips you
    def rotate(self, scr, others):
        j = self.center_index
        testTeromino = [pg.Rect(self.blocks[i].rect) for i in range(4)]
        #rotates a copy of the Tetromino
        if self.type != 3:
            for i in range(4):
                if i != j:
                    ix = self.blocks[i].rect.x
                    jx = self.blocks[j].rect.x
                    iy = self.blocks[i].rect.y
                    jy = self.blocks[j].rect.y
                    size = self.blocks[i].size
                    dist_x = dist_y = 1
                    #horizontal block shifting
                    if iy == jy:
                        if abs(ix - jx) != size:
                            dist_x = dist_y = 2
                            
                        if ix < jx:
                            testTeromino[i].move_ip(size*dist_x, -size*dist_y)
                        elif ix > jx:
                            testTeromino[i].move_ip(-size*dist_x, size*dist_y) 
                    #vertical block shifting        
                    elif ix == jx:
                        if abs(iy - jy) != size:
                            dist_x = dist_y = 2
                        
                        if iy < jy:
                            testTeromino[i].move_ip(size*dist_x, size*dist_y) 
                        elif iy > jy:
                            testTeromino[i].move_ip(-size*dist_x, -size*dist_y)
                    #dyagonal block shifting        
                    elif ix != jx and iy != jy:
                        if ix < jx and iy > jy:
                            testTeromino[i].move_ip(0, -size*2)
                        elif ix < jx and iy < jy:
                            testTeromino[i].move_ip(size*2, 0)
                        elif ix > jx and iy < jy:
                            testTeromino[i].move_ip(0, size*2)
                        elif ix > jx and iy > jy:
                            testTeromino[i].move_ip(-size*2, 0)
        #checks if the copy is cliping and if not, the actual Tetromino is rotated
        collided = False
        for b in others:
            for t in testTeromino:
                if t.topleft == b.rect.topleft:
                    collided = True
                    break
        for t in testTeromino:
            if t.x < 0 or t.topright[0] > scr[0] or t.y > scr[1]:
                collided = True
                break
        if collided is False:
            for i in range(4):
                self.blocks[i].rect.x = testTeromino[i].x
                self.blocks[i].rect.y = testTeromino[i].y
        
            