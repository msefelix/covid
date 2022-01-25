from cofli.data.cf_update_vic_gov import vic_by_location, add_a_csv
from cofli.data.cf_update_covidlive import update_ts_by_state
from cofli.visual.cf_update_vic import update_figs

def main(event, context):
    vic_by_location()
    add_a_csv()

    update_ts_by_state('vic')
    
    update_figs()

    return