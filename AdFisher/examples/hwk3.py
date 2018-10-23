import sys
sys.path.insert(0, "../core")       # files from the core # noqa: E402

import adfisher                     # adfisher wrapper function
import web.pre_experiment.alexa     # collecting top sites from alexa
import web.google_ads               # interacting with Google ads and Ad Settings
import web.google_news              # interacting with Google ads and Ad Settings
import converter.reader             # read log and create feature vectors
import analysis.statistics          # statistics for significance testing

query_file = 'queries.txt'
site_file = 'sites.txt'
log_file = None


def make_browser(unit_id, treatment_id):
    """Construct an experimental unit."""
    pass  # TODO


def control_treatment(unit):
    """Control Group treatment."""
    pass  # TODO


def exp_treatment1(unit):
    """Experimental Group treatment: TOPIC websites"""
    pass  # TODO


def exp_treatment2(unit):
    """Experimental Group treatment: TOPIC queries"""
    pass  # TODO


def measurement(unit):
    """Measurement - Collects ads."""
    pass  # TODO


def cleanup_browser(unit):
    """Shuts down the browser once we are done with it."""
    unit.quit()


def load_results():
    """Load results reads the log_file, and creates feature vectors."""

    collection, names = converter.reader.read_log(log_file)
    return converter.reader.get_feature_vectors(collection, feat_choice='news')


def test_stat(observed_values, unit_assignments):
    """Test statistic."""
    pass  # TODO


# maintain these invocation options
options = ['measure', 'analyze']
if len(sys.argv) < 3 or sys.argv[1] not in options or sys.argv[2] not in ["1", "2"]:
    print("run with argument: (measure | analyze) (1 | 2)")
    sys.exit(1)

treatments = None
treatment_names = None

if sys.argv[2] == "1":
    log_file = "hypothesis1.log"

    treatments = [exp_treatment1, control_treatment]
    treatment_names = [
        "experimental (TOPIC sites)",
        "control (null)",
    ]
if sys.argv[2] == "2":
    log_file = "hypothesis2.log"

    treatments = [exp_treatment2, control_treatment]
    treatment_names = [
        "experimental (TOPIC queries)",
        "control (null)",
    ]

if sys.argv[1] == 'measure':
    # CAN change parameters below

    adfisher.do_experiment(
        make_unit=make_browser,
        treatments=treatments,
        treatment_names=treatment_names,
        measurement=measurement,
        end_unit=cleanup_browser,
        exp_flag=True,
        analysis_flag=False,
        num_blocks=10,
        num_units=6,
        timeout=2000,
        log_file=log_file
    )


if sys.argv[1] == 'analyze':
    # CAN change parameters below

    adfisher.do_experiment(
        treatments=treatments,
        treatment_names=treatment_names,
        load_results=load_results,
        test_stat=test_stat,
        log_file=log_file,
        ml_analysis=True,
        exp_flag=False,
        analysis_flag=True,
    )
