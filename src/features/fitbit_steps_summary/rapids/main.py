import pandas as pd
import numpy as np

def statsFeatures(steps_data, features_to_compute, features_type, steps_features):
    if features_type == "steps" or features_type == "sumsteps":
        col_name = "steps"
    elif features_type == "durationsedentarybout" or features_type == "durationactivebout":
        col_name = "duration"
    else:
        raise ValueError("features_type can only be one of ['steps', 'sumsteps', 'durationsedentarybout', 'durationactivebout'].")

    if ("summarycount" if features_type == "sumsteps" else "intradaycount") + features_type.replace("duration", "episode") in features_to_compute:
        steps_features["steps_rapids_" + ("summarycount" if features_type == "sumsteps" else "intradaycount") + features_type.replace("duration", "episode")] = steps_data.groupby(["local_segment"])[col_name].count()
    if ("summarysum" if features_type == "sumsteps" else "intradaysum") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summarysum" if features_type == "sumsteps" else "intradaysum") + features_type] = steps_data.groupby(["local_segment"])[col_name].sum()
    if ("summarymax" if features_type == "sumsteps" else "intradaymax") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summarymax" if features_type == "sumsteps" else "intradaymax") + features_type] = steps_data.groupby(["local_segment"])[col_name].max()
    if ("summarymin" if features_type == "sumsteps" else "intradaymin") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summarymin" if features_type == "sumsteps" else "intradaymin") + features_type] = steps_data.groupby(["local_segment"])[col_name].min()
    if ("summaryavg" if features_type == "sumsteps" else "intradayavg") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summaryavg" if features_type == "sumsteps" else "intradayavg") + features_type] = steps_data.groupby(["local_segment"])[col_name].mean()
    if ("summarymedian" if features_type == "sumsteps" else "intradaymedian") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summarymedian" if features_type == "sumsteps" else "intradaymedian") + features_type] = steps_data.groupby(["local_segment"])[col_name].median()
    if ("summarystd" if features_type == "sumsteps" else "intradaystd") + features_type in features_to_compute:
        steps_features["steps_rapids_" + ("summarystd" if features_type == "sumsteps" else "intradaystd") + features_type] = steps_data.groupby(["local_segment"])[col_name].std()

    return steps_features

def extractStepsFeaturesFromSummaryData(steps_summary_data, summary_features_to_compute):
    steps_summary_features = pd.DataFrame()

    # statistics features of daily steps count
    steps_summary_features = statsFeatures(steps_summary_data, summary_features_to_compute, "sumsteps", steps_summary_features)

    steps_summary_features.reset_index(inplace=True)
    
    return steps_summary_features



def rapids_features(sensor_data_files, day_segment, provider, filter_data_by_segment, *args, **kwargs):

    steps_summary_data = pd.read_csv(sensor_data_files["sensor_data"])
    requested_summary_features = ["summary" + x for x in provider["FEATURES"]]

    # name of the features this function can compute
    base_summary_features = ["summarymaxsumsteps", "summaryminsumsteps", "summaryavgsumsteps", "summarymediansumsteps", "summarystdsumsteps"]
    # the subset of requested features this function can compute
    summary_features_to_compute = list(set(requested_summary_features) & set(base_summary_features))

    # extract features from summary data
    steps_summary_features = pd.DataFrame(columns=["local_segment"] + ["steps_rapids_" + x for x in summary_features_to_compute])
    if not steps_summary_data.empty:
        steps_summary_data = filter_data_by_segment(steps_summary_data, day_segment)

        if not steps_summary_data.empty:
            # only keep the segments start at 00:00:00 and end at 23:59:59
            datetime_start_regex = "[0-9]{4}[\\-|\\/][0-9]{2}[\\-|\\/][0-9]{2} 00:00:00"
            datetime_end_regex = "[0-9]{4}[\\-|\\/][0-9]{2}[\\-|\\/][0-9]{2} 23:59:59"

            segment_regex = "{}#{},{}".format(day_segment, datetime_start_regex, datetime_end_regex)
            steps_summary_data = steps_summary_data[steps_summary_data["local_segment"].str.match(segment_regex)]

            if not steps_summary_data.empty:
                steps_summary_features = extractStepsFeaturesFromSummaryData(steps_summary_data, summary_features_to_compute)
    
    return steps_summary_features
