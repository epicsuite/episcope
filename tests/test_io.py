DATA_DIRECTORY = "/Users/alessandro.genova/work/sources/epicsuite/test_data/LA-UR-25-24911.1"

def test_ensemble():
    from episcope.library.io.v1_1.ensemble import Ensemble
    
    ensemble = Ensemble(DATA_DIRECTORY)

    experiment_name = "Untr_A"
    timestep_name = "12hpi"
    chromosome_name = "NC_023642.1"
    peak_track_name = "ATAC"
    point_track_name = "compartment"

    experiment = ensemble._experiments[experiment_name]
    timestep = experiment._timesteps[timestep_name]

    structure = timestep._structures[chromosome_name]
    peak_track = timestep._peak_tracks[peak_track_name][chromosome_name]
    point_track = timestep._point_tracks[point_track_name][chromosome_name]

    ensemble, experiment, timestep, structure, peak_track, point_track

    assert True

def main():
    test_ensemble()

if __name__ == "__main__":
    main()
