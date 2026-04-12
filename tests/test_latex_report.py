import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.three_ps_lcca_core.core.latex.report import format_formula, generate_latex_report


def test_format_formula_uses_abbreviations_for_long_identifiers():
    formula = (
        "initial_cost_of_construction x interest_rate x "
        "time_for_construction_years x investment_ratio x "
        "sum_of_present_worth_factor"
    )

    formatted = format_formula(formula)

    assert "C_0" in formatted
    assert "SPWF" in formatted
    assert "initial_cost_of_construction" not in formatted


def test_format_formula_renders_division_as_fraction():
    formula = (
        "initial_cost_of_construction x "
        "percentage_of_initial_construction_cost_per_year / 100"
    )

    formatted = format_formula(formula)

    assert "\\frac{" in formatted
    assert "p_{c,y}" in formatted


def test_generate_latex_report_scales_display_equations_to_page_width(tmp_path: Path):
    output_path = tmp_path / "report.tex"
    sample_data = {
        "initial_stage": {"economic": {"time_cost_of_loan": 215671.82}},
        "use_stage": {},
        "reconstruction": {},
        "end_of_life": {},
        "warnings": [],
        "notes": [],
    }
    sample_input_data = {
        "general_parameters": {
            "service_life_years": 75,
            "analysis_period_years": 150,
            "discount_rate_percent": 4,
            "inflation_rate_percent": 2,
            "interest_rate_percent": 7.75,
            "currency_conversion": 1,
        }
    }
    sample_construction_costs = {
        "initial_construction_cost": 12843979.44,
        "initial_carbon_emissions_cost": 2065434.91,
        "superstructure_construction_cost": 9356038.92,
        "total_scrap_value": 2164095.02,
    }
    debug_data = {
        "initial_stage": {
            "time_cost_of_loan": {
                "formulae": {
                    "time_cost_of_loan": (
                        "initial_cost_of_construction x interest_rate x "
                        "time_for_construction_years x investment_ratio x "
                        "sum_of_present_worth_factor x "
                        "percentage_of_initial_construction_cost_per_year"
                    )
                },
                "inputs": {
                    "initial_cost_of_construction": 12843979.44,
                    "interest_rate": 0.0775,
                    "time_for_construction_years": 0.4333333333,
                    "investment_ratio": 0.5,
                    "sum_of_present_worth_factor": 1,
                    "percentage_of_initial_construction_cost_per_year": 0.1,
                },
                "computed_values": {
                    "time_cost_of_loan": 215671.82,
                },
            }
        }
    }

    generate_latex_report(
        sample_data,
        output_path=str(output_path),
        input_data=sample_input_data,
        construction_costs=sample_construction_costs,
        debug_data=debug_data,
    )

    report_text = output_path.read_text(encoding="utf-8")

    assert "\\usepackage{adjustbox}" in report_text
    assert "\\begin{adjustbox}{max width=\\linewidth}" in report_text
    assert "\\begin{aligned}" in report_text
    assert "&=" in report_text
    assert "\\textbf{Abbreviations}" in report_text
    assert "C_0" in report_text
    assert "SPWF" in report_text
