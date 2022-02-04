import pandas as pd
from cofli.settings import bucket


def update_ts_by_state(state:str) -> pd.DataFrame:
    ### Download data
    live_ts = {}
    for ts_type, cols in {'cases':['NEW'],
                        'active-cases':['ACTIVE'],
                        'tests':['NET'],
                        'hospitalised':['HOSP', 'ICU', 'VENT']}.items():
        df_temp = pd.read_html(f"https://covidlive.com.au/report/daily-{ts_type}/{state}")[1][['DATE'] + cols]
        live_ts[ts_type] = df_temp
        
    ### Consolidate
    res = []
    for ts_type, df_temp in live_ts.items():
        df_temp.columns = [x.lower() for x in df_temp.columns]
        df_temp['date'] = pd.to_datetime(df_temp['date'], yearfirst=False)
        res.append(df_temp.set_index('date'))
    
    res = pd.concat(res, axis=1, ignore_index=False).dropna(how='all').rename(columns={'net':'tests'})

    res['active (k)'] = (res['active'] / 1000)
    res['tests (k)'] = (res['tests'] / 1000)

    res = res.drop(['cases', 'active', 'tests'], axis=1).fillna(0).astype(int).reset_index()
        
    return res