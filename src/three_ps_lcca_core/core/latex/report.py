from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]

DEBUG_STAGE_FILES = {
    "initial_stage": PROJECT_ROOT / "debug" / "stage_costs_1-initial_cost_breakdown.json",
    "use_stage": PROJECT_ROOT / "debug" / "stage_costs_2-use_stage_cost_breakdown.json",
    "reconstruction": PROJECT_ROOT / "debug" / "stage_costs_3-Reconstruction_breakdown.json",
    "end_of_life": PROJECT_ROOT / "debug" / "stage_costs_4-end_of_life_breakdown.json",
}

GENERAL_PARAMETER_KEYS = (
    "service_life_years",
    "analysis_period_years",
    "discount_rate_percent",
    "inflation_rate_percent",
    "interest_rate_percent",
    "currency_conversion",
)

FORMULA_SYMBOLS = {
    "cost_of_initial_carbon_emissions_in": r"C_{CO_2,0}",
    "cost_of_reconstruction_after_demolition": r"C_{recon}",
    "cost_of_super_structure": r"C_{ss}",
    "demolition_carbon_cost": r"C_{CO_2,demo}",
    "demolition_cost": r"C_{demo}",
    "demolition_spwi": r"PWF_{demo}",
    "initial_carbon_cost": r"C_{CO_2,0}",
    "initial_construction_cost": r"C_0",
    "initial_cost_of_construction": r"C_0",
    "interest_rate": "r",
    "interval_for_repair_and_rehabitation_in_years": r"n_{rr}",
    "interval_for_repair_and_rehabitation_in_years_for_inspection": r"n_{mi}",
    "interval_for_replacement_in_years": r"n_{rep}",
    "interval_in_years": "n",
    "investment_ratio": "I",
    "major_inspection_cost": r"C_{mi}",
    "percentage_of_initial_cabron_emission_cost": r"p_{CO_2}",
    "percentage_of_initial_carbon_emission_cost": r"p_{CO_2}",
    "percentage_of_initial_construction_cost": r"p_c",
    "percentage_of_initial_construction_cost_for_inspection": r"p_{mi}",
    "percentage_of_initial_construction_cost_per_year": r"p_{c,y}",
    "percentage_of_super_structure_cost": r"p_{ss}",
    "present_worth_factor": "PWF",
    "replacement_cost": r"C_{rep}",
    "routine_carbon_cost_per_year": r"C_{pm,CO_2,y}",
    "routine_inspection_cost_per_year": r"C_{ri,y}",
    "routine_maintenance_cost_per_year": r"C_{pm,y}",
    "sum_of_present_worth_factor": "SPWF",
    "sum_of_present_worth_factor_for_inspection": r"SPWF_{mi}",
    "sum_of_present_worth_factor_for_replacement": r"SPWF_{rep}",
    "time_for_construction_years": r"t_c",
    "time_cost_of_loan": r"C_{loan}",
    "total_scrap_cost": "S",
}

FORMULA_OPERATORS = {
    "*": "*",
    "+": "+",
    "-": "-",
    "/": "/",
    "=": "=",
    "x": "*",
    "(": "(",
    ")": ")",
}

OPERATOR_PRECEDENCE = {
    "=": 0,
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
}
AUTO_SYMBOL_STOPWORDS = {
    "after",
    "and",
    "cost",
    "during",
    "for",
    "in",
    "of",
    "per",
    "present",
    "total",
    "value",
    "with",
    "worth",
    "year",
    "years",
}
SCALAR_DICT_THRESHOLD = 25
SECTION_COMMANDS = {
    1: "section",
    2: "subsection",
    3: "subsubsection",
}
COMPACT_HEADING_AFTERSPACE = "-0.35em"


