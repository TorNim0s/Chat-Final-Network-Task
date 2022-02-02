import pygame

pygame.init()

users = ["Eldad", "Ilan", "Shlomi", "Yael", "Yehuda"]

screen = pygame.display.set_mode((1080, 720))
users_surface = pygame.surface.Surface((280, 500))
chat_surface = pygame.surface.Surface((800, 720))
menu_surface = pygame.surface.Surface((280, 220))

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
f = pygame.font.SysFont('', 24)
header = pygame.font.SysFont('', 32)
for l in users:
    users_surface.blit(f.render(l, True, (255, 255, 255)), (20, y))
    y += 30

users_surface.blit(header.render("Users", True, (255, 255, 255)), (120, 15))
pygame.draw.line(users_surface, (255,255,255), (0, 50),(280, 50))

pygame.draw.line(users_surface, (255,255,255), (0, 0),(0, 720))
pygame.draw.line(users_surface, (255,255,255), (280, 0),(280, 720))
pygame.draw.line(users_surface, (255,255,255), (0, 0),(280, 0))
pygame.draw.line(users_surface, (255,255,255), (0, 720),(280, 720))


# chat surface
pygame.draw.line(chat_surface, (255,255,255), (0, 0),(800, 0))
pygame.draw.line(chat_surface, (255,255,255), (0, 50),(800, 50))
chat_surface.blit(header.render("Eldad's And Ilan's Chat Room", True, (255, 255, 255)), (250, 15))

# menu surface
pygame.draw.line(menu_surface, (255,255,255), (0, 0),(0, 720))
pygame.draw.line(menu_surface, (255,255,255), (280, 0),(280, 720))
pygame.draw.line(menu_surface, (255,255,255), (0, 0),(280, 0))
pygame.draw.line(menu_surface, (255,255,255), (0, 720),(280, 720))

menu_surface.blit(header.render("Menu", True, (255, 255, 255)), (120, 15))
pygame.draw.line(menu_surface, (255,255,255), (0, 50),(280, 50))


clock = pygame.time.Clock()
quit = False

scroll_users_y = 0
scroll_chat_y = 0

while not quit:
    quit = pygame.event.get(pygame.QUIT)
    for e in pygame.event.get():
        if e.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            rect = users_surface.get_rect()
            rect.x = 800
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

    screen.blit(chat_surface, (0, scroll_chat_y))
    screen.blit(users_surface, (800, scroll_users_y))
    screen.blit(menu_surface, (800, 500))
    pygame.display.flip()
    clock.tick(60)