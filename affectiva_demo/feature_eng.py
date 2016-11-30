import pandas as pd
import numpy as np


def computeStats(view):
    df = frames_to_df(view)
    return computWeights(df)


def frames_to_df(view):
    frame_items = ['emojis', 'totalFrames', 'emotions', 'framesSkipped']
    dfs = []
    for frame_item in frame_items:
        tmp = []
        for i in range(0, len(view['frames'])):
            tmp.append(view['frames'][i][frame_item])
        if type(tmp[0]) == int:
            tmp_df = pd.DataFrame({frame_item: tmp})
        else:
            tmp_df = pd.DataFrame(tmp)
        dfs.append(tmp_df)
    final_df = pd.concat(dfs, axis=1)
    return final_df


def computWeights(df):
    # print df
    stats = {}
    for col in df.columns:
        tmp_df = df[col] * df.totalFrames
        val = tmp_df.sum()/df.totalFrames.sum()
        stats[col] = val
    # print stats
    return stats
