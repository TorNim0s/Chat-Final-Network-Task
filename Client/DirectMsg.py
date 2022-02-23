import pygame as pg

from LoginGUI import InputBox
from LoginGUI import Button

class DirectMsg:
    def __init__(self, connector=None):
        # self.connector = connector
        pg.init()
        self.screen = pg.display.set_mode((400, 200))
        self.done = False
        self.screen.fill((30, 30, 30))
        self.input_surface1 = pg.surface.Surface((175, 30))
        self.input_surface2 = pg.surface.Surface((300, 100))

        self.header = pg.font.SysFont('', 28)
        self.screen.blit(self.header.render("Send Direct Message", True, (255, 255, 255)), (20, 15))
        self.screen.blit(self.header.render("To: ", True, (255, 255, 255)), (20, 53))

        self.input_box1 = InputBox(0, 0, 175, 30, surface=self.input_surface1, addX=100, addY=50)
        self.input_box2 = InputBox(0, 0, 300, 100, surface=self.input_surface2, addY=100)

    def init(self):
        clock = pg.time.Clock()
        input_boxes = [self.input_box1, self.input_box2]
        send = Button('Send', 315, 115, 75, 75, direct=self)

        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                    pg.quit()

                for box in input_boxes:
                    box.handle_event(event)
                send.handle_event(event)

            if self.done:
                break

            self.input_surface1.fill((30, 30, 30))
            self.input_surface2.fill((30, 30, 30))

            for box in input_boxes:
                box.draw()

            send.update()
            send.draw(self.screen)

            self.screen.blit(self.input_surface1, (100, 50))
            self.screen.blit(self.input_surface2, (0, 100))

            pg.display.flip()
            clock.tick(30)


if __name__ == '__main__':
    msg = DirectMsg()
    msg.init()
