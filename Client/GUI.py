import pygame as pg

pg.init()

users = ["Eldad", "Ilan", "Shlomi", "Yael", "Yehuda"]

screen = pg.display.set_mode((1080, 720))
users_surface = pg.surface.Surface((280, 500))
chat_surface = pg.surface.Surface((800, 619))
menu_surface = pg.surface.Surface((280, 220))
input_surface = pg.surface.Surface((800, 100))

font = pg.font.Font(None, 32)
input_box = pg.Rect(0, 620, 50, 100)
color_inactive = pg.Color('lightskyblue3')
color_active = pg.Color('dodgerblue2')
color = color_inactive
active = False
text = ''

menu_surface.fill((30, 30, 30))
chat_surface.fill((30, 30, 30))
users_surface.fill((30, 30, 30))

# i_a = users_surface.get_rect()
# x1 = i_a[0]
# x2 = x1 + i_a[2]
# a, b = (255, 0, 0), (60, 255, 120)
# y1 = i_a[1]
# y2 = y1 + i_a[3]
# h = y2-y1
# rate = (float((b[0]-a[0])/h),
#          (float(b[1]-a[1])/h),
#          (float(b[2]-a[2])/h)
#          )
# for line in range(y1,y2):
#      color = (min(max(a[0]+(rate[0]*line),0),255),
#               min(max(a[1]+(rate[1]*line),0),255),
#               min(max(a[2]+(rate[2]*line),0),255)
#               )
#      pygame.draw.line(users_surface, color, (x1, line),(x2, line))

y = 60
f = pg.font.SysFont('', 24)
header = pg.font.SysFont('', 32)
for l in users:
    users_surface.blit(f.render(l, True, (255, 255, 255)), (20, y))
    y += 30

users_surface.blit(header.render("Users", True, (255, 255, 255)), (120, 15))
pg.draw.line(users_surface, (255, 255, 255), (0, 50), (280, 50))
pg.draw.line(users_surface, (255, 255, 255), (0, 0), (0, 720))
pg.draw.line(users_surface, (255, 255, 255), (280, 0), (280, 720))
pg.draw.line(users_surface, (255, 255, 255), (0, 0), (280, 0))
pg.draw.line(users_surface, (255, 255, 255), (0, 720), (280, 720))

# chat surface
pg.draw.line(chat_surface, (255, 255, 255), (0, 0), (800, 0))
pg.draw.line(chat_surface, (255, 255, 255), (0, 50), (800, 50))
chat_surface.blit(header.render("Eldad's And Ilan's Chat Room", True, (255, 255, 255)), (250, 15))

# menu surface
pg.draw.line(menu_surface, (255, 255, 255), (0, 0), (0, 720))
pg.draw.line(menu_surface, (255, 255, 255), (280, 0), (280, 720))
pg.draw.line(menu_surface, (255, 255, 255), (0, 0), (280, 0))
pg.draw.line(menu_surface, (255, 255, 255), (0, 720), (280, 720))
menu_surface.blit(header.render("Menu", True, (255, 255, 255)), (120, 15))
pg.draw.line(menu_surface, (255, 255, 255), (0, 50), (280, 50))

# input surface


clock = pg.time.Clock()
quit = False

scroll_users_y = 0
scroll_chat_y = 0

while not quit:
    quit = pg.event.get(pg.QUIT)
    for e in pg.event.get():
        if e.type == pg.MOUSEBUTTONDOWN:
            mouse = pg.mouse.get_pos()
            rect = users_surface.get_rect()
            rect.x = 800
            if input_box.collidepoint(e.pos):
                # Toggle the active variable.
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive

            if rect.collidepoint(mouse):
                if e.button == 4:
                    scroll_users_y = min(scroll_users_y + 15, 0)
                if e.button == 5:
                    scroll_users_y = max(scroll_users_y - 15, -300)
            if chat_surface.get_rect().collidepoint(mouse):
                if e.button == 4:
                    scroll_chat_y = min(scroll_chat_y + 15, 0)
                if e.button == 5:
                    scroll_chat_y = max(scroll_chat_y - 15, -300)

        if e.type == pg.KEYDOWN:
            if active:
                if e.key == pg.K_RETURN:
                    print(text)
                    text = ''
                elif e.key == pg.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += e.unicode

    screen.fill((30, 30, 30))
    txt_surface = font.render(text, True, pg.Color("white"))
    width = max(800, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pg.draw.rect(screen, color, input_box, 2)
    screen.blit(input_surface, (0, 800))

    screen.blit(chat_surface, (0, scroll_chat_y))
    screen.blit(users_surface, (800, scroll_users_y))
    screen.blit(menu_surface, (800, 500))

    pg.display.flip()
    clock.tick(30)
