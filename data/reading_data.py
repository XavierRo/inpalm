import pandas as pd
import configparser
#import logging

#utilisation d'un fichier de configuration
fichier_configuration = "inpal.ini"

config = configparser.ConfigParser()
files = ['inpal.ini','../config/inpal.ini', 'D:/Data/git/in-palm/config/inpal.ini']
#lire le nom du fichier dans une variable d'environnement

res = config.read(files)
print(f"config ={config}")
print(f"config.files = {res}")
folder = config['input_data']['folder_data']
print(f"répertoire des données = {folder}")
file_carac = config['input_data']['file_caracterisation']


def reading_file(filename):
    """
    Lecture d'un fichier de données type csv pour charger un dataframe
    :param filename:
    :return: Dataframe correspondant au fichier
    """
    df = None
    try:
        df = pd.read_csv(filename, encoding='UTF-8')
    except Exception as error :
        print(f'Error! Please provide an csv file : {error}')
    return df


#Fonction pour la lecture des fichiers données par utilisateurs
#Modification pour récupération des infos via interface
def reading_data():

    field_caracteristic_file = f"{folder}/{file_carac}"
    year_data_file = f"{folder}/Year_Field_data_example.csv"
    fertilization_data_file = f"{folder}/Fertilization_data_example.csv"
    rainfall_data_file = f"{folder}/Rainfall_data_example.csv"

    field_caracteristic = reading_file(field_caracteristic_file)
    year_data = pd.read_csv(year_data_file)
    fertilization_data = pd.read_csv(fertilization_data_file)
    rainfall_data=pd.read_csv(rainfall_data_file)

    return field_caracteristic,year_data,fertilization_data,rainfall_data

if __name__ == '__main__':
    donnees_entree = reading_data()
    for df in donnees_entree:
        print(df.head(5))
