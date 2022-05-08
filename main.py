import pygame as pg
from random import randint
from pygame.locals import QUIT, USEREVENT, KEYDOWN, K_ESCAPE, K_DOWN, K_UP, K_LEFT, K_RIGHT, MOUSEBUTTONDOWN

from models import Tetromino

SCR_W = 400
GAME_W = SCR_W - (SCR_W/4)
SCR_H = 400
BLOCK_SIZE = SCR_W / 20
moveCooldown = 30
rotateCooldown = 30
score = 0
lines = 0
lines_limit = 10
level = 1
last_lev = 1
tetris_streak = False

def move_blocks(key, tetro, static_blocks):
    global rotateCooldown, moveCooldown
    #cooldown
    moveCooldown = moveCooldown - 1 if moveCooldown != 0 else 0
    rotateCooldown = rotateCooldown - 1 if rotateCooldown != 0 else 0

    #movement/rotation
    if key[K_UP] and not rotateCooldown:
        tetro.rotate((GAME_W,SCR_H), static_blocks)
        rotateCooldown = 15
    if key[K_LEFT] and not moveCooldown:
        tetro.move((GAME_W, SCR_H), static_blocks, K_LEFT)
        moveCooldown = 10
    elif key[K_RIGHT] and not moveCooldown:
        tetro.move((GAME_W, SCR_H), static_blocks, K_RIGHT)
        moveCooldown = 10

def shift_blocks(blocks_in_rows, blocks):   
    #removes blocks
    row_cleared = 0
    start_idx = -1
    for idx, val in enumerate(blocks_in_rows):
        if val == GAME_W/BLOCK_SIZE:
            if start_idx == -1:
                start_idx = idx-1
            row_cleared +=1
            for b in blocks.copy():
                if int(b.rect.y/BLOCK_SIZE) == idx:
                    b.kill()
                    blocks_in_rows[idx] -= 1
    #shifts blocks down
    if row_cleared:
        for i in range(len(blocks_in_rows)):
            for b in blocks:
                blocks_in_rows[int(b.rect.y/BLOCK_SIZE)] -= 1
                while not b.check_collision((SCR_W, SCR_H), blocks, 'D'):
                    b.move('D')
                blocks_in_rows[int(b.rect.y/BLOCK_SIZE)] += 1
        global score, lines, tetris_streak, level
        if row_cleared != 4:
            tetris_streak = False
        score += int((100 * (row_cleared ** 1.5)) * 1.5) if tetris_streak else int(100 * (row_cleared ** 1.5))
        lines += row_cleared
        if row_cleared == 4:
            tetris_streak = True

        if lines > lines_limit:
            level += 1
        

def create_next():
    next_tetro = Tetromino(15, BLOCK_SIZE, randint(0, 6))
    for b in next_tetro.blocks:
        b.rect.x += 10
        for i in range(5):
            b.move('D')
    return next_tetro
    
def draw_hud(screen, next_blocks):
    for b in next_blocks.blocks:
        screen.blit(b.image, b.rect)
    pg.draw.line(screen, "white", (305, 50), (305, 120))
    pg.draw.line(screen, "white", (305, 50), (390, 50))
    pg.draw.line(screen, "white", (305, 120), (390, 120))
    pg.draw.line(screen, "white", (390, 50), (390, 120))
    font = pg.font.Font("assets/arial.ttf", 14)
    
    text_surf = font.render("Next", True, "white")
    text_rect = text_surf.get_rect(topright = (360, 30))
    screen.blit(text_surf, text_rect)

    render_points(font, screen, "Score", score, (380, 150), (370, 170))
    render_points(font, screen, "Lines", lines, (380, 200), (370, 220))
    render_points(font, screen, "Level", level, (380, 240), (370, 260))

def game_over_hub(screen):
    font = pg.font.Font("assets/arial.ttf", 36)
    text_surf = font.render("Game Over", False, (255, 0, 150))
    text_rect = text_surf.get_rect(center = (SCR_W /2, SCR_H/2 - 100))
    screen.blit(text_surf, text_rect)
    button = pg.Surface((100,50))
    b_rect = button.get_rect(center = (SCR_W /2, SCR_H/2))
    button.fill((100, 250, 100))
    screen.blit(button, b_rect)
    font = pg.font.Font("assets/arial.ttf", 24)
    text_surf = font.render("Restart", False, (0, 0, 0))
    text_rect = text_surf.get_rect(center = (SCR_W /2, SCR_H/2))
    screen.blit(text_surf, text_rect)


    for event in pg.event.get():
        if event.type == MOUSEBUTTONDOWN and b_rect.collidepoint(pg.mouse.get_pos()):
            return True
    return False
    
