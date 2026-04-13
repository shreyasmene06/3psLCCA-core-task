from __future__ import annotations

from typing import Any

from .stage_cost.stage_cost import StageCostCalculator
from .utils.dump_to_file import dump_to_file
from .utils.input_validator import ironclad_validator
from ..inputs.input_global import InputGlobalMetaData


def run_full_lcc_analysis(
    input_data: dict[str, Any] | InputGlobalMetaData,
    construction_costs: dict[str, Any],
    debug: bool = False,
    latex_report: bool = False,
    latex_output_path: str | None = None,
) -> dict[str, Any]:
    """
    Entry point for the OSDAG LCC module (global RUC mode only).
    Validates input, and computes Life Cycle Stage Costs using the
    pre-computed daily_road_user_cost_with_vehicular_emissions.

    Args:
        input_data: Project input.
        construction_costs: Initial construction costs.
        debug: When True, dumps intermediate inputs and stage breakdown JSON files.
        latex_report: When True, generates a LaTeX report.
        latex_output_path: Optional output path for the generated `.tex` report.

    Returns:
        dict: Stage-wise LCC results (initial, use, reconstruction, end-of-life).

    Raises:
        TypeError: If input_data is of an unexpected type.
        ValueError: If input fails validation or required fields are missing.
    """

    requested_debug = debug
    internal_debug = debug or latex_report

    # --- 1. Normalise input_data to dict ---
    if isinstance(input_data, dict):
        gp = input_data.get("general_parameters")
        if gp is None:
            raise ValueError("Missing 'general_parameters' block.")
        InputGlobalMetaData.from_dict(input_data)  # validate structure early
    elif isinstance(input_data, InputGlobalMetaData):
        input_data = input_data.to_dict()
    else:
        raise TypeError("input_data must be a dict or InputGlobalMetaData.")

    # --- 2. Dump all normalised inputs for debugging ---
    if requested_debug:
        dump_to_file(
            "A0_Core_Inputs.json",
            {"input_data": input_data, "construction_costs": construction_costs},
        )

    # --- 3. Validate input ---
    validation_report = ironclad_validator(input_data)
    if validation_report["errors"]:
        raise ValueError(
            f"Input validation failed with errors:\n{validation_report['errors']}"
        )

    # --- 4. Prepare Stage Cost Parameters ---
    ruc_results = input_data.get("daily_road_user_cost_with_vehicular_emissions", {})
    stage_params = input_data.get("maintenance_and_stage_parameters", {}).copy()
    stage_params["general"] = input_data.get("general_parameters", {})

    stage_construction_costs = dict(construction_costs)
    stage_construction_costs["daily_road_user_cost_with_vehicular_emissions"] = ruc_results

    if requested_debug:
        dump_to_file(
            "Stage_Cost_Calculator_Inputs.json",
            {"stage_params": stage_params, "construction_costs": stage_construction_costs},
        )
        dump_to_file("A0_Validation_report.json", validation_report)

    # --- 5. Initialize and run LCC calculations ---
    stage_calc = StageCostCalculator(
        stage_params,
        stage_construction_costs,
        debug=internal_debug,
        persist_debug_files=requested_debug,
    )

    result = {
        "initial_stage": stage_calc.initial_cost_calculator(),
        "use_stage": stage_calc.use_stage_cost_calculator(),
        "reconstruction": stage_calc.reconstruction(),
        "end_of_life": stage_calc.end_of_life_stage_costs(),
        "warnings": validation_report["warnings"],
        "notes": validation_report["info"],
    }

    if latex_report:
        from .latex.report import generate_latex_report

        generate_latex_report(
            data=result,
            output_path=latex_output_path or "LCCA_Report.tex",
            input_data=input_data,
            construction_costs=construction_costs,
            debug_data=stage_calc.get_debug_payloads() if internal_debug else None,
        )

    return result
