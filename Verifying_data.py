#Librairie
import pandas as pd
from Reading_data import Reading_data

#Variable contenant les entêtes pour chaque type de fichier
Header_Field_caracteristic=['Field_name','Localisation','Year_planting','End_field','Slope','Texture','Organic_Carbon','Initial_soil_water','Previous_palm','Terraces']
Header_Year_data=['Year','Yield (tFFB/ha/year)','Understorey_biomass','Legume_fraction','Pruned_frond','Atmospheric_deposition']
Header_Fertilization_data=['Year','Month','Fertilization_type','Quantity','Unit (per ha)','Composition','Placement']
Header_Rainfall_data=['Year','Month','Rainfall(mm)','Rain frequency']



# Appeler la fonction Reading_data
Field_caracteristic, Year_data, Fertilization_data, Rainfall_data = Reading_data()



#Fonction de vérification des fichiers fournit
def File_type(Field_caracteristic,Year_data,Fertilization_data,Rainfall_data):

    #Création de variable récupérant dans une liste les entêtes de chaque fichier donnée par l'utilisateur
    header_field=Field_caracteristic.columns.tolist()
    header_year=Year_data.columns.tolist()
    header_fertilization=Fertilization_data.columns.tolist()
    header_rainfall= Rainfall_data.columns.tolist()

    #Vérification que les entêtes correspondent
    #Caracterististique parcelle
    if header_field != Header_Field_caracteristic:
        diff_field = list(set(header_field) - set(Header_Field_caracteristic))

    #Données annuelles
    if header_year != Header_Field_caracteristic:
        diff_year = list(set(header_year) - set(Header_Year_data))

    #Données fertilisation
    #Données pluviométrie




    return diff_field,diff_year




File_type(Field_caracteristic,Year_data,Fertilization_data,Rainfall_data)

#fonction test: ./Example_File/Year_Field_data_example.csv