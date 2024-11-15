import pygame
import numpy as np
import pyaudio
import wave

# Configuration de Pygame
pygame.init()
screen_width = 1000
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Projekt Melody")

# Chargement du fichier audio
filename = "Draft-phone.wav"
wf = wave.open(filename, 'rb')

# Configuration de PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                 channels=wf.getnchannels(),
                 rate=wf.getframerate(),
                 output=True)

# Fonction pour dessiner le spectre
def draw_spectrum(spectrum, max_limits, bar_heights, exceeded):
    screen.fill((0, 0, 0))  # Effacer l'écran
    bar_width = 80  # Largeur des barres
    max_height = screen_height - 50  # Hauteur maximale des barres

    # Identifier les quatre plus hautes valeurs
    indices = np.argsort(spectrum)[-4:]  # Obtenir les indices des 4 plus hautes valeurs
    heights = spectrum[indices]  # Obtenir les hauteurs correspondantes
    
    # Couleurs des barres
    colors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]  # Vert, Jaune, Rouge

    # Dessiner les barres aux positions fixes
    for i, index in enumerate(indices[0:3]):
        # Interpoler la hauteur des barres pour ralentir leur mouvement
        bar_heights[i] += (heights[i] / np.max(spectrum) * (max_height * 1.5) - bar_heights[i]) * 0.2  # 0.1 est le facteur de lissage
        height = int(bar_heights[i])  # Récupérer la hauteur lissée
        x_position = (i + 1) * (screen_width // 5) - (bar_width // 2)  # Position fixe pour chaque barre

        # Vérifier si la barre passe sous la ligne qui la concerne
        if heights[i] < max_limits[i]:
            color = colors[i]  # Prendre la couleur de la ligne
        else:
            color = (0, 255, 0)  # Couleur par défaut (vert)

        pygame.draw.rect(screen, color, (x_position, screen_height - height, bar_width, height))  # Dessiner la barre

        # Vérifier si la barre dépasse la limite
        if height > max_limits[i] and not exceeded[i]:
            print("Limite dépassée pour la barre", i + 1)
            exceeded[i] = True  # Marquer comme dépassé
        elif height <= max_limits[i]:
            exceeded[i] = False  # Réinitialiser si la barre est en dessous de la limite
            print("en dessous")

    # Dessiner les lignes de limite
    pygame.draw.line(screen, (255, 0, 0), (0, max_limits[0]), (screen_width, max_limits[0]), 5)  # Ligne rouge
    pygame.draw.line(screen, (255, 255, 0), (0, max_limits[1]), (screen_width, max_limits[1]), 5)  # Ligne jaune
    pygame.draw.line(screen, (0, 0, 255), (0, max_limits[2]), (screen_width, max_limits[2]), 5)  # Ligne bleue

    pygame.display.flip()

# Lecture de l'audio et affichage du spectre
chunk = 1024  # Taille du bloc audio
data = wf.readframes(chunk)

# Définir la limite maximale
max_limits = [100, 200, 300]  # Limites pour chaque barre
bar_heights = [0, 0, 0]  # Initialiser les hauteurs des barres
exceeded = [False, False, False]  # État de dépassement pour chaque barre

while data:
    stream.write(data)  # Jouer l'audio
    audio_data = np.frombuffer(data, dtype=np.int16)  # Convertir les données audio en tableau NumPy
    spectrum = np.abs(np.fft.rfft(audio_data))  # Calculer le spectre
    spectrum = spectrum[:screen_width // 2]  # Limiter la taille du spectre à la largeur de l'écran
    draw_spectrum(spectrum, max_limits, bar_heights, exceeded)  # Dessiner le spectre

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            data = None  # Quitter la boucle
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Espace pressé !")  # Action à effectuer lorsque la touche espace est pressée

    data = wf.readframes(chunk)  # Lire le prochain bloc de données audio

# Nettoyage
stream.stop_stream()
stream.close()
p.terminate()
wf.close()
