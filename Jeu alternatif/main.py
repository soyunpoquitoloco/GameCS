import pygame
import numpy as np
import pyaudio
import wave
from PIL import Image
import serial
from datetime import datetime
from Player import Player
import time

# Configuration de Pygame
pygame.init()
screen_width = 1000
screen_height = 800
#Nom de la page et dimension
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Projekt Melody")

#Importer l'image de game over
gomort = pygame.image.load("assets/mort.png")
gomort = pygame.transform.scale(gomort,(800,431))
#Importer le tuto
before = pygame.image.load("assets/Before.png")
before = pygame.transform.scale(before,(800,431))
after = pygame.image.load("assets/After.png")
after = pygame.transform.scale(after,(800,431))
#importer et charger le bouton start
bouton_lancement = pygame.image.load("assets/Start.png")
bouton_lancement = pygame.transform.scale(bouton_lancement,(350,350))
bouton_lancement_rect = bouton_lancement.get_rect()
bouton_lancement_rect.x = 320
bouton_lancement_rect.y = 550
#importer et charger les boutons de sélection de level
lvl_Prodigy = pygame.image.load("assets/Prodigy.png")
lvl_Prodigy = pygame.transform.scale(lvl_Prodigy,(600,100))
lvl_Prodigy_rect = lvl_Prodigy.get_rect()
lvl_Prodigy_rect.x = 0
lvl_Prodigy_rect.y = 100
lvl_Daft = pygame.image.load("assets/Daft Punk.png")
lvl_Daft = pygame.transform.scale(lvl_Daft,(600,100))
lvl_Daft_rect = lvl_Daft.get_rect()
lvl_Daft_rect.x = 0
lvl_Daft_rect.y = 250
#Importer le back button
back = pygame.image.load("assets/back.png")
back = pygame.transform.scale(back,(400,231))
back_rect = back.get_rect()
back_rect.x = 700
back_rect.y = 600
#importer et charger la bannière
banner = pygame.image.load("assets/Banner.png")
banner = pygame.transform.scale(banner,(500,800))

# Fonction pour charger le GIF du background
def load_gif(filename):
    with Image.open(filename) as img:
        frames = []
        try:
            while True:
                # Convertir chaque image en surface Pygame
                img_frame = img.convert("RGBA")
                img_frame = img_frame.resize((600,600))  # Redimensionner l'image
                frame = pygame.image.fromstring(img_frame.tobytes(), img_frame.size, img_frame.mode)
                frames.append(frame)
                img.seek(len(frames))  # Passer à l'image suivante
        except EOFError:
            pass  # Fin des images
    return frames
# Charger le GIF
gif_frames = load_gif("assets/bg.gif")  # Remplacez par le chemin de votre GIF
frame_count = len(gif_frames)
current_frame = 0
frame_rate = 100  # Temps entre les frames en millisecondes
last_update = pygame.time.get_ticks()

pygame.mixer.init()
# Charger les sons
click_sound = pygame.mixer.Sound("lvlup.wav")
menu_sound = pygame.mixer.Sound("Insomnia.wav")

# Initialiser la police
pygame.font.init()
font = pygame.font.Font(None, 36)

