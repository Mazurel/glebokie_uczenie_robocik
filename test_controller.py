import pygame
import sys

pygame.init()
pygame.joystick.init()

try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print("Press Ctrl+C to exit.")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                print(f"Axis: {event.axis}, Value: {event.value}")
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Button Pressed: {event.button}")

except KeyboardInterrupt:
    pygame.quit()
    sys.exit()
