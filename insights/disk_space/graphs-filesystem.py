import streamlit as st
import pandas as pd
from sage.src import dss_folder
from sage.insights.data_structures import structures

def main(df=pd.DataFrame()):
    # load data structure
    data = structures.get("bar_chart")

    # Load additional data
    if df.empty:
        df = dss_folder.read_folder_input(
            folder_name="base_data",
            path=f"/{st.session_state.instance_name}/disk_space/filesystem.csv"
        )

    # Data Cleanse
    del df["filesystem"]
    del df["size"]
    del df["used"]
    del df["available"]

    # Build the data structure
    data["title"] = "Filesystem % Usage"
    data["data"] = df
    data["x"] = "mounted_on"
    data["y"] = "used_pct"
    data["x_label"] = "% Used"
    data["y_label"] = "Mounted On"
    data["horizontal"] = True
    
    return data