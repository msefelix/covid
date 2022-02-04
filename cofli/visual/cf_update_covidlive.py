import plotly.express as px
import pandas as pd

def make_a_ts_fig(df: pd.DataFrame, y:str, title:str):
    cols = ['daily', '7D AVG']
    df_temp = df[[y, f"7D AVG - {y}"]]
    df_temp.columns = cols
    fig = px.line(df_temp, x=df_temp.index, y=cols, 
                  title=title, labels={'y':''})
    fig.update_layout(title={'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
                    yaxis={'title':''})
    return fig