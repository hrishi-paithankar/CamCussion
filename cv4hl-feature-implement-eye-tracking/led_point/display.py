import pygame
from led_point.trajectory import Trajectory
from led_point.point import Point
import ctypes

class Display:
    def __init__(self, point_speed = 1):
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.width, self.height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        pygame.init()

        self.point_radius = 30
        self.window = pygame.display.set_mode((self.width, self.height))
        self.window.fill((149, 199, 206))
        self.trajectory = Trajectory(Point(self.width, self.height), point_speed, 2*self.point_radius)

    def draw_point(self, position):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        self.window.fill((149, 199, 206))
        pygame.draw.circle(self.window, (255, 0, 0), (position.x, position.y), self.point_radius)
        pygame.display.flip()

    def run(self):
        """running = True
        while running:"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        self.trajectory.move_point()
        position = self.get_current_position()

        self.window.fill((149, 199, 206))
        pygame.draw.circle(self.window, (255, 0, 0), (position.x, position.y), self.point_radius)
        pygame.display.flip()

    def central_point(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        position = Point(self.width // 2, self.height // 2)
        self.window.fill((149, 199, 206))
        pygame.draw.circle(self.window, (255, 0, 0), (position.x, position.y), self.point_radius)
        pygame.display.flip()

    def wait_processing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # The function displays a message that the user has to wait for the data processing to complete
        self.window.fill((149, 199, 206))
        font = pygame.font.Font(None, 36)
        text = font.render("Please wait for data processing to be completed", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.window.blit(text, text_rect)
        pygame.display.flip()
    
    def quit(self):
        pygame.quit()

    def get_current_position(self):
        return self.trajectory.get_current_position()

# Usage
if __name__ == "__main__":
    display = Display()
    display.run()