# Fonction pour dessiner le spectre
def draw_spectrum(spectrum, bar_heights):
    screen.fill((0, 0, 0))  # L'écran est noir
    bar_width = 80  # Largeur des barres
    max_height = screen_height - 50  # Hauteur maximale des barres
    click = [False, False, False]
    # Identifier les quatre plus hautes valeurs
    indices = np.argsort(spectrum)[-4:]  # Obtenir les indices des 4 plus hautes valeurs
    heights = spectrum[indices]  # Obtenir les hauteurs correspondantes

    # Couleurs des barres
    colors = [(0, 0, 255), (255, 255, 0), (255, 0, 0)]  # Bleu, Jaune, Rouge

    # Dessiner les barres aux positions fixes
    for i in range (0,3) :
        # Interpoler la hauteur des barres pour ralentir leur mouvement
        bar_heights[i] += (heights[i] / np.max(spectrum) * (max_height * 1.5) - bar_heights[i]) * 0.1  # 0.1 est le facteur de lissage
        bar_heights[i] = np.nan_to_num(bar_heights[i])
        height = int(bar_heights[i])  # Récupérer la hauteur lissée
        x_position = (i + 1) * (screen_width // 5) - (bar_width // 2)  # Position fixe pour chaque barre
        # Vérifier si la barre passe sous la ligne qui la concerne

        if height > height_max[i] :
            click[i] = True
            color = (0, 255, 0)  # Couleur par défaut (vert)
        else:
            color = colors[i]  # Prendre la couleur de la ligne
        
        pygame.draw.rect(screen, color, (x_position, screen_height - height, bar_width, height))  # Dessiner la barre

    # Dessiner les lignes de limite
    pygame.draw.line(screen, (255, 0, 0), ((2 + 1) * (screen_width // 5) - (bar_width // 2), screen_height - height_max[2]), (screen_width, screen_height - height_max[2]), 5)  # Ligne rouge
    pygame.draw.line(screen, (255, 255, 0), ((1 + 1) * (screen_width // 5) - (bar_width // 2), screen_height - height_max[1]), (screen_width, screen_height - height_max[1]), 5)  # Ligne jaune
    pygame.draw.line(screen, (0, 0, 255), ((0 + 1) * (screen_width // 5) - (bar_width // 2), screen_height - height_max[0]), (screen_width, screen_height - height_max[0]), 5)  # Ligne bleue

    return click

up = False
right = False
left = False
line = ""
def read_serial(ser,up,right,left,click,line):#on essaie de détecter le maintien de pression des touches avec des variables booléennes pour maintenir un état
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
    if click[1] and line=="UP":
        player.score += 100
        print("augmente")
    elif click[1] == False and line=="Key released: U":
        player.score -= 100
        player.errors += 1
        print("diminue")
    elif click[2] and line=="RIGHT":
        player.score += 100
        print("augmente")
    elif click[2] == False and line=="Key released: A":
        player.score -= 100
        player.errors += 1
        print("diminue")
    elif click[0] and line=="LEFT":
        player.score += 100
        print("augmente")
    elif click[0] == False and line=="Key released: B":
        player.score -= 100
        player.errors += 1
        print("diminue")
        

#Variable de jeu
tuto = False
score = 10000
errors = 0
score_max = 10000
player_name = ""
mort = False
loop_music = True
menu = 0
game = False #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
running = True
pause = False
# Configuration de la connexion série
ser = serial.Serial('COM8', 115200, timeout=1)
while running == True:
    if tuto:
        screen.fill((0,0,0))
        # Afficher le texte demandant le nom du joueur
        prompt_text = font.render("Entrez le nom du joueur:", True, (255, 255, 255))
        screen.blit(prompt_text, (350, 500))
        # Afficher le nom du joueur saisi
        name_text = font.render(player_name, True, (255, 255, 255))
        screen.blit(name_text, (400, 540))
        pygame.display.flip()
        # Instancier un objet de la classe Player
        player = Player(name=player_name, score = score, errors = errors, player_state="menu")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Appuyer sur Entrée pour valider le nom
                    screen.fill((0,0,0))
                    screen.blit(before,(100,150))
                    prompt_text = font.render("Ici les barres sont sous leur limite, tout va bien", True, (255, 255, 255))
                    screen.blit(prompt_text, (100, 50))
                    pygame.display.flip()
                    pygame.time.delay(5000)
                    screen.fill((0,0,0))
                    screen.blit(after,(100,150))
                    prompt_text = font.render("Ici les barres dépassent leur limite, il faut utiliser les flèches <- | ->", True, (255, 255, 255))
                    screen.blit(prompt_text, (100, 50))
                    prompt_text = font.render("pour scorer des points", True, (255, 255, 255))
                    screen.blit(prompt_text, (100, 70))
                    pygame.display.flip()
                    pygame.time.delay(5000)
                    menu = 1
                    tuto = False
                elif event.key == pygame.K_BACKSPACE:  # Gérer la touche Retour arrière
                    player_name = player_name[:-1]  # Supprimer le dernier caractère
                else:
                    player_name += event.unicode  # Ajouter le caractère saisi
    if mort:
        # Afficher le texte demandant le nom du joueur
        prompt_text = font.render("Appuyez sur enter", True, (255, 255, 255))
        screen.blit(prompt_text, (350, 500))
        screen.blit(gomort, (100,150))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Appuyer sur Entrée pour valider le nom
                    player.save() #On sauvegarde les variables du joueur
                    leaderboard = player.leaderboard()
                    screen.fill((0,0,0))
                    title = font.render('Leaderboard', True, (255,255,255))
                    screen.blit(title, (350, 500 - 36 * 2))
                    for index, entry in enumerate(leaderboard.itertuples(index=False)):
                        text = font.render(f'{index + 1}. {entry.nom} - {entry.score}', True, (255,255,255))
                        screen.blit(text, (350, 500 + 36 * index))
                    pygame.display.flip()
                    pygame.time.delay(5000)
                    mort = False
                    menu = 1
                    menu_sound.play() #On joue la musique du menu
                    player.reset() #on reset les variables du joueur
        
    
    elif game == True:
        wf = wave.open(filename, 'rb')
                # Configuration de PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Lecture de l'audio et affichage du spectre
        chunk = 1024  # Taille du bloc audio
        data = wf.readframes(chunk)

        # Définir la limite maximale
        height_max = [450,550,750]
        bar_heights = [0, 0, 0]  # Initialiser les hauteurs des barres

        while data and mort == False: #Boucle de niveau
            if pause == False:
                stream.write(data)  # Jouer l'audio
                audio_data = np.frombuffer(data, dtype=np.int16)  # Convertir les données audio en tableau NumPy
                spectrum = np.abs(np.fft.rfft(audio_data))  # Calculer le spectre
                spectrum = spectrum[:screen_width // 2]  # Limiter la taille du spectre à la largeur de l'écran
                click = draw_spectrum(spectrum, bar_heights)  # Dessiner le spectre

                # Rendre le score en texte
                score_text = font.render(f"Score: {player.score}", True, (0, 255, 0))  # Texte blanc
                screen.blit(score_text, (10, 10))
                #Mettre à jour l'écran
                pygame.display.flip()
                # Gestion des événements
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        data = None  # Quitter la boucle
                        pygame.quit()
                    if event.type == pygame.KEYDOWN:  # Vérifier si une touche est pressée
                        if event.key == pygame.K_p: 
                            screen.fill((0,0,0))
                            pause_text = font.render("Pause", True, (255, 255, 255))  # Texte blanc
                            screen.blit(pause_text, (480, 380))
                            pygame.display.flip()
                            pause = True
                            player.player_state = "pause"
                            player.save() #On sauvegarde la donnée des variables pour savoir quand était la pause
                # Vérifier l'état des touches
                keys = pygame.key.get_pressed()
                # Si la touche UP est maintenue
                if keys[pygame.K_UP]:
                    if click[1]:
                        player.score += 100
                    else:
                        player.score -= 100
                        player.errors += 1
                # Si la touche LEFT est maintenue
                if keys[pygame.K_LEFT]:
                    if click[0]:
                        player.score += 100
                    else:
                        player.score -= 100
                        player.errors += 1
                # Si la touche RIGHT est maintenue
                if keys[pygame.K_RIGHT]:
                    if click[2]:
                        player.score += 100 
                    else:
                        player.score -= 100
                        player.errors += 1

                read_serial(ser,up,right,left,click,line)
                data = wf.readframes(chunk)  # Lire le prochain bloc de données audio
                player.player_state = "in level"
                if player.score < 0:
                    mort = True
                    game = False
                    print("mort")
                    player.player_state = "lost"
                player.save() #On sauvegarde la donnée des variables dans le csv dans la boucle de jeu
            else:
                screen.fill((0,0,0))
                pause_text = font.render("Pause", True, (255, 255, 255))  # Texte blanc
                screen.blit(pause_text, (480, 380))
                pygame.display.flip()
                # Gestion des événements
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        data = None  # Quitter la boucle
                        pygame.quit()
                    if event.type == pygame.KEYDOWN:  # Vérifier si une touche est pressée
                        if event.key == pygame.K_p: 
                            pause = False
        # Nettoyage
        mort = True
        game = False
        print("fin de partie")
        player.player_state = "won"
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
    
    
    
    elif menu == 0: 
        if loop_music:
            loop_music = False
            menu_sound.play()
        # Gérer l'animation
        now = pygame.time.get_ticks()
        if now - last_update > frame_rate:
            current_frame = (current_frame + 1) % frame_count
            last_update = now
        # Remplir l'écran avec une couleur
        screen.fill((0, 0, 0))  #Noir
        # Afficher le cadre actuel du GIF
        screen.blit(gif_frames[current_frame], (200, 100))
        #Appliquer le background du menu
        screen.blit(banner, (250,0))
        screen.blit(bouton_lancement, bouton_lancement_rect)
        #Mettre à jour l'écran
        pygame.display.flip()
    
    
    
    elif menu == 1:
        #Gérer l'animation
        now = pygame.time.get_ticks()
        if now - last_update > frame_rate:
            current_frame = (current_frame + 1) % frame_count
            last_update = now
        # Remplir l'écran avec une couleur
        screen.fill((0, 0, 0))  #Noir
        # Afficher le cadre actuel du GIF
        screen.blit(gif_frames[current_frame], (200, 100))
        screen.blit(back, back_rect)
        screen.blit(lvl_Prodigy, lvl_Prodigy_rect)
        screen.blit(lvl_Daft, lvl_Daft_rect)
        #Mettre à jour l'écran
        pygame.display.flip()
    
    
    
    # si le joueur ferme la fenetre
    for event in pygame.event.get():
        # vérifier que l'event ferme la fenetre
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Fermeture du jeu")
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #Vérification de si la souris est en collision avec le bouton de lancement
            if bouton_lancement_rect.collidepoint(event.pos):
                #Mettre le jeu en mode lancé
                print("menu2")
                click_sound.play()
                tuto = True
                menu = 2
            elif lvl_Prodigy_rect.collidepoint(event.pos):
                #Mettre le jeu en mode lancé car niveau sélectionné
                print("lvlProdigy")
                click_sound.play()
                menu_sound.stop()
                game = True
                filename = "The Prodigy Beyondthedeathray.wav"
                player.level = filename
                player.player_state = "select lvl"
                player.save()
            elif lvl_Daft_rect.collidepoint(event.pos):
                #Mettre le jeu en mode lancé car niveau sélectionné
                print("lvlDaft")
                click_sound.play()
                menu_sound.stop()
                game = True
                filename = "Daft Punk Beyond.wav"
                player.level = filename
                player.player_state = "select lvl"
                player.save()
            elif back_rect.collidepoint(event.pos):
                #Mettre le jeu en mode lancé
                print("back")
                click_sound.play()
                menu = 0


