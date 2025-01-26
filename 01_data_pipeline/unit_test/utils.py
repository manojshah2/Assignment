##############################################################################
# Import necessary modules and files
##############################################################################


import pandas as pd
import os
import sqlite3
from sqlite3 import Error
from constants import *
from city_tier_mapping import city_tier_mapping
from significant_categorical_level import *

 
###############################################################################
# Define the function to build database
###############################################################################

def build_dbs():
    '''
    This function checks if the db file with specified name is present 
    in the /Assignment/01_data_pipeline/scripts folder. If it is not present it creates 
    the db file with the given name at the given path. 


    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should exist  


    OUTPUT
    The function returns the following under the given conditions:
        1. If the file exists at the specified path
                prints 'DB Already Exists' and returns 'DB Exists'

        2. If the db file is not present at the specified loction
                prints 'Creating Database' and creates the sqlite db 
                file at the specified path with the specified name and 
                once the db file is created prints 'New DB Created' and 
                returns 'DB created'


    SAMPLE USAGE
        build_dbs()
    '''
    if os.path.isfile(DB_PATH + DB_FILE_NAME):
        print("DB Already Exists")
        print(os.getcwd())
        return
    
    print("Creating Database")
    conn = False
    try:
        conn = sqlite3.connect(DB_PATH + DB_FILE_NAME)
        print("New DB Created")
    # return an error if connection not established
    except Error as e:
        print(e)
        return "Error"
    # closing the connection once the database is created
    finally:
        if conn:
            conn.close()
            return "DB Created"

##############################################################################
# Define function to load the csv file
##############################################################################
def load_data(file_path):
    return pd.read_csv(file_path)

###############################################################################
# Define function to load the csv file to the database
###############################################################################

def load_data_into_db():
    '''
    Thie function loads the data present in data directory into the db
    which was created previously.
    It also replaces any null values present in 'toal_leads_dropped' and
    'referred_lead' columns with 0.


    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be
        DATA_DIRECTORY : path of the directory where 'leadscoring.csv' 
                        file is present
        

    OUTPUT
        Saves the processed dataframe in the db in a table named 'loaded_data'.
        If the table with the same name already exsists then the function 
        replaces it.


    SAMPLE USAGE
        load_data_into_db()
    '''
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)
    total_leads_data = load_data(LEAD_SCORING_TEST_DATA)

    # Replace the null values to 0 in columns total_leads_droppped and referred_lead
    total_leads_data["total_leads_droppped"] = total_leads_data["total_leads_droppped"].fillna(0)
    total_leads_data["referred_lead"] = total_leads_data["referred_lead"].fillna(0)

    # saving the data to database named table loaded_data
    total_leads_data.to_sql(name="loaded_data", con=cnx, if_exists='replace', index=False)


###############################################################################
# Define function to map cities to their respective tiers
###############################################################################

    
def map_city_tier():
    '''
    This function maps all the cities to their respective tier as per the
    mappings provided in the city_tier_mapping.py file. If a
    particular city's tier isn't mapped(present) in the city_tier_mapping.py 
    file then the function maps that particular city to 3.0 which represents
    tier-3.


    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be
        city_tier_mapping : a dictionary that maps the cities to their tier

    
    OUTPUT
        Saves the processed dataframe in the db in a table named
        'city_tier_mapped'. If the table with the same name already 
        exsists then the function replaces it.

    
    SAMPLE USAGE
        map_city_tier()

    '''

    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)

    # read data from database
    total_leads_data = pd.read_sql("select * from loaded_data", con=cnx)

    # map the city tier
    total_leads_data["city_tier"] = total_leads_data["city_mapped"].map(city_tier_mapping)
    total_leads_data["city_tier"] = total_leads_data["city_tier"].fillna(3.0)

    total_leads_data.drop(["city_mapped"],axis=1, inplace=True)

    # save the data back to db
    total_leads_data.to_sql(name="city_tier_mapped", con=cnx, if_exists='replace', index=False)


###############################################################################
# Define function to map insignificant categorial variables to "others"
###############################################################################


