import pandas as pd
from typing import Dict
from cofli.settings import locations


def download_ts_by_location(location:str) -> Dict[str, pd.DataFrame]:
    live_ts = {}
    for ts_type, cols in {'cases':['NEW'],
                        'active-cases':['ACTIVE'],
                        'tests':['NET'],
                        'deaths':['NET'],
                        'hospitalised':['HOSP', 'ICU', 'VENT']}.items():
        df_temp = pd.read_html(f"https://covidlive.com.au/report/daily-{ts_type}/{location}")[1][['DATE'] + cols]
        if ts_type == 'deaths':
            df_temp = df_temp.rename(columns={'NET':'DEATHS'})
        live_ts[ts_type] = df_temp
    
    return live_ts


def consolidate_ts(live_ts: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """[summary]

    Args:
        live_ts (Dict[str, pd.DataFrame]): [description]

    Returns:
        pd.DataFrame: A table indexed by DatetimeIndex
    """    
    res = []
    for df_temp in live_ts.values():
        df_temp.columns = [x.lower() for x in df_temp.columns]
        df_temp['date'] = pd.to_datetime(df_temp['date'], yearfirst=False)
        res.append(df_temp.set_index('date'))
    
    res = pd.concat(res, axis=1, ignore_index=False).dropna(how='all').rename(columns={'net':'tests'})
    
    for col in ['new', 'tests', 'active', 'deaths']:
        if res[col].dtype == 'O':
            res[col] = res[col].replace(to_replace={'-':0})

    res = res.fillna(0).astype(int)
        
    return res


def update_ts(opath):
    for location in locations:
        print(location)

        live_ts = download_ts_by_location(location)

        ts_df = consolidate_ts(live_ts)

        # Get 7 day moving average
        ts7 = ts_df.rolling('7D').mean().fillna(0).astype(int)
        ts7.columns = [f"7D AVG - {x}" for x in ts7.columns]
        ts_df = ts_df.join(ts7)

        ts_df.to_parquet(f"{opath}/{location}.parquet")

    return
