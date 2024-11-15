import csv
from datetime import datetime
import os
import pandas as pd

class Player:
    def __init__(self,name,score,errors,player_state):
        self.name = name #permet de connaitre le nom du joueur
        self.level = "" #permet de connaitre le niveau auquel il a joué ou il joue
        self.score = score #permet de connaitre son score et de le suivre en temps reel en le recuperant regulierement
        self.errors = errors #permet de connaitre le nombre de fois ou il appuie quand il ne devait pas 
        self.player_state = player_state #permet de savoir s'il est en train de selectionner un niveau, s'il est en jeu, en pause

    def reset(self):
        self.score = 10000
        self.level = ""
        self.errors = 0
        self.player_state = "menu"

    # Fonction pour écrire les données dans un fichier CSV
    def write_to_csv(self,filename, data):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Écrire l'en-tête si le fichier n'existe pas encore
            writer.writerow(data)
        
    def save(self):
        # Écrire les données dans le fichier CSV
        # Obtenez l'heure actuelle
        now = datetime.now()
        # Obtenez le timestamp
        timestamp = now.timestamp()
        # Convertissez le timestamp en un objet datetime
        dt_object = datetime.fromtimestamp(timestamp)
        self.write_to_csv(f'player_data/{self.name}.csv', [self.name,self.level, self.score, self.errors, self.player_state, dt_object])

    def leaderboard(self):
        # Définir les noms des colonnes
        column_names = ['nom', 'level', 'score', 'erreurs', 'etat', 'date']
        # Obtenir le répertoire actuel
        current_directory = os.getcwd()+"/player_data"
        # Créer une liste pour stocker les données
        all_scores = []
        # Définir la valeur de level à filtrer
        level_to_filter = self.level  # Remplacez 'votre_niveau' par le niveau que vous souhaitez filtrer
        # Parcourir tous les fichiers dans le répertoire actuel
        for filename in os.listdir(current_directory):
            # Vérifier si le fichier a une extension .csv
            if filename.endswith('.csv'):
                # Créer le chemin complet du fichier
                file_path = os.path.join(current_directory, filename)
                # Lire le fichier CSV avec pandas sans en-tête
                try:
                    df = pd.read_csv(file_path, header=None, names=column_names)
                    # Filtrer les lignes où 'etat' est 'won' et 'level' correspond à level_to_filter
                    filtered_df = df[(df['etat'] == 'won') & (df['level'] == level_to_filter)]
                    # Ajouter les scores et les noms à la liste
                    all_scores.extend(filtered_df[['nom', 'score']].to_dict(orient='records'))
                except Exception as e:
                    print(f"Erreur lors de la lecture de {filename}: {e}")
        # Convertir la liste en DataFrame
        scores_df = pd.DataFrame(all_scores)
        # Trier par score de manière décroissante et récupérer les trois premiers
        top_scores = scores_df.sort_values(by='score', ascending=False).head(3)
        # Afficher les résultats
        print(f"Les trois premiers scores avec leurs noms correspondants (état 'won' et level '{level_to_filter}') :")
        print(top_scores)
        print(all_scores)
        return top_scores