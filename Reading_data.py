import pandas as pd


#Fonction pour la lecture des fichiers données par utilisateurs
#Modification pour récupération des infos via interface
def Reading_data():
    try:
        #Récupération et lecture du fichier caractéristique de la parcelle
        Field_caracteristic_input=input("Please indicated the csv file with the field characteristics\n")
        #Vérification que le fichier soit bien un fichier csv
        while not Field_caracteristic_input.lower().endswith('.csv') :
            print("Error! The file must be a valid CSV file.")
            Field_caracteristic_input = input("Please indicate the csv file with the field characteristics\n")
        #Intégration du fichier dans une variable
        Field_caracteristic=pd.read_csv(Field_caracteristic_input)

        # Récupération et lecture du fichier données annuelles (couvert, rendement, devenir des élagages...)
        Year_data_input=input("Please indicated the csv file with the years informations \n")
        # Vérification que le fichier soit bien un fichier csv
        while not Year_data_input.lower().endswith('.csv'):
            print("Error! The file must be a valid CSV file.")
            Year_data_input = input("Please indicate the csv file with the years informations\n")
        #Intégration du fichier dans une variable
        Year_data= pd.read_csv(Year_data_input)

        # Récupération et lecture du fichier de fertilisation
        Fertilization_data_input=input("Please indicated the csv file with the fertilization informations\n")
        # Vérification que le fichier soit bien un fichier csv
        while not Fertilization_data_input.lower().endswith('.csv'):
            print("Error! The file must be a valid CSV file.")
            Fertilization_data_input = input("Please indicate the csv file with the fertilization informations\n")
        # Intégration du fichier dans une variable
        Fertilization_data=pd.read_csv(Fertilization_data_input)


        #Récupération et lecture du fichier pluviométrie
        Rainfall_data_input=input("Please indicated the csv file with the rainfall informations \n")
        # Vérification que le fichier soit bien un fichier csv
        while not Rainfall_data_input.lower().endswith('.csv'):
            print("Error! The file must be a valid CSV file.")
            Rainfall_data_input = input("Please indicate the csv file with the rainfall informations\n")
        # Intégration du fichier dans une variable
        Rainfall_data=pd.read_csv(Rainfall_data_input)

        return Field_caracteristic, Year_data, Fertilization_data, Rainfall_data

    except Exception as error :
        print(f'Error! Please provide an csv file : {error}')
        return None,None, None, None

#Reading_data()



