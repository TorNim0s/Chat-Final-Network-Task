import sys

import pygame as pg

class GUI:
    def __init__(self, Connector):
        pg.init()

        self.screen = pg.display.set_mode((1080, 720))
        self.users_surface = pg.surface.Surface((280, 500))
        self.chat_surface = pg.surface.Surface((800, 619))
        self.menu_surface = pg.surface.Surface((280, 220))
        self.input_surface = pg.surface.Surface((800, 100))

        self.scroll_users_y = 0
        self.scroll_chat_y = 0

        self.font = pg.font.Font(None, 32)
        self.input_box = pg.Rect(0, 620, 50, 100)

        self.connector = Connector

    def init(self):

        self.menu_surface.fill((30, 30, 30))
        self.chat_surface.fill((30, 30, 30))
        self.users_surface.fill((30, 30, 30))

        y = 60
        f = pg.font.SysFont('', 24)
        header = pg.font.SysFont('', 32)

        for l in self.connector.users:
            self.users_surface.blit(f.render(l, True, (255, 255, 255)), (20, y))
            y += 30

        self.users_surface.blit(header.render("Users", True, (255, 255, 255)), (120, 15))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 50), (280, 50))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 0), (0, 720))
        pg.draw.line(self.users_surface, (255, 255, 255), (280, 0), (280, 720))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 0), (280, 0))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 720), (280, 720))

        # chat surface
        # pg.draw.line(self.chat_surface, (255, 255, 255), (0, 0), (800, 0))
        # pg.draw.line(self.chat_surface, (255, 255, 255), (0, 50), (800, 50))
        # self.chat_surface.blit(header.render("Eldad's And Ilan's Chat Room", True, (255, 255, 255)), (250, 15))

        # menu surface
        pg.draw.line(self.menu_surface, (255, 255, 255), (0, 0), (0, 720))
        pg.draw.line(self.menu_surface, (255, 255, 255), (280, 0), (280, 720))
        pg.draw.line(self.menu_surface, (255, 255, 255), (0, 0), (280, 0))
        pg.draw.line(self.menu_surface, (255, 255, 255), (0, 720), (280, 720))
        self.menu_surface.blit(header.render("Menu", True, (255, 255, 255)), (120, 15))
        pg.draw.line(self.menu_surface, (255, 255, 255), (0, 50), (280, 50))

        # input surface

    def update_users(self , users):
        f = pg.font.SysFont('', 24)
        y = 60
        self.users_surface.fill((30, 30, 30))

        header = pg.font.SysFont('', 32)

        self.users_surface.blit(header.render("Users", True, (255, 255, 255)), (120, 15))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 50), (280, 50))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 0), (0, 720))
        pg.draw.line(self.users_surface, (255, 255, 255), (280, 0), (280, 720))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 0), (280, 0))
        pg.draw.line(self.users_surface, (255, 255, 255), (0, 720), (280, 720))

        for item in users:
            self.users_surface.blit(f.render(item, True, (255, 255, 255)), (20, y))
            y+=30

    def update(self, message):
        f = pg.font.SysFont('', 24)
        y = 0
        self.chat_surface.fill((30, 30, 30))
        for item in self.connector.data:
            self.chat_surface.blit(f.render(item, True, (255, 255, 255)), (20, 20+y))
            y+=30

    def start(self):
        clock = pg.time.Clock()
        color_inactive = pg.Color('lightskyblue3')
        color_active = pg.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        quit = False
        while not quit:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    quit = True
                    pg.quit()
                elif e.type == pg.MOUSEBUTTONDOWN:
                    mouse = pg.mouse.get_pos()
                    rect = self.users_surface.get_rect()
                    rect.x = 800
                    if self.input_box.collidepoint(e.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive

                    if rect.collidepoint(mouse):
                        if e.button == 4:
                            self.scroll_users_y = min(self.scroll_users_y + 15, 0)
                        if e.button == 5:
                            self.scroll_users_y = max(self.scroll_users_y - 15, -300)
                    if self.chat_surface.get_rect().collidepoint(mouse):
                        if e.button == 4:
                            self.scroll_chat_y = min(self.scroll_chat_y + 15, 0)
                        if e.button == 5:
                            self.scroll_chat_y = max(self.scroll_chat_y - 15, -300)

                elif e.type == pg.KEYDOWN:
                    if active:
                        if e.key == pg.K_RETURN:
                            self.connector.send_message(text)
                            print(text)
                            text = ''
                        elif e.key == pg.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += e.unicode

            if quit:
                break

            self.screen.fill((30, 30, 30))
            txt_surface = self.font.render(text, True, pg.Color("white"))
            width = max(800, txt_surface.get_width() + 10)
            self.input_box.w = width
            self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
            pg.draw.rect(self.screen, color, self.input_box, 2)
            self.screen.blit(self.input_surface, (0, 800))

            self.screen.blit(self.chat_surface, (0, self.scroll_chat_y))
            self.screen.blit(self.users_surface, (800, self.scroll_users_y))
            self.screen.blit(self.menu_surface, (800, 500))

            pg.display.flip()
            clock.tick(30)