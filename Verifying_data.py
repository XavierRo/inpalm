#Librairie
import pandas as pd
from Reading_data import Reading_data


#Variable contenant les entêtes pour chaque type de fichier
Header_Field_caracteristic=['Field_name','Localisation','Year_planting','End_field','Slope','Texture','Organic_Carbon','Initial_soil_water','Previous_palm','Terraces']
Header_Year_data=['Year','Yield (tFFB/ha/year)','Understorey_biomass','Legume_fraction','Pruned_frond','Atmospheric_deposition']
Header_Fertilization_data=['Year','Month','Fertilization_type','Quantity','Unit (per ha)','Composition','Placement']
Header_Rainfall_data=['Year','Month','Rainfall(mm)','Rain frequency']

#Variable des listes définit
Texture=["Clay", "Clay loam", "Loam", "Loamy sand", "Sand", "Sandy clay", "Sandy clay loam", "Sandy loam", "Silt", "Silty clay", "Silty clay loam", "Silt loam"]
Previous_palm=[ "No(first cycle)", "Exported", "Shredded left on soil"]
Terraces=["Yes", "No"]
Understorey_biomass=["Very high", "High", "Medium", "Low", "No"]
Legume_fraction = ["Very high", "High", "Medium", "Low", "No"]
Pruned_frond = ["Exported", "In heaps", "In windrows", "Spread(anti erosion)"]
Organic_fertilizer_type = ["EFB", "Compost"]
Organic_fertilizer_Placement = ["In the circle", "In the harvesting path", "Spread(anti erosion)"]
Mineral_Nitrogen_type =["Ammonium Sulfate", "Urea", "Ammonium Chloride", "Ammonium Nitrate", "Sodium Nitrate"]
Mineral_Nitrogen_Placement = ["In the circle buried", "In the circle not buried", "In the circle + windrow", "Evenly distributed"]




# Appeler la fonction Reading_data
Field_caracteristic, Year_data, Fertilization_data, Rainfall_data = Reading_data()



#Fonction de vérification des fichiers fournit par l'utilisateur
def File_type(Field_caracteristic,Year_data,Fertilization_data,Rainfall_data):

    #Création de variable récupérant dans une liste les entêtes de chaque fichier donnée par l'utilisateur
    header_field=Field_caracteristic.columns.tolist()
    header_year=Year_data.columns.tolist()
    header_fertilization=Fertilization_data.columns.tolist()
    header_rainfall= Rainfall_data.columns.tolist()

    #Vérification que les entêtes correspondent
    #Caracterististique parcelle
    if header_field != Header_Field_caracteristic:
        print("Please use the same format as Field_caracteristics_example.csv file.\n"
              "Please modify your file and restart the program ")
        exit()

    #Données annuelles
    if header_year != Header_Year_data:
        print("Please use the same format as Year_Field_data_example.csv file.\n"
              "Please modify your file and restart the program ")
        exit()

    #Données fertilisation
    if header_fertilization != Header_Fertilization_data:
        print("Please use the same format as Fertilization_data_example.csv file.\n"
              "Please modify your file and restart the program ")
        exit()

    #Données pluviométrie
    if header_rainfall != Header_Rainfall_data:
        print("Please use the same format as Rainfall_data_example.csv file.\n"
              "Please modify your file and restart the program ")
        exit()



