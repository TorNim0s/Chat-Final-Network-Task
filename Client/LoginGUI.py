import pygame as pg


class InputBox:

    def __init__(self, x, y, w, h, text='', surface=None):
        self.COLOR_INACTIVE = pg.Color('lightskyblue3')
        self.COLOR_ACTIVE = pg.Color('dodgerblue2')
        self.FONT = pg.font.Font(None, 32)
        self.rect = pg.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.surface = surface

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            temp = self.rect.copy()
            temp.y += 50
            temp.x += 100
            if temp.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        self.rect.w = 175

    def draw(self):
        # Blit the text.
        self.surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(self.surface, self.color, self.rect, 2)


class Button:

    def __init__(self, text, x=0, y=0, width=100, height=50, command=None, login=None):
        self.login = login
        self.text = text
        self.command = command

        self.image_normal = pg.Surface((width, height))
        self.image_normal.fill((255, 255, 255))

        self.image_hovered = pg.Surface((width, height))
        self.image_hovered.fill((0, 255, 0))

        self.image = self.image_normal
        self.rect = self.image.get_rect()

        font = pg.font.Font('freesansbold.ttf', 15)

        text_image = font.render(text, True, (0, 0, 0))
        text_rect = text_image.get_rect(center=self.rect.center)

        self.image_normal.blit(text_image, text_rect)
        self.image_hovered.blit(text_image, text_rect)

        # you can't use it before `blit`
        self.rect.topleft = (x, y)
        self.hovered = False

    def update(self):

        if self.hovered:
            self.image = self.image_hovered
        else:
            self.image = self.image_normal

    def draw(self, surface):

        surface.blit(self.image, self.rect)

    def handle_event(self, event):

        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.hovered:
                self.login.connector.set_client_info(self.login.input_box1.text, self.login.input_box2.text,
                                                     self.login.input_box3.text)
                self.login.done = True


class LoginGUI:
    def __init__(self, connector):
        self.connector = connector
        pg.init()
        self.screen = pg.display.set_mode((300, 250))
        self.done = False
        self.screen.fill((30, 30, 30))
        self.input_surface = pg.surface.Surface((175, 135))

        header = pg.font.SysFont('', 28)
        self.screen.blit(header.render("Welcome to our Chat Room", True, (255, 255, 255)), (20, 15))
        self.screen.blit(header.render("Name: ", True, (255, 255, 255)), (20, 53))
        self.screen.blit(header.render("IP: ", True, (255, 255, 255)), (20, 103))
        self.screen.blit(header.render("Port: ", True, (255, 255, 255)), (20, 153))

        self.input_box1 = InputBox(0, 0, 175, 30, surface=self.input_surface)
        self.input_box2 = InputBox(0, 50, 175, 30, surface=self.input_surface)
        self.input_box3 = InputBox(0, 100, 175, 30, surface=self.input_surface)

    def init(self):
        clock = pg.time.Clock()
        input_boxes = [self.input_box1, self.input_box2, self.input_box3]
        button = Button('Login', 75, 200, 150, 30, login=self)

        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True
                for box in input_boxes:
                    box.handle_event(event)
                button.handle_event(event)

            for box in input_boxes:
                box.update()

            self.input_surface.fill((30, 30, 30))

            for box in input_boxes:
                box.draw()

            button.update()
            button.draw(self.screen)
            self.screen.blit(self.input_surface, (100, 50))
            pg.display.flip()
            clock.tick(30)
