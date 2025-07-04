import os
import importlib
import pandas as pd

from sage.base_data import project_handle as dss_object
from sage.src import dss_folder


def run_modules(project_handle, project_key, instance_name, dt):
    directory = dss_object.__path__[0]
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                module_name = f[:-3]
                path = root.replace(directory, "")
                fp = os.path.join(root, f)
                spec = importlib.util.spec_from_file_location(module_name, fp)
                results = False
                try:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'main'):
                        results = module.main(project_handle)
                except Exception as e:
                    results = [False, None]
                    print(f"Error importing or running ({path}) {module_name}: {e}")
            if results[0]:
                category = path.split('/')[-1]
                dt_year  = str(dt.year)
                dt_month = str(f'{dt.month:02d}')
                dt_day   = str(f'{dt.day:02d}')
                dss_folder.write_folder_output(
                    folder_name = "partitioned_data",
                    path = f"/{instance_name}/{category}/{module_name}/{project_key}/{dt_year}/{dt_month}/{dt_day}/data.csv",
                    data_type = "DF",
                    data = results[1]
                )
    return


def stack_project_data(instance_name):
    # create a partitioned folder dataframe
    folder = dss_folder.get_folder(folder_name="partitioned_data")
    d = folder.list_partitions()
    folder_df = pd.DataFrame(d, columns=["partitions"])
    folder_df[["instance_name", "category", "module", "project_key", "dt"]] = folder_df["partitions"].str.split("|", expand=True)
    # Loop over the sets and gather
    for i,grp in folder_df.groupby(by=["category", "module"]):
        # get latest dt partition
        max_date = grp['dt'].max()
        filtered_df = grp[grp['dt'] == max_date]
        # loop over and build consolidated df
        df = pd.DataFrame()
        for partition in filtered_df.partitions.tolist():
            path = folder.list_paths_in_partition(partition=partition)[0]
            tdf = dss_folder.read_folder_input(folder_name="partitioned_data", path=path)
            if df.empty:
                df = tdf
            else:
                df = pd.concat([df, tdf], ignore_index=True)
        # Write consolidated DF to folder
        dss_folder.write_folder_output(
            folder_name = "base_data",
            path = f"/{instance_name}/{i[0]}/{i[1]}.csv",
            data_type = "DF",
            data = df
        )
    return


def main(client, instance_name, dt):
    # Gather data
    project_keys = client.list_project_keys()
    for project_key in project_keys:
        project_handle = client.get_project(project_key=project_key)
        run_modules(project_handle, project_key, instance_name, dt)
    # Stack individual results
    stack_project_data(instance_name)
    return


if __name__ == "__main__":
    main()