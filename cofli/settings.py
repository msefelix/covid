from datetime import date
today = str(date.today())
bucket = "gs://covid-analytics-data"
locations = ['aus', 'vic', 'nsw', 'qld', 'wa', 'sa', 'act', 'tas', 'nt']

# active imported libs
# cofli
# dash
# dash_bootstrap_components
# gcsfs
# geopandas
# pandas
# pickle
# plotly
# requests
# tempfile
# zipfile

# dash==2.1.0
# dash-bootstrap-components==1.0.2
# gcsfs==2022.1.0
# geopandas==0.9.0
# pandas==1.1.4
# plotly==5.5.0
# requests==2.25.1
# git+https://github.com/msefelix/covid.git