def map_categorical_vars():
    '''
    This function maps all the insignificant variables present in 'first_platform_c'
    'first_utm_medium_c' and 'first_utm_source_c'. The list of significant variables
    should be stored in a python file in the 'significant_categorical_level.py' 
    so that it can be imported as a variable in utils file.
    

    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be present
        list_platform : list of all the significant platform.
        list_medium : list of all the significat medium
        list_source : list of all rhe significant source

        **NOTE : list_platform, list_medium & list_source are all constants and
                 must be stored in 'significant_categorical_level.py'
                 file. The significant levels are calculated by taking top 90
                 percentils of all the levels. For more information refer
                 'data_cleaning.ipynb' notebook.
  

    OUTPUT
        Saves the processed dataframe in the db in a table named
        'categorical_variables_mapped'. If the table with the same name already 
        exsists then the function replaces it.

    
    SAMPLE USAGE
        map_categorical_vars()
    '''

    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)

    # loads the data from db
    df = pd.read_sql("select * from city_tier_mapped", con=cnx)

    # replace the data which are not on the list to others, so that we can have only selected categories and others
    new_df = df[~df['first_platform_c'].isin(list_platform)] # get rows for levels which are not present in list_platform
    new_df['first_platform_c'] = "others" # replace the value of these levels to others
    old_df = df[df['first_platform_c'].isin(list_platform)] # get rows for levels which are present in list_platform
    df = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe

    # all the levels below 90 percentage are assgined to a single level called others
    new_df = df[~df['first_utm_medium_c'].isin(list_medium)] # get rows for levels which are not present in list_medium
    new_df['first_utm_medium_c'] = "others" # replace the value of these levels to others
    old_df = df[df['first_utm_medium_c'].isin(list_medium)] # get rows for levels which are present in list_medium
    df = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe

    # all the levels below 90 percentage are assgined to a single level called others
    new_df = df[~df['first_utm_source_c'].isin(list_source)] # get rows for levels which are not present in list_source
    new_df['first_utm_source_c'] = "others" # replace the value of these levels to others
    old_df = df[df['first_utm_source_c'].isin(list_source)] # get rows for levels which are present in list_source
    df = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe

    df = df.drop_duplicates()                    
    print("Storing mapped df to table categorical_variables_mapped")

    # save the data back to db
    df.to_sql(name="categorical_variables_mapped", con=cnx, if_exists='replace', index=False)


##############################################################################
# Define function that maps interaction columns into 4 types of interactions
##############################################################################
def interactions_mapping():
    '''
    This function maps the interaction columns into 4 unique interaction columns
    These mappings are present in 'interaction_mapping.csv' file. 


    INPUTS
        DB_FILE_NAME: Name of the database file
        DB_PATH : path where the db file should be present
        INTERACTION_MAPPING : path to the csv file containing interaction's
                                   mappings
        INDEX_COLUMNS_TRAINING : list of columns to be used as index while pivoting and
                                 unpivoting during training
        INDEX_COLUMNS_INFERENCE: list of columns to be used as index while pivoting and
                                 unpivoting during inference
        NOT_FEATURES: Features which have less significance and needs to be dropped
                                 
        NOTE : Since while inference we will not have 'app_complete_flag' which is
        our label, we will have to exculde it from our features list. It is recommended 
        that you use an if loop and check if 'app_complete_flag' is present in 
        'categorical_variables_mapped' table and if it is present pass a list with 
        'app_complete_flag' column, or else pass a list without 'app_complete_flag'
        column.

    
    OUTPUT
        Saves the processed dataframe in the db in a table named 
        'interactions_mapped'. If the table with the same name already exsists then 
        the function replaces it.
        
        It also drops all the features that are not requried for training model and 
        writes it in a table named 'model_input'

    
    SAMPLE USAGE
        interactions_mapping()
    '''
    cnx = sqlite3.connect(DB_PATH + DB_FILE_NAME)

    # loads the data from db
    total_leads_data = pd.read_sql("select * from categorical_variables_mapped", con=cnx)

    # loads the interaction mapping file
    interaction_mapping = load_data(DB_PATH + INTERACTION_MAPPING)

    # perform unpivot with column provided
    lead_data_unpivot = pd.melt(total_leads_data, id_vars=INDEX_COLUMNS_TRAINING, var_name='interaction_type', value_name='interaction_value')
    lead_data_unpivot['interaction_value'] = lead_data_unpivot['interaction_value'].fillna(0)

    # map the interaction_type from interaction mapping file
    lead_data_unpivot = pd.merge(lead_data_unpivot, interaction_mapping, on='interaction_type', how='left')

    lead_data_unpivot = lead_data_unpivot.drop(["interaction_type"], axis=1)

    # perform pivot operation to get back to original state
    lead_data_pivot = lead_data_unpivot.pivot_table(
        values='interaction_value', index=INDEX_COLUMNS_INFERENCE, columns='interaction_mapping', aggfunc='sum')
    lead_data_pivot = lead_data_pivot.reset_index()

    # save the data back to interaction_mapped
    lead_data_pivot.to_sql(name="interactions_mapped", con=cnx, if_exists='replace', index=False)

    # drops the not required column for training
    lead_data_pivot = lead_data_pivot.drop(NOT_FEATURES,axis=1)

    # save the data back to model input for training
    lead_data_pivot.to_sql(name="model_input", con=cnx, if_exists='replace', index=False)