import pygame
import math
pygame.init()

WIDTH, HEIGHT =  800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("body Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)

class Body:
    # Astronomical Unity
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    sc = 250
    SCALE = sc / AU 
    TIMESTEP = 3600 * 12 # 1 day in second

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

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

        pygame.draw.circle(win, self.color, (x, y), self.radius)
        
        if not self.sun:
            distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)}km", 1, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

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

    def check_colision(self, bodies):
        for body in bodies:
            if self == body:
                continue

            distance_x = body.x - self.x
            distance_y = body.y - self.y
            distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
            if distance * Body.SCALE <= body.radius + self.radius:
                bodies.remove(body)
        
    def merge_body(self, body):
        pass


def main():
    run = True
    clock = pygame.time.Clock()

    

    venus = Body(0.723 * Body.AU, 0, 14, WHITE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000

    bodies = []

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

                

    
                

        for body in bodies:
            body.update_position(bodies)
            body.check_colision(bodies)
            body.draw(WIN)

        pygame.display.update()

    pygame.quit()


main()