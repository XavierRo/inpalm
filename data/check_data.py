#Librairie
import pandas as pd
from exception.InPalmException import InPalmException
from exception import InPalmException

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
#Liste mois pour vérification
Month_data = ["January","February","March","April","May","June","July","August","September","November","December"]


def file_type_verification(dataframe, heardlist):
    """
    Méthode de verification des headers
    :param dataframe: dataframe
    :param heardlist: listes des noms de colonnes attendu
    :param error_message:
    :return:
    """
    #Vérification que les entêtes correspondent
    #Caracterististique parcelle
    if dataframe.columns.tolist() != heardlist:
        error_message = f"Les entetes doivent être {heardlist}"
        print(error_message)
        raise InPalmException(error_message)
    else:
        print(f"les entetes du dataframe \n {dataframe.head(5)} \n sont ok")


#Fonction vérification que les données utilisateurs soient bien ceux de la liste définit sortie des tableaux d'erreurs
def data_type(Field_caracteristic, Year_data, Fertilization_data,Rainfall_data):

    #Création des variables qui contiendront types d'erreurs
    Error_field_list_data=[]
    Error_year_list_data = []
    Error_fertilization_list_data = []
    Error_rain_list_data=[]

    #Création des variables qui contiendront les tableaux d'erreurs
    Error_field_df=[]
    Error_year_df=[]
    Error_fertilization_df=[]
    Error_rain_df=[]

    #Vérification des listes présentes dans  Field_caracteristic
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
    #Contrôle du mois
    Error_month=Fertilization_data[~Fertilization_data["Month"].isin(Month_data)]
    for i, row in Error_month.iterrows():
        Error_fertilization_list_data.append(
        {'Number column': i + 2, 'Title Columns': 'Month', 'Error Value': 'Invalid month data'})
    #Contrôle pour le type de fertilisation
    for i,row in Fertilization_data.iterrows():
        #Cas de la fertilisation de type minéral
        if row['Fertilization_type']=='Mineral':
            #Ajout si pas dans la liste prédéfinie
            if row['Composition'] not in Mineral_Nitrogen_type:
                Error_fertilization_list_data.append({'Number column': i + 2, 'Title Columns': 'Composition', 'Error Value': row["Composition"]})
            # Vérification du placement minéral
            if row['Placement'] not in Mineral_Nitrogen_Placement:
                Error_fertilization_list_data.append({'Number column': i + 2, 'Title Columns': 'Placement', 'Error Value': row["Placement"]})
        elif row['Fertilization_type'] == 'Organic':
            # Vérification de la composition organique
            if row['Composition'] not in Organic_fertilizer_type:
                Error_fertilization_list_data.append(
                    {'Number column': i + 2, 'Title Columns': 'Composition', 'Error Value': row["Composition"]})
            # Vérification du placement organique
            if row['Placement'] not in Organic_fertilizer_Placement:
                Error_fertilization_list_data.append(
                    {'Number column': i + 2, 'Title Columns': 'Placement', 'Error Value': row["Placement"]})
        else:
            # Si le type de fertilisation est invalide
            Error_fertilization_list_data.append(
                {'Number column': i + 2, 'Title Columns': 'Fertilization_type', 'Error Value': 'Invalid fertilization type'})
    # Création du tableau avec les erreurs présent dans le fichier Field-caracteristic
    Error_fertilization_df = pd.DataFrame(Error_fertilization_list_data)

    #Vérification du mois dans Rainfall_data
    # Vérification des listes présentes dans  Field_caracteristic
    Error_Month = Rainfall_data[~Rainfall_data["Month"].isin(Month_data)]
    # Ajout des erreurs pour chaque colonne spécifique
    for i, row in Error_Month.iterrows():
        Error_rain_list_data.append(
            {'Number column': i + 2, 'Title Columns': 'Month', 'Error Value': "Invalid month data"})
    # Création du tableau avec les erreurs présent dans le fichier Field-caracteristic
    Error_rain_df = pd.DataFrame(Error_Month)

    return Error_field_df,Error_year_df,Error_fertilization_df,Error_rain_df

#Vérification que les données soit bien des
def int_data(Field_caracteristic,Year_data,Fertilization_data,Rainfall_data):

    #Variable permettant de récupérer les informations erreurs
    int_error_fielddata=[]
    int_error_yeardata=[]
    int_error_fertilizationdata=[]
    int_error_raindata=[]

    #Variable permettant crée un tableau avec la localisation des erreurs
    int_error_fielddata_df=[]


    for i,value in Field_caracteristic["Year_planting"].iteritems():
        if i<0:
            int_error_fielddata.append( {'Number column': i + 2, 'Title Columns': 'Year planting', 'Error Value': "Invalid type number"})
            print(int_error_fielddata)















    #Vérification des Year_data
    #Index_Year_error.extend(Year_data[~Year_data])

#file_type(Field_caracteristic, Year_data, Fertilization_data, Rainfall_data)
#data_type(Field_caracteristic, Year_data, Fertilization_data)
#int_data(Field_caracteristic,Year_data,Fertilization_data,Rainfall_data)



#fonction test: ./Example_File/Year_Field_data_example.csv
#C:\Users\svrignon\Desktop\programme\CSV_data\Essai\Field_caracteristics_example.csv
#./Example_File/Year_Field_data_example.csv
#./Example_File/Fertilization_data_example.csv
#./Example_File/Rainfall_data_example.csv