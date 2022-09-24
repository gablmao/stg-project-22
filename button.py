import pygame

#create button
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False

    #draws image of button and check for mouse position and interaction
    def drawB(self, surface):
        action = False
        pos = pygame.mouse.get_pos()  #mouse position
        

        if self.rect.collidepoint(pos):  #mouse hovers over image/button
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))  #draws button

        #print(pos)
        return action
        