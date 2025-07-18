import streamlit as st
import pandas as pd
from sage.src import dss_folder
from sage.insights.data_structures import structures

def main(df=pd.DataFrame()):
    # load data structure
    data = structures.get("metric")

    # Load additional data
    if df.empty:
        df = dss_folder.read_folder_input(
            folder_name="base_data",
            path=f"/projects/metadata.csv" # change this line
        )

    # Perform logic here

    # Set values
    data["label"] = "Total DSS Projects"
    data["data"] = df["project_key"].nunique()

    return data