from traceback import print_tb
import pygame
import math
pygame.init()

WIDTH, HEIGHT =  1920, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("body Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 30)

class Body:
    # Astronomical Unity
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    sc = 100
    SCALE = sc / AU 
    TIMESTEP = 3600 * 24 * 1 # 1 day in second

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0
        self.distance_to_sun_x = 0
        self.distance_to_sun_y = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        if not self.sun:
            pygame.draw.line(
                win,
                self.color,
                (
                    self.x * self.SCALE + WIDTH / 2,
                    self.y * self.SCALE + HEIGHT / 2
                ),
                (
                    (self.x + self.distance_to_sun_x)* self.SCALE + WIDTH / 2,
                    (self.y + self.distance_to_sun_y)* self.SCALE + HEIGHT / 2
                ),
                2
            )
        pygame.draw.circle(win, self.color, (x, y), self.radius)
        
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)} KM", 1, WHITE)
            velocity_text = FONT.render(f"{round(math.sqrt(self.x_vel ** 2 + self.y_vel ** 2), 1)} KM/H", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))
            win.blit(velocity_text, (x - distance_text.get_width()/2, y + distance_text.get_height()/2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

            self.distance_to_sun_x = distance_x
            self.distance_to_sun_y = distance_y

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, bodies):
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue

            fx, fy = self.attraction(body)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))
    
    def unelastic_collission(self, body1, body2):
        my_x_vel_final = body1.x_vel * (body1.mass - body2.mass)/(body1.mass + body2.mass) + body2.x_vel * 2 * body2.mass / (body1.mass + body2.mass) * (1 - body1.mass/(body1.mass + body2.mass))
        my_y_vel_final = body1.y_vel * (body1.mass - body2.mass)/(body1.mass + body2.mass) + body2.y_vel * 2 * body2.mass / (body1.mass + body2.mass) * (1 - body1.mass/(body1.mass + body2.mass))



        body_x_vel_final = 2 *  body1.x_vel * body1.mass/(body1.mass + body2.mass) - body2.x_vel * (body1.mass - body2.mass) / (body1.mass + body2.mass) * (1 - body1.mass/(body1.mass + body2.mass))
        body_y_vel_final = 2 *  body1.y_vel * body1.mass/(body1.mass + body2.mass) - body2.y_vel * (body1.mass - body2.mass) / (body1.mass + body2.mass) * (1 - body1.mass/(body1.mass + body2.mass))

        return (my_x_vel_final, my_y_vel_final, body_x_vel_final, body_y_vel_final)

    def check_colision(self, bodies):
        for body in bodies:
            if self == body:
                continue

            distance_x = body.x - self.x
            distance_y = body.y - self.y
            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
            if distance * Body.SCALE <= body.radius + self.radius:
                r, m = self.merge_body(body)
                if self.mass >= body.mass:
                    print('aq1')
                    self.x_vel, self.y_vel, body.x_vel, body.y_vel = self.unelastic_collission(self, body)
                    self.radius, self.mass = r, m
                    bodies.remove(body)
                else:
                    print('aq2')
                    body.x_vel, body.y_vel, self.x_vel, self.y_vel = self.unelastic_collission(body, self)
                    body.radius, body.mass = r, m
                    bodies.remove(self)

    
    def add_wall_collision(self):
        if self.x * self.SCALE - self.radius < -(WIDTH/2):
            self.x_vel *= -1

        if self.y * self.SCALE - self.radius < -(HEIGHT/2): 
            self.y_vel *= -1

        if self.x * self.SCALE + self.radius > (WIDTH/2):
            self.x_vel *= -1

        if self.y * self.SCALE + self.radius > (HEIGHT/2): 
            self.y_vel *= -1


    def merge_body(self, body):
        my_volume = (4/3) * math.pi * (self.radius ** 3)
        other_volume = (4/3) * math.pi * (body.radius ** 3)

        total_volume = my_volume + other_volume

        new_radius = (total_volume*(3/4)/math.pi)**(1/3)

        new_mass = self.mass + body.mass
 
        return new_radius, new_mass

def main():
    
    run = True
    clock = pygame.time.Clock()

    bodies = []
    body_drag = False
    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))
        left_pressed = False
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                
                x, y =pygame.mouse.get_pos()
                x = (x - WIDTH/2)/Body.sc
                y = (y - HEIGHT/2)/Body.sc

                if event.key == pygame.K_e:
                    earth = Body(x * Body.AU, y* Body.AU, 16, BLUE, 5.9742 * 10**24)
                    earth.y_vel = 29.783 * 1000

                    bodies.append(earth)

                if keys[pygame.K_LEFT] and keys[pygame.K_m]:
                    left_pressed = True
                    
                    mercury = Body(x * Body.AU, y * Body.AU, 8, DARK_GREY, 3.30 * 10**23)
                    mercury.y_vel = 47.4 * 1000
                    bodies.append(mercury)

                if keys[pygame.K_m] and left_pressed == False:
                    mars = Body(x * Body.AU, y * Body.AU, 12, RED, 6.39 * 10**23)
                    mars.y_vel = 24.077 * 1000

                    bodies.append(mars)

                if keys[pygame.K_s]:
                    sun = Body(x * Body.AU, y * Body.AU, 30, YELLOW, 1.98892 * 10**30)
                    sun.sun = True
                    bodies.append(sun)

                if keys[pygame.K_b]:
                    bh = Body(x * Body.AU, y * Body.AU, 20, (148, 0, 211), 1.98892 * 10**30 * 100)
                    bh.sun = True
                    bodies.append(bh)

                if keys[pygame.K_v]:
                    venus = Body(x * Body.AU, y * Body.AU, 14, WHITE, 4.8685 * 10**24)
                    venus.y_vel = 35.02 * 1000
                    bodies.append(venus)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:   
                    x, y = pygame.mouse.get_pos()
                    x = (x - WIDTH/2)/Body.sc * Body.AU
                    y = (y - HEIGHT/2)/Body.sc * Body.AU

                            
                    for body in bodies:
                        distance_x = body.x  - x
                        distance_y = body.y - y
                        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

                        if distance * Body.SCALE <= body.radius:
                            print(body.sun)
                            body_drag = True
                           

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    body_drag = False

            if event.type == pygame.MOUSEMOTION:
                if body_drag:
                    x, y = pygame.mouse.get_pos()
                    x = (x - WIDTH/2)/Body.sc * Body.AU
                    y = (y - HEIGHT/2)/Body.sc * Body.AU
                    body.x = x
                    body.y = y

        for body in bodies:
            body.update_position(bodies)
            body.check_colision(bodies)
            #body.add_wall_colision()
            body.draw(WIN)

        pygame.display.update()

    pygame.quit()


main()
