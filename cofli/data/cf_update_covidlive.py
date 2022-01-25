import pandas as pd


def update_ts_by_state(state:str) -> pd.DataFrame:
    ### Download data
    live_ts = {}
    for ts_type in ['active-cases', 'tests', 'hospitalised']:
        df_temp = pd.read_html(f"https://covidlive.com.au/report/daily-{ts_type}/{state}")[1]
        live_ts[ts_type] = df_temp
        
    ### Consolidate
    res = []
    for ts_type, df_temp in live_ts.items():
        df_temp.columns = [x.lower() for x in df_temp.columns]
        df_temp['date'] = pd.to_datetime(df_temp['date'], yearfirst=False)
        res.append(df_temp.set_index('date'))
    
    res = pd.concat(res, axis=1, ignore_index=False)
    res = res.drop(['var', 'net'], axis=1).dropna(how='all')

    res['active (k)'] = (res['active'] / 1000)
    res['tests (k)'] = (res['tests'] / 1000)

    res = res.drop(['active', 'tests'], axis=1).fillna(0).astype(int).reset_index()
        
    return res