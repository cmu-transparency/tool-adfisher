import sys
# import os
sys.path.insert(0, "../core")       # files from the core # noqa: E402

import adfisher                     # adfisher wrapper function
import web.pre_experiment.alexa     # collecting top sites from alexa
import web.google_search             # interacting with Google News
# import converter.reader             # read log and create feature vectors
# import analysis.statistics          # statistics for significance testing

log_file = 'log.demo.txt'
site_file = 'demo.txt'


def make_browser(unit_id, treatment_id):
    b = web.google_search.GoogleSearchUnit(
        browser='firefox',
        log_file=log_file,
        unit_id=unit_id,
        treatment_id=treatment_id,
        headless=False,
        proxy=None)

    return b


# Control Group treatment
def control_treatment(unit):
    pass


# Experimental Group treatment
def exp_treatment(unit):
    pass


# Measurement - Collects ads
def measurement(unit):
    unit.search_and_collect(query_file='carsquery.txt', searchdelay=20, pages=2)


# Shuts down the browser once we are done with it.
def cleanup_browser(unit):
    unit.quit()

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


# Load results reads the log_file, and creates feature vectors
def load_results():
    pass


def test_stat(observed_values, unit_assignments):
    pass


adfisher.do_experiment(
    make_unit=make_browser,
    treatments=[control_treatment, exp_treatment],
    measurement=measurement,
    end_unit=cleanup_browser,
    load_results=load_results,
    test_stat=test_stat,
    ml_analysis=True,
    num_blocks=1,
    num_units=2,
    timeout=2000,
    log_file=log_file,
    exp_flag=True,
    analysis_flag=False,
    treatment_names=["control", "experimental"]
)
