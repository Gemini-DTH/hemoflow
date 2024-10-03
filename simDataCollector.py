import os
import sys

import pandas as pd

def main_run(dir):
    rootdir = os.path.abspath(dir)

    paths = []
    for root, dirs, files in os.walk(rootdir, topdown=False):
        for name in files:
            if "DS_Store" not in name:  # MAC
                paths.append(str(os.path.join(root, name)))

    df = pd.DataFrame()
    counter = 0
    datas = []
    for path in paths:
        if "post_data" in path:
            datas.append(path)
            df_temp = pd.read_csv(path, header=None)
            df_temp = df_temp.transpose()
            df_temp.columns = df_temp.iloc[0]
            df_temp = df_temp[1:]

            if counter == 0:
                df = pd.DataFrame(df_temp)
                counter += 1
            else:
                df = pd.concat([df, df_temp])

    df = df.set_index("casename")
    df.to_csv(os.path.join(rootdir, "simulationData.csv"), index=True, header=True)
    print(f"{len(datas)} simulation data files gathered and written to CSV")


if __name__ == "__main__":
    main_run(sys.argv[1])
