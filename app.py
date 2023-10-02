import streamlit as st
import pandas as pd
import ast 
from PIL import Image
from urllib.error import URLError

# Constants
DEFAULT_NUMBER_OF_ROWS = 5
DEFAULT_NUMBER_OF_COLUMNS = 5
GRADE_TO_IMAGE = {
    'A': 'app/static/A.png',
    'B': 'app/static/B.png',
    'C': 'app/static/C.png',
    'D': 'app/static/D.png',
    'E': 'app/static/E.png'
}
# Set page configuration
st.set_page_config(
    page_title='OpenClassrooms',
    layout='wide',
    page_icon=':rocket:'
)

# Load CSS
def load_css(file_name):
    with open(file_name) as f:
        return f.read()

st.markdown(f'<style>{load_css("static/cascade.css")}</style>', unsafe_allow_html=True)

# Initialization
if 'position' not in st.session_state:
    st.session_state.position = 0
   
# getting the UN data 
def get_UN_data():
    df = pd.read_csv("df_app.csv", sep="\t", nrows=5000)
    return df

cols_to_show = ["code", "product_name","brands", "image_url","nutriscore_grade","nova_group", "salt_combined_100g","saturated_fat_100g","nutriscore_score","pnns_groups_2", "proteins_100g","fat_100g","carbohydrates_100g","sugars_100g",  "energy_kcal_100g","fiber_100g","additives_n","additives_list"]
additives_list = []