def render_points(font, screen, lable, points, lab_pos, poi_pos):
    text_surf = font.render(f"---{lable}---", True, "white")
    text_rect = text_surf.get_rect(topright = lab_pos)
    screen.blit(text_surf, text_rect)
    text_surf = font.render(f"{points}", True, "white")
    text_rect = text_surf.get_rect(topright = poi_pos)
    screen.blit(text_surf, text_rect)

def main():
    global score, level, lines, lines_limit, last_lev, tetris_streak
    pg.init()
    pg.display.set_caption("tetris")
    screen = pg.display.set_mode((SCR_W,SCR_H))
    clock = pg.time.Clock()

    #groups to store the blocks 
    all_blocks = pg.sprite.Group()
    static_blocks = pg.sprite.Group()

    #stores the current active block
    tetro = Tetromino(randint(0,10), BLOCK_SIZE, randint(0,6))
    next_tetro = create_next()
    for block in tetro.blocks:
        all_blocks.add(block)
    blocks_in_rows = [0 for i in range(int(SCR_H/BLOCK_SIZE))]
    #timing variables
    BLOCK_FALL = USEREVENT +1
    FALL_FALL = USEREVENT +2
    pg.time.set_timer(BLOCK_FALL, 1000 - (100 * level))
    pg.time.set_timer(FALL_FALL, 70)

    timeStopped = 0

    bg = pg.image.load("assets/bg.png").convert()
    bg = pg.transform.scale(bg, (GAME_W, SCR_H))
    game_over = False
    while True:
        if not game_over:
            key = pg.key.get_pressed()
            #events/inputs
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    return False    
                if event.type == BLOCK_FALL and not key[K_DOWN]:
                    tetro.move((GAME_W, SCR_H), static_blocks)
                if event.type == FALL_FALL and key[K_DOWN]:
                    tetro.move((GAME_W, SCR_H), static_blocks)
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pg.quit()
                        return False
                    
            #logic/updates
            if level < 40 and level > last_lev:
                pg.time.set_timer(BLOCK_FALL, 1000 - (25 * level)) 
                last_lev +=1
        
            
            #left, right, and rotation movement
            move_blocks(key, tetro, static_blocks)
            #removs the block from the tetro object when it stops for more then a second and creates a new tetromino
        
            stopped = False
            for b in tetro.blocks:
                if b.check_collision((GAME_W, SCR_H), static_blocks, 'D'):
                    stopped = True
                    break
            if not stopped: 
                timeStopped = pg.time.get_ticks()
                
            if pg.time.get_ticks() - timeStopped > 400:
                for b in tetro.blocks:
                    if b.rect.y < 0:
                        game_over = True
                    static_blocks.add(b)
                    blocks_in_rows[int(b.rect.y/BLOCK_SIZE)] += 1
                tetro = Tetromino(randint(0,10), BLOCK_SIZE, next_tetro.type)
                for block in tetro.blocks:
                    all_blocks.add(block)
                next_tetro = create_next()
                score +=1
            #removes blocks when a row is filled and shifts blocks down
            shift_blocks(blocks_in_rows, static_blocks)            
        
        #drawing
        screen.fill("black")
        screen.blit(bg, (0,0))
        all_blocks.draw(screen)
        draw_hud(screen, next_tetro)
        if game_over:
            if game_over_hub(screen):
                for b in all_blocks:
                    b.kill()
                for b in static_blocks:
                    b.kill()
                tetro = Tetromino(randint(0,10), BLOCK_SIZE, randint(0,6))
                next_tetro = create_next()
                for block in tetro.blocks:
                    all_blocks.add(block)
                blocks_in_rows = [0 for i in range(int(SCR_H/BLOCK_SIZE))] 
                score = 0
                lines = 0
                lines_limit = 10
                level = 1
                last_lev = 1
                tetris_streak = False
                game_over = False
            
        pg.display.flip()
        clock.tick(60)
    
if __name__ == "__main__":
    main()