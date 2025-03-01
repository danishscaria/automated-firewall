import datetime
import logging
import azure.functions as func
from firewall_optimizer import optimize_firewalls  # ✅ Correct import
from scripts  import update_azure_firewall  # Import the missing function

app = func.FunctionApp()

@app.function_name(name="FirewallOptimizerFunction")
@app.timer_trigger(schedule="5 */ * * * *", arg_name="mytimer")
def run_firewall_update(myTimer: func.TimerRequest):
    update_azure_firewall()
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info('🔥 Firewall optimizer function triggered at %s', utc_timestamp)

    try:
        result = optimize_firewalls()
        logging.info("✅ Firewall optimization result: %s", result)
    except Exception as e:
        logging.error("❌ Error during firewall optimization: %s", e)
