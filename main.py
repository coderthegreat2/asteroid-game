import asyncio
import pygame, random, math

async def main():
    pygame.init()

    font = pygame.font.SysFont("Arial", 24)
    screenx = 1200
    screeny = 800
    screen = pygame.display.set_mode((screenx, screeny))

    clock = pygame.time.Clock()
    running = True


    ship_pos = pygame.math.Vector2(screenx/2,screeny/2)
    ship_dir = 0
    ship_vel = pygame.math.Vector2(0,0)

    enemy_position = pygame.Vector2(screenx/4,screeny/2)
    enemy_angle = 0
    enemy_cd = 0

    DETECTION_RANGE = 300
    FOV_THRESHOLD = 0.7

    SHIP_ACCEL = 0.25
    MISSILE_SPEED = 12

    count = 12

    score = 0

    def draw_ship():
        x = int(ship_pos.x)
        y = int(ship_pos.y)

        original_points = [
            pygame.math.Vector2(x, y - 22),
            pygame.math.Vector2(x - 17, y + 18),
            pygame.math.Vector2(x, y + 10),
            pygame.math.Vector2(x + 17, y + 18)
        ]

        points = []

        for p in original_points[:]:
            points.append((p-pygame.math.Vector2(x,y)).rotate(ship_dir+90)+pygame.Vector2(x,y))


        pygame.draw.polygon(screen, (80, 255, 150), points, 2)

        pygame.draw.circle(screen, (80, 255, 150), (x,y), 3)

    def draw_enemy():
        x = int(enemy_position.x)
        y = int(enemy_position.y)

        original_points = [
            pygame.math.Vector2(x, y - 22),
            pygame.math.Vector2(x - 17, y + 18),
            pygame.math.Vector2(x, y + 10),
            pygame.math.Vector2(x + 17, y + 18)
        ]

        points = []

        for p in original_points[:]:
            points.append((p-pygame.math.Vector2(x,y)).rotate(-enemy_angle+90)+pygame.Vector2(x,y))

        pygame.draw.polygon(screen, (255, 80, 150), points, 2)

        pygame.draw.circle(screen, (255, 80, 150), (x,y), 3)
        

    class Asteroid():

        def __init__(self):

            self.r = random.randint(20,60)
            self.pos = pygame.math.Vector2(random.randint(0+self.r,screenx-self.r),random.randint(0+self.r,screeny-self.r))
            self.dir = random.uniform(0,2*math.pi)
            self.spe = random.uniform(1,5)
            self.vel = pygame.math.Vector2(math.cos(self.dir), math.sin(self.dir))*self.spe
            while self.pos.distance_to(ship_pos) < self.r+8+24:
                self.pos = pygame.math.Vector2(random.randint(0+self.r,screenx-self.r),random.randint(0+self.r,screeny-self.r))


        def update(self):
            self.pos += self.vel

            if self.pos.x <= 0+self.r:
                self.pos.x = 0+self.r
                self.vel.x = -self.vel.x
            if self.pos.x >= screenx-self.r:
                self.pos.x = screenx-self.r
                self.vel.x = -self.vel.x
            
            if self.pos.y <= 0+self.r:
                self.pos.y = 0+self.r
                self.vel.y = -self.vel.y
            if self.pos.y >= screeny-self.r:
                self.pos.y = screeny-self.r
                self.vel.y = -self.vel.y

        def draw(self):
            pygame.draw.circle(screen,(255,255,255),self.pos,self.r,4)

    def asteroid_collision(a1, a2):
        dist_sq = a1.pos.distance_squared_to(a2.pos)
        r_sum_sq = (a1.r + a2.r) **2

        if dist_sq <= r_sum_sq and dist_sq > 0:
            dist = math.sqrt(dist_sq)
            norm = (a2.pos-a1.pos)/dist

            overlap = math.sqrt(r_sum_sq) - dist
            a1.pos -= norm*overlap*0.5
            a2.pos += norm*overlap*0.5

            vel_relative = a2.vel-a1.vel
            vel_norm = vel_relative.dot(norm)

            if vel_norm < 0:
                a1.vel += norm * vel_norm 
                a2.vel -= norm * vel_norm


    class Missile():

        def __init__(self, pos, dir, vel, c):

            self.r = 4
            self.pos = pos
            self.dir = dir
            self.vel = vel        
            self.c = c

        def update(self):
            self.pos += self.vel

        def draw(self):
            pygame.draw.circle(screen,self.c,self.pos,self.r)

    def missile_collision(m,a) -> bool:
        dist_sq = m.pos.distance_squared_to(a.pos)
        r_sum_sq = (m.r + a.r) **2

        if dist_sq <= r_sum_sq and dist_sq > 0:
            return True

    def ship_collision(o):
        dist_sq = ship_pos.distance_squared_to(o.pos)
        r_sum_sq = (8 + o.r) **2

        if dist_sq <= r_sum_sq and dist_sq > 0:
            return True

    def missile_collision(m,a) -> bool:
        dist_sq = m.pos.distance_squared_to(a.pos)
        r_sum_sq = (m.r + a.r) **2

        if dist_sq <= r_sum_sq and dist_sq > 0:
            return True

    def ship_collision(o):
        dist_sq = ship_pos.distance_squared_to(o.pos)
        r_sum_sq = (8 + o.r) **2

        if dist_sq <= r_sum_sq and dist_sq > 0:
            return True
            
    asteroids = []
    missiles = []
    enemy_missiles = []

    for i in range(count):
        asteroids.append(Asteroid())

    # The Game Loop & Event Handling
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                target = pygame.Vector2(event.pos)
                direction = target - ship_pos
                direction = direction.normalize()
                missile_velocity = direction * MISSILE_SPEED
                missiles.append(Missile(pygame.math.Vector2(ship_pos), direction, missile_velocity,(255,255,255)))

        pressed = pygame.key.get_pressed()

        mouse_pos_relative = pygame.math.Vector2(pygame.mouse.get_pos())-ship_pos
        ship_dir = math.degrees(math.atan2(mouse_pos_relative.y,mouse_pos_relative.x))
        
        for i in range(len(asteroids)):
            asteroids[i].update()
            for j in range(count):
                asteroid_collision(asteroids[i],asteroids[j])

        for m in missiles[:]:
            m.update()
            for a in asteroids[:]:
                if missile_collision(m,a):
                    missiles.remove(m)
                    asteroids.remove(a)
                    asteroids.append(Asteroid())
                    score += 1
                    break

        for m in enemy_missiles[:]:
            m.update()
            if ship_collision(m):
                print(f"Score: {score}")
                running = False
                

        if pressed[pygame.K_w]:
            ship_vel += pygame.math.Vector2(1,0).rotate(ship_dir)*SHIP_ACCEL
        elif ship_vel != pygame.math.Vector2(0,0):
            ship_vel -= ship_vel.normalize()*SHIP_ACCEL
            if(ship_vel.magnitude() < 0.25):
                ship_vel -= ship_vel
        ship_pos += ship_vel
        if ship_pos.x > screenx:
            ship_pos.x -= screenx
        if ship_pos.x < 0:
            ship_pos.x += screenx
        if ship_pos.y > screeny:
            ship_pos.y -= screeny
        if ship_pos.y < 0:
            ship_pos.y += screeny

        for a in asteroids[:]:
            if ship_collision(a):
                print(f"Score: {score}")
                running = False

        if enemy_cd>0:
            enemy_cd -= 1

        radians = math.radians(enemy_angle)
        enemy_forward = pygame.Vector2(math.cos(radians),-math.sin(radians))
        to_player = (ship_pos - enemy_position)
        if to_player.length() > 0:
            to_player = to_player.normalize()
        distance = enemy_position.distance_to(ship_pos)
        dot = enemy_forward.dot(to_player)
        if distance < DETECTION_RANGE and dot > FOV_THRESHOLD:
            detected = True
        else:
            detected = False

        enemy_angle += 1

        if detected:
            enemy_angle = (ship_pos-enemy_position).angle_to(pygame.math.Vector2(1,0))

        if detected and enemy_cd == 0:
            target = ship_pos
            direction = target - enemy_position
            direction = direction.normalize()
            missile_velocity = direction * MISSILE_SPEED
            enemy_missiles.append(Missile(pygame.math.Vector2(enemy_position), direction, missile_velocity,(255,0,0)))
            enemy_cd = 20

        # Rendering (Drawing) Graphics  
        screen.fill((20, 24, 40))
        for i in range(count):
            asteroids[i].draw()

        for i in range(len(missiles)):
            missiles[i].draw()
        for i in range(len(enemy_missiles)):
            enemy_missiles[i].draw()

        draw_ship()
        draw_enemy()
        pygame.draw.circle(screen,(128,128,128),enemy_position,DETECTION_RANGE,1)

        score_text = font.render(f"Score: {score}",True,(255,255,255))
        screen.blit(score_text, (20,20))

        pygame.display.flip()

        # Frame Rate & Cleanup
        clock.tick(60)

    pygame.quit()

    await asyncio.sleep(0)

asyncio.run(main())