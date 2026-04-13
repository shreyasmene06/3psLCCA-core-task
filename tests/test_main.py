import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.examples.from_dict.Input_global import Input_global
from src.three_ps_lcca_core.core.main import run_full_lcc_analysis


CONSTRUCTION_COSTS = {
    "initial_construction_cost": 12843979.44,
    "initial_carbon_emissions_cost": 2065434.91,
    "superstructure_construction_cost": 9356038.92,
    "total_scrap_value": 2164095.02,
}


def test_latex_report_mode_does_not_dump_debug_files_when_debug_is_false(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)
    output_path = tmp_path / "LCCA_Report.tex"

    run_full_lcc_analysis(
        input_data=Input_global,
        construction_costs=CONSTRUCTION_COSTS,
        debug=False,
        latex_report=True,
        latex_output_path=str(output_path),
    )

    assert output_path.exists()
    debug_dir = tmp_path / "debug"
    assert not (debug_dir / "A0_Core_Inputs.json").exists()
    assert not (debug_dir / "Stage_Cost_Calculator_Inputs.json").exists()
    assert not (debug_dir / "A0_Validation_report.json").exists()
    assert not (debug_dir / "stage_costs_1-initial_cost_breakdown.json").exists()
    assert not (debug_dir / "stage_costs_2-use_stage_cost_breakdown.json").exists()
    assert not (debug_dir / "stage_costs_3-Reconstruction_breakdown.json").exists()
    assert not (debug_dir / "stage_costs_4-end_of_life_breakdown.json").exists()


def test_debug_mode_still_dumps_debug_files(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    run_full_lcc_analysis(
        input_data=Input_global,
        construction_costs=CONSTRUCTION_COSTS,
        debug=True,
        latex_report=False,
    )

    debug_dir = tmp_path / "debug"
    assert (debug_dir / "A0_Core_Inputs.json").exists()
    assert (debug_dir / "Stage_Cost_Calculator_Inputs.json").exists()
    assert (debug_dir / "A0_Validation_report.json").exists()
    assert (debug_dir / "stage_costs_1-initial_cost_breakdown.json").exists()
    assert (debug_dir / "stage_costs_2-use_stage_cost_breakdown.json").exists()
    assert (debug_dir / "stage_costs_3-Reconstruction_breakdown.json").exists()
    assert (debug_dir / "stage_costs_4-end_of_life_breakdown.json").exists()