#Fonction vérification que les données utilisateurs soient bien ceux de la liste définit sortie des tableaux d'erreurs
def Data_type(Field_caracteristic, Year_data, Fertilization_data, Rainfall_data):

    #Création des variables qui contiendront les tableaux erreurs
    Error_field_list_data=[]
    Error_year_list_data = []
    Error_fertilization_list_data = []
    Error_rain_list_data = []

    #Vérification des liste présent dans  Field_caracteristic
    Error_texture=Field_caracteristic[~Field_caracteristic["Texture"].isin(Texture)]
    Error_previous_palm=Field_caracteristic[~Field_caracteristic["Previous_palm"].isin(Previous_palm)]
    Error_terraces=Field_caracteristic[~Field_caracteristic["Terraces"].isin(Terraces)]
    #Ajout des erreurs pour chaque colonne spécifique
    for i, row in Error_texture.iterrows():
        Error_field_list_data.append({'Number column': i+2, 'Title Columns':'Texture','Error Value':row["Texture"]})
    for i, row in Error_previous_palm.iterrows():
        Error_field_list_data.append({'Number column': i + 2, 'Title Columns': 'Previous_palm', 'Error Value': row["Previous_palm"]})
    for i, row in Error_terraces.iterrows():
        Error_field_list_data.append({'Number column': i + 2, 'Title Columns': 'Terraces', 'Error Value': row["Terraces"]})
    #Création du tableau avec les erreurs présent dans le fichier Field-caracteristic
    Error_field_df=pd.DataFrame(Error_field_list_data)

    # Vérification des listes présentes dans Yield data
    Error_understorey_biomass = Year_data[~Year_data["Understorey_biomass"].isin(Understorey_biomass)]
    Error_legume_fraction = Year_data[~Year_data["Legume_fraction"].isin(Legume_fraction)]
    Error_pruned_frond = Year_data[~Year_data["Pruned_frond"].isin(Pruned_frond)]
    # Ajout des erreurs pour chaque colonne spécifique
    for i, row in Error_understorey_biomass.iterrows():
        Error_year_list_data.append({'Number column': i + 2, 'Title Columns': 'Understorey_biomass', 'Error Value': row["Understorey_biomass"]})
    for i, row in Error_legume_fraction.iterrows():
        Error_year_list_data.append({'Number column': i + 2, 'Title Columns': 'Legume_fraction', 'Error Value': row["Legume_fraction"]})
    for i, row in Error_pruned_frond.iterrows():
        Error_year_list_data.append({'Number column': i + 2, 'Title Columns': 'Pruned_frond', 'Error Value': row["Pruned_frond"]})
        # Création du tableau avec les erreurs présent dans le fichier Field-caracteristic
        Error_year_df = pd.DataFrame(Error_year_list_data)

    # Vérification des listes présentes dans Fertilization_data
    for i,row in Fertilization_data.iterrows():
        #Cas de la fertilisation de type minéral
        if row['Fertilization_type']=='Mineral':
            #Ajout si pas dans la liste prédéfinie
            if row['Composition'] not in Mineral_Nitrogen_type:
                Error_year_list_data.append({'Number column': i + 2, 'Title Columns': 'Composition', 'Error Value': row["Composition"]})
            # Vérification du placement minéral
            if row['Placement'] not in Mineral_Nitrogen_Placement:
                Error_year_list_data.append({'Number column': i + 2, 'Title Columns': 'Placement', 'Error Value': row["Placement"]})
        elif row['Fertilization_type'] == 'Organic':
            # Vérification de la composition organique
            if row['Composition'] not in Organic_fertilizer_type:
                Error_year_list_data.append(
                    {'Number column': i + 2, 'Title Columns': 'Composition', 'Error Value': row["Composition"]})
            # Vérification du placement organique
            if row['Placement'] not in Organic_fertilizer_Placement:
                Error_year_list_data.append(
                    {'Number column': i + 2, 'Title Columns': 'Placement', 'Error Value': row["Placement"]})
        else:
            # Si le type de fertilisation est invalide A modifier
            print(f"Invalid Fertilization_type at row {i + 2}. Please verify your Fertilization_type column.")
    # Création du tableau avec les erreurs présent dans le fichier Field-caracteristic
    Error_fertilization_df = pd.DataFrame(Error_year_list_data)
    print(Error_fertilization_df)















    #Vérification des Year_data
    #Index_Year_error.extend(Year_data[~Year_data])


Data_type(Field_caracteristic, Year_data, Fertilization_data, Rainfall_data)

#File_type(Field_caracteristic, Year_data, Fertilization_data, Rainfall_data)

#fonction test: ./Example_File/Year_Field_data_example.csv
#C:\Users\svrignon\Desktop\programme\CSV_data\Essai\Field_caracteristics_example.csv
#./Example_File/Year_Field_data_example.csv
#./Example_File/Fertilization_data_example.csv
#./Example_File/Rainfall_data_example.csv