def escape_latex(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def humanize_key(key: Any) -> str:
    return str(key).replace("_", " ").strip().title()


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def format_number(value: float) -> str:
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def format_value(value: Any) -> str:
    if is_number(value):
        return escape_latex(format_number(float(value)))
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return escape_latex(", ".join(str(item) for item in value))
    return escape_latex(value)


def format_math_number(value: Any) -> str:
    if not is_number(value):
        return escape_latex(value)
    return format_number(float(value)).replace(",", r"\,")


def render_heading(title: str, level: int) -> str:
    if level <= 3:
        command = SECTION_COMMANDS[level]
        return f"\\{command}{{{escape_latex(humanize_key(title))}}}\n"
    return (
        f"\\textbf{{{escape_latex(humanize_key(title))}}}\\par"
        f"\\vspace{{{COMPACT_HEADING_AFTERSPACE}}}\n"
    )


def safe_stage_title(stage_name: str) -> str:
    return {
        "initial_stage": "Initial Stage",
        "use_stage": "Use Stage",
        "reconstruction": "Reconstruction",
        "end_of_life": "End-of-Life Stage",
    }.get(stage_name, humanize_key(stage_name))


def auto_symbol(name: str) -> str:
    parts = [part for part in name.split("_") if part]
    filtered = [part for part in parts if part not in AUTO_SYMBOL_STOPWORDS]
    seed = filtered or parts or [name]
    if len(seed) == 1:
        token = seed[0]
        return token[: min(len(token), 4)].upper()
    return "".join(part[0].upper() for part in seed[:4])


def tokenize_formula(formula: str) -> list[str]:
    prepared = formula
    for operator in ("(", ")", "+", "-", "/", "=", "*"):
        prepared = prepared.replace(operator, f" {operator} ")
    return prepared.split()


def is_symbolic_formula(formula: str) -> bool:
    stripped = formula.strip()
    if not stripped:
        return False
    if stripped.lower().startswith("calculated based on"):
        return False
    tokens = tokenize_formula(stripped)
    if len(tokens) == 1:
        return True
    return any(token in FORMULA_OPERATORS for token in tokens)


def token_to_symbol(token: str, legend: dict[str, str]) -> str:
    symbol = FORMULA_SYMBOLS.get(token)
    if symbol is None:
        symbol = auto_symbol(token)
    legend[token] = symbol
    return symbol


def is_numeric_token(token: str) -> bool:
    numeric = token.replace(".", "", 1)
    return numeric.isdigit()


def normalize_operator(token: str) -> str:
    return FORMULA_OPERATORS.get(token, token)


def parse_formula(formula: str) -> Any:
    tokens = tokenize_formula(formula)
    position = 0

    def parse_expression(min_precedence: int = 0) -> Any:
        nonlocal position
        node = parse_primary()

        while position < len(tokens):
            operator = normalize_operator(tokens[position])
            precedence = OPERATOR_PRECEDENCE.get(operator)
            if precedence is None or precedence < min_precedence:
                break
            position += 1
            rhs = parse_expression(precedence + 1)
            node = ("binary", operator, node, rhs)

        return node

    def parse_primary() -> Any:
        nonlocal position
        if position >= len(tokens):
            return ("atom", "")

        token = tokens[position]
        position += 1

        if token == "(":
            inner = parse_expression()
            if position < len(tokens) and tokens[position] == ")":
                position += 1
            return ("group", inner)

        return ("atom", token)

    return parse_expression()


def render_formula_atom(
    token: str,
    legend: dict[str, str],
    inputs: dict[str, Any] | None = None,
    abbreviate: bool = True,
) -> str:
    if inputs and token in inputs:
        return format_math_number(inputs[token])

    if is_numeric_token(token):
        return token

    if abbreviate:
        return token_to_symbol(token, legend)

    return rf"\text{{{escape_latex(humanize_key(token))}}}"


def node_precedence(node: Any) -> int:
    if not isinstance(node, tuple):
        return 99
    kind = node[0]
    if kind in {"atom", "group"}:
        return 99
    return OPERATOR_PRECEDENCE.get(node[1], 99)


def render_formula_node(
    node: Any,
    legend: dict[str, str],
    inputs: dict[str, Any] | None = None,
    abbreviate: bool = True,
) -> str:
    if not isinstance(node, tuple):
        return ""

    kind = node[0]
    if kind == "atom":
        return render_formula_atom(
            node[1],
            legend=legend,
            inputs=inputs,
            abbreviate=abbreviate,
        )

    if kind == "group":
        inner = render_formula_node(
            node[1],
            legend=legend,
            inputs=inputs,
            abbreviate=abbreviate,
        )
        return rf"\left({inner}\right)"

    _, operator, left, right = node

    if operator == "/":
        numerator = render_formula_node(
            left,
            legend=legend,
            inputs=inputs,
            abbreviate=abbreviate,
        )
        denominator = render_formula_node(
            right,
            legend=legend,
            inputs=inputs,
            abbreviate=abbreviate,
        )
        return rf"\frac{{{numerator}}}{{{denominator}}}"

    left_rendered = render_formula_node(
        left,
        legend=legend,
        inputs=inputs,
        abbreviate=abbreviate,
    )
    right_rendered = render_formula_node(
        right,
        legend=legend,
        inputs=inputs,
        abbreviate=abbreviate,
    )

    current_precedence = OPERATOR_PRECEDENCE[operator]
    if node_precedence(left) < current_precedence:
        left_rendered = rf"\left({left_rendered}\right)"

    if node_precedence(right) < current_precedence or (
        operator in {"-", "/"} and node_precedence(right) == current_precedence
    ):
        right_rendered = rf"\left({right_rendered}\right)"

    math_operator = {
        "*": r"\times",
        "+": "+",
        "-": "-",
        "=": "=",
    }[operator]
    return f"{left_rendered} {math_operator} {right_rendered}"


def flatten_binary_chain(node: Any, operator: str) -> list[Any]:
    if (
        isinstance(node, tuple)
        and len(node) == 4
        and node[0] == "binary"
        and node[1] == operator
    ):
        return flatten_binary_chain(node[2], operator) + flatten_binary_chain(
            node[3], operator
        )
    return [node]


def render_equation_lines(
    formula_name: str,
    formula: str,
    inputs: dict[str, Any] | None = None,
    abbreviate: bool = True,
) -> tuple[list[str], dict[str, str]]:
    legend: dict[str, str] = {}
    lhs = token_to_symbol(formula_name, legend) if abbreviate else escape_latex(
        humanize_key(formula_name)
    )
    expression = parse_formula(formula)

    if (
        isinstance(expression, tuple)
        and len(expression) == 4
        and expression[0] == "binary"
        and expression[1] == "*"
    ):
        terms = flatten_binary_chain(expression, "*")
        rendered_terms = [
            render_formula_node(
                term,
                legend=legend,
                inputs=inputs,
                abbreviate=abbreviate,
            )
            for term in terms
        ]
        lines = [f"{lhs} &= {rendered_terms[0]}"]
        current_line = lines[0]
        for term in rendered_terms[1:]:
            next_piece = rf"\times {term}"
            if len(current_line) + len(next_piece) > 72:
                current_line = rf"&\qquad {next_piece}"
                lines.append(current_line)
                continue
            current_line = f"{current_line} {next_piece}"
            lines[-1] = current_line
        return lines, legend

    rhs = render_formula_node(
        expression,
        legend=legend,
        inputs=inputs,
        abbreviate=abbreviate,
    )
    lines = [f"{lhs} &= {rhs}"]

    return lines, legend


def format_formula(
    formula: str,
    inputs: dict[str, Any] | None = None,
    abbreviate: bool = True,
) -> str:
    if not is_symbolic_formula(formula):
        return escape_latex(formula)
    expression = parse_formula(formula)
    return render_formula_node(
        expression,
        legend={},
        inputs=inputs,
        abbreviate=abbreviate,
    )


def render_math_display(lines: list[str]) -> str:
    body = " \\\\\n".join(lines)
    return (
        "\\begin{center}\n"
        "\\begin{adjustbox}{max width=\\linewidth}\n"
        "$\\displaystyle\\begin{aligned}\n"
        f"{body}\n"
        "\\end{aligned}$\n"
        "\\end{adjustbox}\n"
        "\\end{center}\n"
    )


def explain_formula(name: str) -> str:
    label = humanize_key(name).lower()
    if label.startswith("present value of "):
        tail = label.replace("present value of ", "", 1)
        return (
            f"This converts {escape_latex(tail)} into present-value terms "
            "using the applicable discounting factor."
        )
    if "per year" in label:
        return f"This calculates the annual {escape_latex(label.replace(' per year', ''))} before discounting."
    if "factor" in label:
        return f"This calculates the {escape_latex(label)} used elsewhere in the report."
    return f"This calculates {escape_latex(label)}."


def result_for_formula(
    formula_name: str,
    payload: dict[str, Any],
) -> Any | None:
    computed_values = payload.get("computed_values")
    if isinstance(computed_values, dict) and formula_name in computed_values:
        return computed_values[formula_name]
    if formula_name in payload and is_number(payload[formula_name]):
        return payload[formula_name]
    if "value" in payload and is_number(payload["value"]):
        return payload["value"]
    return None


def render_formula_entry(
    formula_name: str,
    formula: str,
    inputs: dict[str, Any] | None,
    result: Any | None,
) -> str:
    parts = [render_heading(formula_name, 4)]
    parts.append(f"{explain_formula(formula_name)}\n\n")

    if not is_symbolic_formula(formula):
        parts.append(f"\\textit{{Formula note.}} {escape_latex(formula)}.\n\n")
        if result is not None:
            parts.append(
                f"\\textit{{Result.}} {escape_latex(humanize_key(formula_name))} = {format_value(result)}.\n\n"
            )
        return "".join(parts)

    symbolic_lines, legend = render_equation_lines(
        formula_name=formula_name,
        formula=formula,
        abbreviate=True,
    )
    parts.append(render_heading("equation", 4))
    parts.append(render_math_display(symbolic_lines))

    if inputs:
        substituted_lines, _ = render_equation_lines(
            formula_name=formula_name,
            formula=formula,
            inputs=inputs,
            abbreviate=True,
        )
        parts.append(render_heading("substitution", 4))
        parts.append(render_math_display(substituted_lines))

    if result is not None:
        result_symbol = token_to_symbol(formula_name, legend)
        parts.append(render_heading("result", 4))
        parts.append(
            render_math_display([f"{result_symbol} &= {format_math_number(result)}"])
        )

    if legend:
        legend_rows = [
            (f"${symbol}$", escape_latex(humanize_key(token)))
            for token, symbol in legend.items()
        ]
        parts.append(render_heading("abbreviations", 4))
        parts.append(render_tabularx(legend_rows, ("Symbol", "Meaning")))

    return "".join(parts)


def render_tabularx(
    rows: list[tuple[str, str]],
    headers: tuple[str, str],
) -> str:
    parts = [
        "\\begin{tabularx}{\\linewidth}{>{\\raggedright\\arraybackslash}p{0.43\\linewidth} >{\\raggedright\\arraybackslash}X}\n",
        "\\toprule\n",
        f"{escape_latex(headers[0])} & {escape_latex(headers[1])} \\\\\n",
        "\\midrule\n",
    ]
    for left, right in rows:
        parts.append(f"{left} & {right} \\\\\n")
    parts.append("\\bottomrule\n\\end{tabularx}\n")
    return "".join(parts)


def render_longtable(
    rows: list[tuple[str, str]],
    headers: tuple[str, str],
) -> str:
    parts = [
        "\\begin{longtable}{p{0.43\\linewidth} p{0.49\\linewidth}}\n",
        "\\toprule\n",
        f"{escape_latex(headers[0])} & {escape_latex(headers[1])} \\\\\n",
        "\\midrule\n",
        "\\endfirsthead\n",
        "\\toprule\n",
        f"{escape_latex(headers[0])} & {escape_latex(headers[1])} \\\\\n",
        "\\midrule\n",
        "\\endhead\n",
    ]
    for left, right in rows:
        parts.append(f"{left} & {right} \\\\\n")
    parts.append("\\bottomrule\n\\end{longtable}\n")
    return "".join(parts)


def render_kv_table(
    mapping: dict[str, Any],
    headers: tuple[str, str] = ("Parameter", "Value"),
) -> str:
    rows = [
        (escape_latex(humanize_key(key)), format_value(value))
        for key, value in mapping.items()
    ]
    if len(rows) > SCALAR_DICT_THRESHOLD:
        return render_longtable(rows, headers)
    return render_tabularx(rows, headers)


def render_list(items: list[Any]) -> str:
    parts = ["\\begin{itemize}[leftmargin=*]\n"]
    for item in items:
        parts.append(f"\\item {format_value(item)}\n")
    parts.append("\\end{itemize}\n")
    return "".join(parts)


def sum_numeric_values(payload: Any) -> float:
    if is_number(payload):
        return float(payload)
    if isinstance(payload, dict):
        return sum(sum_numeric_values(value) for value in payload.values())
    if isinstance(payload, list):
        return sum(sum_numeric_values(item) for item in payload)
    return 0.0


def render_scalar_mapping(
    mapping: dict[str, Any],
    level: int,
    title: str | None = None,
) -> str:
    parts: list[str] = []
    if title:
        parts.append(render_heading(title, min(level, 4)))
    parts.append(render_kv_table(mapping))
    return "".join(parts)


def render_payload(
    title: str,
    payload: Any,
    level: int = 2,
) -> str:
    parts = [render_heading(title, min(level, 4))]

    if isinstance(payload, list):
        parts.append(render_list(payload))
        return "".join(parts)

    if not isinstance(payload, dict):
        parts.append(f"{format_value(payload)}\n")
        return "".join(parts)

    if "formulae" in payload and isinstance(payload["formulae"], dict):
        for formula_name, formula in payload["formulae"].items():
            parts.append(
                render_formula_entry(
                    formula_name=formula_name,
                    formula=formula,
                    inputs=payload.get("inputs")
                    if isinstance(payload.get("inputs"), dict)
                    else None,
                    result=result_for_formula(formula_name, payload),
                )
            )

    if "formula" in payload and isinstance(payload["formula"], str):
        parts.append(
            render_formula_entry(
                formula_name=title,
                formula=payload["formula"],
                inputs=payload.get("inputs")
                if isinstance(payload.get("inputs"), dict)
                else None,
                result=result_for_formula(title, payload),
            )
        )

    for block_name, header in (
        ("inputs", ("Input", "Value")),
        ("computed_values", ("Computed Value", "Result")),
    ):
        block = payload.get(block_name)
        if isinstance(block, dict) and block:
            parts.append(render_heading(block_name, 4))
            parts.append(render_kv_table(block, headers=header))

    if "note" in payload:
        parts.append(f"\\textit{{Note.}} {format_value(payload['note'])}.\n\n")

    remaining_scalars: dict[str, Any] = {}
    handled_keys = {"formulae", "formula", "inputs", "computed_values", "note"}
    for key, value in payload.items():
        if key in handled_keys:
            continue
        if isinstance(value, dict):
            parts.append(render_payload(key, value, level=min(level + 1, 4)))
        elif isinstance(value, list):
            parts.append(render_payload(key, value, level=min(level + 1, 4)))
        else:
            remaining_scalars[key] = value

    if remaining_scalars:
        parts.append(render_kv_table(remaining_scalars))

    return "".join(parts)


def render_stage_details(debug_payload: Any) -> str:
    parts = ["\\subsection{Detailed Calculations}\n"]
    if isinstance(debug_payload, dict):
        for block_name, block_value in debug_payload.items():
            parts.append(render_payload(block_name, block_value, level=3))
    else:
        parts.append(f"{format_value(debug_payload)}\n")
    return "".join(parts)


def render_stage_summary(
    stage_name: str,
    stage_data: dict[str, Any],
    debug_payload: Any | None = None,
) -> str:
    parts = [f"\\section{{{escape_latex(safe_stage_title(stage_name))}}}\n"]

    if not isinstance(stage_data, dict):
        parts.append(f"{format_value(stage_data)}\n")
        if debug_payload:
            parts.append(render_stage_details(debug_payload))
        return "".join(parts)

    if "Note" in stage_data and len(stage_data) == 1:
        parts.append(f"\\textit{{Note.}} {format_value(stage_data['Note'])}.\n")
        if debug_payload:
            parts.append(render_stage_details(debug_payload))
        return "".join(parts)

    summary_rows: list[tuple[str, str]] = []
    for category_name, category_values in stage_data.items():
        if isinstance(category_values, dict):
            for item_name, item_value in category_values.items():
                summary_rows.append(
                    (
                        escape_latex(
                            f"{humanize_key(category_name)}: {humanize_key(item_name)}"
                        ),
                        format_value(item_value),
                    )
                )

    if summary_rows:
        parts.append("\\subsection{Summary}\n")
        parts.append(render_tabularx(summary_rows, ("Component", "Value")))

    for category_name, category_values in stage_data.items():
        if isinstance(category_values, dict):
            parts.append(
                render_scalar_mapping(
                    category_values,
                    level=2,
                    title=category_name,
                )
            )
        else:
            parts.append(
                render_scalar_mapping({category_name: category_values}, level=2)
            )

    if debug_payload:
        parts.append(render_stage_details(debug_payload))

    return "".join(parts)


def load_debug_payloads() -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for stage_name, path in DEBUG_STAGE_FILES.items():
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                payloads[stage_name] = json.load(handle)
    return payloads


def render_title_page(
    input_data: dict[str, Any] | None,
    construction_costs: dict[str, Any] | None,
) -> str:
    parts = [
        "\\title{Life Cycle Cost Analysis Report}\n",
        "\\author{3psLCCA Engine}\n",
        "\\date{\\today}\n",
        "\\maketitle\n",
    ]

    general_parameters = {}
    if isinstance(input_data, dict):
        general_parameters = input_data.get("general_parameters", {})

    if general_parameters:
        parts.append("\\section*{Project Parameters}\n")
        parts.append(
            render_kv_table(
                {
                    key: general_parameters.get(key)
                    for key in GENERAL_PARAMETER_KEYS
                    if key in general_parameters
                },
                headers=("Parameter", "Value"),
            )
        )

    if construction_costs:
        parts.append("\\section*{Construction Cost Inputs}\n")
        parts.append(
            render_kv_table(
                construction_costs,
                headers=("Construction Input", "Value"),
            )
        )

    return "".join(parts)


def render_final_summary(data: dict[str, Any]) -> str:
    rows: list[tuple[str, str]] = []
    grand_total = 0.0
    for stage_name in ("initial_stage", "use_stage", "reconstruction", "end_of_life"):
        stage_total = sum_numeric_values(data.get(stage_name, {}))
        grand_total += stage_total
        rows.append(
            (escape_latex(safe_stage_title(stage_name)), escape_latex(format_number(stage_total)))
        )
    rows.append(("Grand Total", escape_latex(format_number(grand_total))))
    return "\\section{Summary}\n" + render_tabularx(rows, ("Stage", "Total"))


def generate_latex_report(
    data: dict[str, Any],
    output_path: str | None = None,
    input_data: dict[str, Any] | None = None,
    construction_costs: dict[str, Any] | None = None,
    debug_data: dict[str, Any] | None = None,
) -> None:
    output_file = Path(output_path or "LCCA_Report.tex")
    debug_payloads = debug_data if debug_data is not None else load_debug_payloads()

    latex_parts = [
        "\\documentclass{article}\n",
        "\\usepackage[T1]{fontenc}\n",
        "\\usepackage{booktabs}\n",
        "\\usepackage{amsmath}\n",
        "\\usepackage{amssymb}\n",
        "\\usepackage{geometry}\n",
        "\\usepackage{array}\n",
        "\\usepackage{tabularx}\n",
        "\\usepackage{longtable}\n",
        "\\usepackage{adjustbox}\n",
        "\\usepackage{enumitem}\n",
        "\\geometry{margin=1in}\n",
        "\\setlength{\\parindent}{0pt}\n",
        "\\setlength{\\parskip}{0.5em}\n",
        "\\setlength{\\emergencystretch}{2em}\n",
        "\\allowdisplaybreaks\n",
        "\\begin{document}\n",
        render_title_page(input_data, construction_costs),
    ]

    for stage_name in ("initial_stage", "use_stage", "reconstruction", "end_of_life"):
        stage_data = data.get(stage_name)
        if stage_data is None:
            continue
        stage_debug_payload = (
            debug_payloads.get(stage_name)
            if isinstance(debug_payloads, dict)
            else None
        )
        latex_parts.append(
            render_stage_summary(
                stage_name,
                stage_data,
                debug_payload=stage_debug_payload,
            )
        )

    latex_parts.append(render_final_summary(data))

    warnings = data.get("warnings")
    if warnings:
        latex_parts.append("\\section{Warnings}\n")
        latex_parts.append(render_list(warnings if isinstance(warnings, list) else [warnings]))

    notes = data.get("notes")
    if notes:
        latex_parts.append("\\section{Notes}\n")
        latex_parts.append(render_list(notes if isinstance(notes, list) else [notes]))

    latex_parts.append("\\end{document}\n")

    with output_file.open("w", encoding="utf-8") as handle:
        handle.write("".join(latex_parts))

    print(f"LaTeX report generated at: {output_file}")