try:
    df = get_UN_data()
    # drop first 10 rows of the dataframe
    df = df.drop(df.index[0:11])    

    if df.empty:
        st.error("Dataframe is empty.")
        raise ValueError("Dataframe is empty.")
    
    product_options = list(df.product_name + " -- " + df.brands)
    # product_options.insert(0, "")
    product = st.selectbox("Choissisez un produit", product_options)
            
    if product:
        split = product.split("--")
        product = split[0].strip()
        brand = split[1].strip()
        
    # SIDEBAR
    st.sidebar.title("Nutri Suggestion")
    st.sidebar.image("static/choice.jpeg")

    # liste des additifs
    additives = df.additives_list[~df.additives_list.isna()]
    additives = additives.str.split(", ")

    # print(additives)
    for addi in additives:
        for elt in addi:
            if elt !=  " ":
                additives_list.append(elt.strip("'"))

    additives_list = list(dict.fromkeys(additives_list))

    addi_selection = st.sidebar.multiselect("Additifs à exclure", additives_list)
    nova = st.sidebar.slider('NovaGroup',1, 4, (1, 4), 1)
    lip_widget = st.sidebar.empty()
    lip = lip_widget.slider("Lipides par 100g", 0, 100, (0, 100), 1)
    prot = st.sidebar.slider("Protéines par 100g", 0, 100, (0, 100), 10)
    carb = st.sidebar.slider("Glucides par 100g", 0, 100, (0, 100), 10)
    sugars = st.sidebar.slider("Sucres par 100g", 0, 100, (0, 100), 10)
    fiber = st.sidebar.slider("Fibres par 100g", 0, 100, (0, 100), 10)
    cal = st.sidebar.slider("Calories par 100g", 0, 900, (0, 900), 50)
    addi_n = st.sidebar.slider('Nombre d\'additifs',0, 20, (0, 20), 1)
    
    # Choix du produit
    zindex = df[(df["product_name"] == product) & (df["brands"] == brand)].index
    data = df.loc[zindex, cols_to_show].head(1)

    img_slice = df.loc[zindex, ["image_url"]]

    if not img_slice.empty:
        img = img_slice.values[0]
    else:
        st.error("No image found for the selected product.")
        img = None  # or provide a default image URL

    if not data.empty:
        product = data.iloc[0]
    else:
        st.error("No data available for the selected product.")
        product = None  # or provide a default value

    if product is not None:
        st.write(f'<section class="performance-facts"><header class="performance-facts__header"> <h1 class="performance-facts__title">Apports nutritionnels</h1>\
            </header> <table class="performance-facts__table"> <thead> <tr> <th colspan="3" class="small-info"> Quantités pour 100g</th> </tr> </thead>\
            <tbody> <tr> <th colspan="2"> <b>Calories</b></th> <td> {round(product.energy_kcal_100g)} kcal </td> </tr> <tr class="thick-row"></tr>\
            <tr> <th colspan="2"> <b>Matières grasses</b></th> <td> <b>{product.fat_100g+product.saturated_fat_100g} g</b> </td> </tr> <tr> <td class="blank-cell"> </td> <th> Acides gras saturés </th> <td> <b>{product.saturated_fat_100g} g</b>\
            </td></tr><tr></td></tr><tr>\
            <th colspan="2"> <b>Protéines</b></th> <td> <b>{product.proteins_100g} g</b> </td> </tr> <tr> <th colspan="2"> <b>Sel</b> </th> <td> <b>{product.salt_combined_100g} g</b>\
            </td> </tr> <tr> <th colspan="2"> <b>Glucides</b></th> <td> <b>{product.carbohydrates_100g} g</b> </td> </tr> <tr> <td class="blank-cell"> </td>\
            <th> Fibres </th> <td> <b>{product.fiber_100g} g</b> </td> </tr> <tr> <td class="blank-cell"> </td> <th> Sucre </th> <td>{product.sugars_100g} g</td> </tr>\
            </tbody> </table>\
            <img height="40px" src="https://static.openfoodfacts.org/images/attributes/nutriscore-{product.nutriscore_grade.lower()}.svg"/>\
            <img height="40px" src="https://static.openfoodfacts.org/images/attributes/nova-group-{int(product.nova_group)}.svg"/></section>\
            <div style="padding:20px"><img height="550px" src="{product.image_url}"/></div>', unsafe_allow_html=True)
    
        cat1 = df.loc[zindex, ["pnns_groups_1"]].values[0][0]
        cat2 = df.loc[zindex, ["pnns_groups_2"]].values[0][0]
        nutriscore = df.loc[zindex, ["nutriscore_score"]].values[0][0]       

        # filtrage
        mask = (df['pnns_groups_1'] == cat1) & (df['pnns_groups_2'] == cat2) &\
        (df['nutriscore_score'] < nutriscore) &\
        (df['energy_kcal_100g'] >= cal[0]) & (df['energy_kcal_100g'] < cal[1]) &\
        (df['proteins_100g'] >= prot[0]) & (df['proteins_100g'] < prot[1]) &\
        (df['carbohydrates_100g'] >= carb[0]) & (df['carbohydrates_100g'] < carb[1]) &\
        (df['sugars_100g'] >= sugars[0]) & (df['sugars_100g'] < sugars[1]) &\
        (df['fiber_100g'] >= fiber[0]) & (df['fiber_100g'] < fiber[1]) &\
        (df['additives_n'] >= addi_n[0]) & (df['additives_n'] < addi_n[1]) &\
        (df['nova_group'] >= nova[0]) & (df['nova_group'] < nova[1])

        # dataframe filtré
        data2 = df.loc[mask, cols_to_show]
        
        # vérifier si fat_100g est nan et si c'est le cas, filtrer sur fat_100g = 0
        if data2["fat_100g"].isna().any():
            data2 = data2[data2["fat_100g"] == 0]

        # cas particuliers des additfs
        addi_indexes = []
        for index, elt in data2.loc[~data2["additives_list"].isna(),"additives_list"].items(): 
            if elt != " ":
                elt = ast.literal_eval(elt)
            else: 
                continue
            for elt2 in elt:
                if elt2 in (addi_selection):
                    addi_indexes.append(index)
        addi_indexes = list(dict.fromkeys(addi_indexes))

        # filtrage par additifs
        data2 = data2[~data2.index.isin(addi_indexes)]

        # on affiche que 20 résultats
        data2 = data2.sort_values(by="nutriscore_score").head(20)
        shapoo = data2.shape[0]
            
        data2['nutriscore_grade'] = data2['nutriscore_grade'].map(GRADE_TO_IMAGE)

        if(not data2.empty):

            zoo = st.expander("Suggestions de substitutions:", expanded=True)
            
            def dataframe_with_selections(df):
                df_with_selections = df.copy()
                # drop few columns from df_with_selections
                df_with_selections.drop([ 'code', 'nutriscore_score', 'pnns_groups_2', 'additives_list', 'additives_n','nova_group'], axis=1, inplace=True)
                
                # Get dataframe row-selections from user with st.data_editor
                edited_df = st.data_editor(
                    df_with_selections,
                    hide_index=True,
                    column_config = {
                        "image_url": st.column_config.ImageColumn("Image"),
                        "nutriscore_grade": st.column_config.ImageColumn("Nutriscore")
                    },
                    disabled=df.columns,
                )
            selection = dataframe_with_selections(data2)
        else:
            st.write('Aucun résultat trouvé')
        
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )