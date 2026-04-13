import json
from src.three_ps_lcca_core.core.main import run_full_lcc_analysis


# Import user-defined structured inputs
from .Input_global import Input_global


# ============================================================
# DEFINE CONSTRUCTION COST BREAKDOWN
# ============================================================

life_cycle_construction_cost_breakdown = {
    "initial_construction_cost": 12843979.44,
    "initial_carbon_emissions_cost": 2065434.91,
    "superstructure_construction_cost": 9356038.92,
    "total_scrap_value": 2164095.02,
}


# ============================================================
# RUN ANALYSIS FUNCTION
# ============================================================


def execute_analysis(input_data):
    """
    Runs the LCCA analysis using provided input dictionary.
    """

    try:
        results = run_full_lcc_analysis(
            input_data, life_cycle_construction_cost_breakdown, debug=True,latex_report=True,latex_output_path="Example_Report.tex"
        )

        print("✔ LCC Analysis Completed Successfully.")
        return results

    except Exception as e:
        print("✖ Error during LCC analysis:")
        print(e)
        return None


# ============================================================
# MAIN EXECUTION
# ============================================================

# python -m examples.from_dict.example
if __name__ == "__main__":
# =======================================================================
    # run file from project root with:
    # python -m three_ps_lcca_core.examples.example
# ======================================================================
    print("--------------------------------------------------")
    print("Running 3psLCCA Analysis")
    print("--------------------------------------------------")

    results = execute_analysis(Input_global)

    print("\n--- FINAL RESULTS ---")

    if results:
        print(json.dumps(results, indent=2))
    else:
        print("No results generated due to error.")