import os
import vtk
import pyvista as pv
import numpy as np
import argparse


def mag(a):
    "Returns the magnigude of an array of scalars/vectors."
    return np.sqrt((a * a).sum(axis=-1))


def create_file_list(path: str, extension: str):
    """
    Return list of paths of files in path 'path' that have the given extension 'extension'
    """
    return [
        os.path.join(path, file)
        for file in os.listdir(path)
        if file.endswith(extension)
    ]


def vtk_load(inputs):
    inputs = inputs if isinstance(inputs, list) else [inputs]

    sources = [pv.read(input) for input in inputs]
    if len(sources) == 0:
        raise RuntimeError(f"Failed to read any inputs from {inputs}")
    return sources if len(sources) > 1 else sources[0]


def temporal_stats(
    inputs_by_time,
    calc_min: bool = False,
    calc_mean: bool = True,
    calc_max: bool = False,
    calc_std: bool = False,
):
    """
    Compute statistics of point or cell data as it changes over time.

    Given an input that changes over time, vtkTemporalStatistics looks at the data for each time step and
    computes some statistical information of how a point or cell variable changes over time.
    For example, vtkTemporalStatistics can compute the average value of "pressure" over time of each point.

    This filter will produce an array called "time_steps" in the output's FieldData. It contains all the time steps ahta have been processed so far.

    vtkTemporalStatistics ignores the temporal spacing. Each timestep will be weighted the same regardless of how long of an interval it is to the next timestep
    Thus, the average statistic may be quite different from an integration of the variable if the time spacing varies.
    """
    temporal_input = vtk.vtkTemporalDataSetCache()
    temporal_input.DebugOn()
    temporal_input.SetCacheSize(len(inputs_by_time))
    # Enélkül Nem Működik !
    temporal_input.IsASourceOn()

    for input_idx, input in enumerate(inputs_by_time):
        # vtkSetInput(temporal_input, input)
        temporal_input.SetInputDataObject(input)
        temporal_input.UpdateTimeStep(float(input_idx))

    filter = vtk.vtkTemporalStatistics()
    filter.SetInputConnection(temporal_input.GetOutputPort())
    filter.SetComputeAverage(int(calc_mean))
    filter.SetComputeMinimum(int(calc_min))
    filter.SetComputeMaximum(int(calc_max))
    filter.SetComputeStandardDeviation(int(calc_std))
    filter.Update()

    return filter.GetOutput()


def average_simulation(input_data_list, directory, purge=False):
    """
    Extend Time Valued Datasets in input_data_list with Velocity Magnitude Calculated,
    Then Do a Time Average Over All The Attributes, Stored in the Returned DataSet

    Args:
        input_data (DataSet): simulation data

    Returns:
        input_data (DataSet): time-averaged simulation data
    """
    path = os.path.abspath(directory)
    print("Averaging started in folder: " + path)
    casename = str(os.path.splitext(os.path.basename(path))[0])
    os.makedirs(os.path.join(path, "postProc"), exist_ok=True)

    for input_data in input_data_list:
        velocity_magnitude = mag(input_data.point_data["velocity [m/s]"])
        input_data.point_data["velocity_magnitude"] = velocity_magnitude

    input_data_average = temporal_stats(input_data_list, calc_mean=True)

    # SaveData(os.path.join(path, 'postProc', str(casename) + '_time_averaged.vti'), proxy=calc_average, DataMode='Binary')
    pv.ImageData(input_data_average).save(
        os.path.join(path, "postProc", str(casename) + "_time_averaged.vti")
    )
    print("Averaged simulation data saved")

    if purge:
        outputdir = os.path.join(path, "output")
        for f in os.listdir(outputdir):
            os.remove(os.path.join(outputdir, f))
        print("Simulation results purged")

    return input_data_average


def main(path: str, mode: str, pi: float = 1.9, purge: bool = False):
    case_name = str(os.path.splitext(os.path.basename(path))[0])
    if mode == "avglocal":
        sim_data = vtk_load(
            create_file_list(os.path.join(os.path.abspath(path), "output"), ".vti")
        )
        average_simulation(sim_data, path, purge)
    elif mode == "purge":
        for f in os.listdir(os.path.join(path, "output")):
            os.remove(os.path.join(path, "output", f))
        print("Simulation results purged")

    print("Postprocessing finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("d", default="./", help="Path to directory", type=str)
    parser.add_argument("mode", help="Mode: avg, purge", type=str)
    parser.add_argument("-pi", help="Pulsatility index", type=float, default=1.9)
    parser.add_argument(
        "-p", "--purge", action="store_true", help="Purge output directory"
    )
    args = parser.parse_args()

    main(path=os.path.abspath(args.d), mode=args.mode, pi=args.pi, purge=args.purge)
