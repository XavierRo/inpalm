from data.reading_data import reading_data
from data.check_data import file_type_verification, Header_Field_caracteristic, Header_Year_data, Header_Rainfall_data,Header_Fertilization_data

def general_script():
    """
    Description du traitement principal
     - lecture des données
     - verfication des headers
     - ...
    :return:
    """
    # chargement des données
    Field_caracteristic, Year_data, Fertilization_data, Rainfall_data = reading_data()

    #controle des données
    file_type_verification(Field_caracteristic, Header_Field_caracteristic)
    file_type_verification(Year_data, Header_Year_data)
    file_type_verification(Fertilization_data, Header_Fertilization_data)
    file_type_verification(Rainfall_data, Header_Rainfall_data)

    #conversion des données

    #normalisation des données
general_script()