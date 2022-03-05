import sys

import pygame as pg
from LoginGUI import Button
from tkinter import Tk
from tkinter import filedialog

class GUI:
    def __init__(self, Connector):
        # self.message = Button('Direct Message', 70, 75, 150, 30, addX=800, addY=500)
        # self.upload = Button('Upload File', 70, 125, 150, 30, addX=800, addY=500)
        # self.download = Button('Download File', 70, 175, 150, 30, addX=800, addY=500)

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
        self.menu_surface.blit(header.render("List of Commands", True, (255, 255, 255)), (45, 15))
        self.menu_surface.blit(f.render("/pm - private message", True, (255, 255, 255)), (10, 60))
        self.menu_surface.blit(f.render("/upload - upload file", True, (255, 255, 255)), (10, 80))
        self.menu_surface.blit(f.render("/download - download file", True, (255, 255, 255)), (10, 100))
        self.menu_surface.blit(f.render("/files - available files", True, (255, 255, 255)), (10, 120))
        self.menu_surface.blit(f.render("/stop - stop download", True, (255, 255, 255)), (10, 140))
        self.menu_surface.blit(f.render("/resume - resume download", True, (255, 255, 255)), (10, 160))

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
            y += 30

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
                # self.message.handle_event(e)
                # self.upload.handle_event(e)
                # self.download.handle_event(e)

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
                        if e.key == pg.K_RETURN or e.unicode == '\r':
                            split = text.split(' ')
                            print(split)
                            if split[0] == '/pm':
                                self.connector.send_private_message(' '.join(split[2:]), split[1])
                            elif split[0] == '/upload':
                                if len(split) != 3:
                                    self.connector.recieve_message('Wrong number of arguments, use /upload '
                                                                   '<file_save_name> <file_name>')
                                    # Tk().withdraw()
                                    # file_path = filedialog.askopenfilename()  # need to split and take file name
                                    # print(file_path)
                                else:
                                    data = f"{split[1]}"
                                    self.connector.send_file(data, split[2])
                            elif split[0] == '/download':
                                if len(split) != 2:
                                    self.connector.recieve_message('Wrong number of arguments, use /download '
                                                                   '<file_name>')
                                else:
                                    data = f"{split[1]}"
                                    self.connector.download_file(data)
                            elif split[0] == '/files':
                                if len(split) != 2:
                                    self.connector.recieve_message('Wrong number of arguments, use /files '
                                                                   '<starting_number>')
                                else:
                                    data = f"{split[1]}"
                                    self.connector.get_files(data)
                            elif split[0] == "/resume":
                                if(len(split) != 1):
                                    self.connector.recieve_message('Wrong number of arguments, use /resume ')
                                else:
                                    self.connector.client.udp_reliable_connection.send_resume()
                            else:
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

            # self.message.update()
            # self.message.draw(self.menu_surface)
            # self.upload.update()
            # self.upload.draw(self.menu_surface)
            # self.download.update()
            # self.download.draw(self.menu_surface)

            pg.display.flip()
            clock.tick(30)
