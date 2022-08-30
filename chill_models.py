"""
    This file provides a minimalistic implementation of common chill requirement models.
    List of the models was taken from the
    Temperate Fruit Trees under Climate Change: Challenges for Dormancy and Chilling Requirements in Warm Winter Regions
    and

    It should be reasonably safe to do from chill_models import *.

    For all models, the input is assumed to be already in the Pandas DataFrame format
    and have datetime index (using local time) as well as a column labeled 'temp' (for temperatures expressed in
    degrees C).
    The assumption of datetime being resampled to 1H intervals is not being made, however -
    that introduces overhead, but reduces the likelihood of some subtle bugs occurring.
"""

import pandas as pd
from typing import Union
from datetime import datetime


def chilling_hours(df: pd.DataFrame) -> pd.Series:
    """
    Chilling hours model: count hours spent below 7.2 C
    Weinberger, J. Chilling requirements of peach varieties. Proc. Am. Soc. Hortic. Sci. 1950, 56, 122–128.
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    return (temps < 7.2).cumsum()


def utah(df: pd.DataFrame, fahrenheit_model: bool = False) -> float:
    """
    Utah chill model
    The model described in the original article is as follows
    <34 F or 54.01–60 F = 0.0 CU (<1.1 C or 12.2-15.6 C)
    34.01–36 F or 48.01–54 F = 0.5 CU (1.1-2.2 C or 8.9-12.2 C)
    36.01–48 F = 1.0 CU (2.2-8.9 C)
    60.01–65 F = -0.5 CU (15.6-18.3 C)
    > 65.01  F = -1.0 CU (>18.3 C)
    The most widely circulated one, however, uses slightly different values (about 0.3 C higher thresholds):
    <1.4 or 12.5–15.9 C = 0.0 CU
    1.5-2.4 or 9.2–12.4 C = 0.5 CU
    2.5–9.1 C = 1 CU
    16–18 C = -0.5 CU
    >18C = -1 CU
    Richardson, E.; Seeley, S.D.; Walker, D. A model for estimating the completion of rest for Redhaven and Elberta peach trees.
    HortScience 1974, 9, 331–332.
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :param fahrenheit_model: If set to True, uses the "classic" model thresholds.
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    if fahrenheit_model:
        return 0.5 * ((temps > 1.1) & (temps <= 2.2)).cumsum() + \
               1.0 * ((temps > 2.2) & (temps <= 8.9)).cumsum() + \
               0.5 * ((temps > 8.9) & (temps <= 12.2)).cumsum() - \
               0.5 * ((temps > 15.6) & (temps <= 18.3)).cumsum() - \
               1.0 * (temps > 18.3).cumsum()
    else:
        return 0.5 * ((temps > 1.4) & (temps <= 2.4)).cumsum() + \
               1.0 * ((temps > 2.4) & (temps <= 9.1)).cumsum() + \
               0.5 * ((temps > 9.1) & (temps <= 12.4)).cumsum() - \
               0.5 * ((temps > 15.9) & (temps <= 18)).cumsum() - \
               1.0 * (temps > 18).cumsum()


def positive_chill_units(df: pd.DataFrame) -> float:
    """
    A modified Utah model for warmer climates. Avoids negative CU totals by assigning 0 CU for temps over 15.9 C
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    return 0.5 * ((temps > 1.4) & (temps <= 2.4)).cumsum() + \
           1.0 * ((temps > 2.4) & (temps <= 9.1)).cumsum() + \
           0.5 * ((temps > 9.1) & (temps <= 12.4)).cumsum()


def landsberg(df: pd.DataFrame, base_temp: float) -> float:
    """
    This model sums daily averages divided by the "base temperature of the crop".
    Note: resampling in this function is done differently
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :param base_temp: Base temperature of the crop (calibrating factor)
    :return: Chill units (CU)
    """
    temps = df['temp'].resample('1D').bfill()
    return temps.cumsum() / base_temp


def low_chill(df: pd.DataFrame) -> float:
    """
    A model for crops with low chilling requirements
    Gilreath, P.R.; Buchanan, D.W. Rest prediction model for low-chilling Sungold nectarine. J. Am. Soc. Hortic. Sci. 1981, 106,
    426–429.
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    return ((temps >= 1.8) & (temps <= 8)).cumsum() - (temps > 19.5).cumsum()


def north_carolina(df: pd.DataFrame) -> float:
    """
    Shaltout, A.D.; Unrath, C.R. Rest completion prediction model for Starkrimson Delicious apples. J. Am. Soc. Hortic. Sci. 1983, 108,
    957–961.
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    return ((temps >= 1.6) & (temps <= 7.2)).cumsum() - 2 * (temps > 23.3).cumsum()


def dynamic(df: pd.DataFrame) -> float:
    """
    Fishman, S.; Erez, A.; Couvillon, G.A. The temperature-dependence of dormancy breaking in plants - mathematical-analysis of a
    2-step model involving a cooperative transition. J. Theor. Biol. 1987, 124, 473–483.
    :param df: DataFrame with datetime index and a 'temp' column with deg C data
    :return: Chill units (CU)
    """
    if pd.infer_freq(df.index) == 'H':
        temps = df['temp']
    else:
        print('Warning: reindexing was required. This series index would not match the original DataFrame one')
        temps = df['temp'].resample('1H').bfill()
    

def reset_chill_hours(s: pd.Series, reset_date: Union[datetime, int]):
    if type(reset_date) is int:
        start_doy = reset_date
    else:
        start_doy = reset_date.timetuple().tm_yday
    # This one is a little tricky. Basically, we shift the start of the year here with integer division. 365 vs 366 is w/e
    return s.groupby([s.index.year + (s.index.dayofyear - start_doy) // 366]).apply(lambda x: x - x.iloc[0])

