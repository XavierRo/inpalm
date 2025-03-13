import pandas as pd

#Fonction pour la lecture des fichiers données par utilisateurs
#Modification pour récupération des infos via interface
def Reading_data():
    try:
        #Récupération et lecture du fichier caractéristique de la parcelle
        Field_caracteristic_input=input("Please indicated the csv file with the field caracteristics\n")
        Field_caracteristic=pd.read_csv(Field_caracteristic_input)

        # Récupération et lecture du fichier données annuelles (couvert, rendement, devenir des élagages...)
        Year_data_input=input("Please indicated the csv file with the years informations \n")
        Year_data= pd.read_csv(Year_data_input)

        # Récupération et lecture du fichier de fertilisation
        Fertilization_data_input=input("Please indicated the csv file with the fertilization informations \n")
        Fertilization_data=pd.read_csv(Fertilization_data_input)


        #Récupération et lecture du fichier pluviométrie
        Rainfall_data_input=input("Please indicated the csv file with the rainfall informations \n")
        Rainfall_data=pd.read_csv(Rainfall_data_input)

    except Exception as error :
        print(f'Error! Please give an csv file : {error}')

Reading_data()