# Import python packages
import streamlit as st
import requests
import pandas
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie? :cup_with_straw:")
st.write(
    """Coose the fruits you want in your custom Smoothie!
    """
)

name_on_smoothie = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_smoothie)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark Dataframe to Pandas Dataframe so we can use the LOC function 
pd_df = my_dataframe.to_pandas()

ingredient_list = st.multiselect(
    "Choose upt to 5 ingredients!"
    , my_dataframe
    , max_selections=5
)

if ingredient_list:
    ingredients_string = ''
    for fruits_chosen in ingredient_list:
        ingredients_string += fruits_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruits_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruits_chosen + ' Nutrition Information:')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order) values('""" + ingredients_string + """', '""" + name_on_smoothie + """');"""
    
time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered", icon = '✅')


