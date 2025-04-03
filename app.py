from flask import Flask, render_template, request
import math

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    show_load_inputs = False
    load_results = ""
    table_results = {}
    limiting_mr_result = ""
    ast_fixed_support_result = "Pending Calculation"
    ast_simply_supported_result = "Pending Calculation"
    reinforcement_spacing_fixed = "Enter Dia Bar"
    reinforcement_spacing_simply = "Enter Dia Bar"
    rounded_spacing_fixed = "Pending Calculation"
    rounded_spacing_simply = "Pending Calculation"
    actual_ast_fixed = "Pending Calculation"
    actual_ast_simply = "Pending Calculation"
    conclusion_fixed = "Pending Calculation"
    conclusion_simply = "Pending Calculation"
    distribution_reinf = "Pending Calculation"  # ASTD (Distribution Reinforcement from D)
    distribution_spacing = "Pending Calculation"
    distribution_rounded_spacing = "Pending Calculation"
    distribution_conclusion = "Pending Calculation"

    # Store the submitted form data
    form_data = {}

    if request.method == "POST":
        form_data = request.form.copy()  # Capture all submitted data

        try:
            # Retrieve general slab inputs (default to 1 to avoid division by zero)
            fck = float(request.form.get("fck", 1))
            fy = float(request.form.get("fy", 1))
            clear_span = float(request.form.get("clear_span", 1))
            support_width = float(request.form.get("support_width", 1))
            depth_ratio = float(request.form.get("depth_ratio", 1))
            clear_cover = float(request.form.get("clear_cover", 1))
            dia_bar = float(request.form.get("dia_bar", 1))

            if depth_ratio <= 0 or clear_span <= 0:
                raise ValueError("Depth Ratio and Clear Span must be greater than zero.")

            # Initial slab calculations
            depth_of_slab = round((clear_span / depth_ratio) / 10) * 10  # Rounded to nearest 10 mm
            D = clear_cover + (dia_bar / 2) + depth_of_slab
            d = D - clear_cover - (dia_bar / 2)

            result += (
                "<h3>Initial Calculation Outputs</h3>"
                f"<b>Depth of Slab:</b> {depth_of_slab} mm | "
                f"<b>D:</b> {D:.2f} mm | <b>d:</b> {d:.2f} mm<br>"
            )

            # Calculate Distribution Reinforcement (ASTD) using the revised formula.
            # ASTD = ((D * 1000) * 0.12) / 100
            astd_val = ((D * 1000) * 0.12) / 100
            distribution_reinf = f"{astd_val:.3f} mm²"

            # Enable live load input form after initial calculations
            show_load_inputs = True

            # Process live load inputs if provided
            live_load_str = request.form.get("live_load", "")
            floor_finish_str = request.form.get("floor_finish", "")
            if live_load_str and floor_finish_str:
                live_load = float(live_load_str)
                floor_finish = float(floor_finish_str)
                if live_load <= 0 or floor_finish <= 0:
                    raise ValueError("Live Load and Floor Finish must be greater than zero.")

                # Calculate load values
                self_weight = 25 * (D / 1000)  # in kN/m² (D from mm to m)
                total_service_load = self_weight + live_load + floor_finish
                factored_load = 1.5 * total_service_load

                load_results = (
                    "<h3>Load Calculation Outputs</h3>"
                    f"<b>Self Weight:</b> {self_weight:.2f} kN/m² | "
                    f"<b>Total Service Load:</b> {total_service_load:.2f} kN/m² | "
                    f"<b>Factored Load:</b> {factored_load:.2f} kN/m²<br>"
                )

                # Calculate bending moment & shear force values
                least_value = min(clear_span + depth_of_slab, clear_span + support_width)
                if least_value <= 0:
                    raise ValueError("Least Value must be greater than zero.")

                # Fixed Support Calculations
                muc = ((factored_load * (least_value ** 2)) / 24) / 1e6  # kN·m
                mus = muc * 2
                shear_fixed = ((factored_load * least_value) / 2) / 1000  # kN

                # Simply Supported Calculations (using assumed multipliers)
                muc_simply = muc * 3
                mus_simply = 0.0
                shear_simply = shear_fixed

                # Populate bending moment & shear force table dictionary
                table_results = {
                    "Fixed Support": {
                        "Muc": f"{muc:.2f} kN·m",
                        "Mus": f"{mus:.2f} kN·m",
                        "Shear": f"{shear_fixed:.2f} kN"
                    },
                    "Simply Supported": {
                        "Muc": f"{muc_simply:.2f} kN·m",
                        "Mus": f"{mus_simply:.2f} kN·m",
                        "Shear": f"{shear_simply:.2f} kN"
                    }
                }

                # Compute Limiting Moment of Resistance (Mu Limiting)
                limiting_mr_values = {250: 149, 415: 138, 500: 133, 550: 129}
                if fy in limiting_mr_values:
                    limiting_mr = (limiting_mr_values[fy] * fck * (depth_of_slab ** 2)) / 1e6
                    limiting_mr_result = (
                        f"<b>Limiting Moment of Resistance for fy = {fy}:</b> "
                        f"{limiting_mr:.2f} kN·m"
                    )

                # Reinforcement Calculations and Spacing Calculation for MAIN reinforcement
                dia_bar_fixed = float(request.form.get("dia_bar_fixed", 0))
                dia_bar_simply = float(request.form.get("dia_bar_simply", 0))
                if dia_bar_fixed > 0 and dia_bar_simply > 0:
                    try:
                        sqrt_term_fixed = math.sqrt(
                            1 - (4.6 * mus * 1e6) / (fck * 1000 * (depth_of_slab ** 2))
                        )
                        ast_fixed = 0.5 * (fck / fy) * (1 - sqrt_term_fixed) * 1000 * depth_of_slab
                        ast_fixed_support_result = f"{ast_fixed:.2f} mm²"

                        sqrt_term_simply = math.sqrt(
                            1 - (4.6 * muc_simply * 1e6) / (fck * 1000 * (depth_of_slab ** 2))
                        )
                        ast_simply = 0.5 * (fck / fy) * (1 - sqrt_term_simply) * 1000 * depth_of_slab
                        ast_simply_supported_result = f"{ast_simply:.2f} mm²"

                        spacing_fixed = (1000 * (math.pi * (dia_bar_fixed ** 2) / 4)) / ast_fixed
                        spacing_simply = (1000 * (math.pi * (dia_bar_simply ** 2) / 4)) / ast_simply
                        reinforcement_spacing_fixed = f"{spacing_fixed:.2f} mm"
                        reinforcement_spacing_simply = f"{spacing_simply:.2f} mm"

                        rounded_spacing_fixed = str(
                            math.floor(spacing_fixed / 50) * 50
                            if spacing_fixed <= 500 else 500
                        ) + " mm"
                        rounded_spacing_simply = str(
                            math.floor(spacing_simply / 50) * 50
                            if spacing_simply <= 500 else 500
                        ) + " mm"

                        actual_ast_fixed = f"{(1000 * (math.pi * (dia_bar_fixed ** 2) / 4)) / float(rounded_spacing_fixed.split()[0]):.3f} mm²"
                        actual_ast_simply = f"{(1000 * (math.pi * (dia_bar_simply ** 2) / 4)) / float(rounded_spacing_simply.split()[0]):.3f} mm²"

                        conclusion_fixed = (
                            f"Provide {dia_bar_fixed} mm dia of bars @ {rounded_spacing_fixed} c/c"
                        )
                        conclusion_simply = (
                            f"Provide {dia_bar_simply} mm dia of bars @ {rounded_spacing_simply} c/c"
                        )

                    except ValueError:
                        ast_fixed_support_result = "Invalid Calculation"
                        ast_simply_supported_result = "Invalid Calculation"
                        reinforcement_spacing_fixed = "N/A"
                        reinforcement_spacing_simply = "N/A"
                        rounded_spacing_fixed = "N/A"
                        rounded_spacing_simply = "N/A"
                        actual_ast_fixed = "N/A"
                        actual_ast_simply = "N/A"
                        conclusion_fixed = "N/A"
                        conclusion_simply = "N/A"
                else:
                    reinforcement_spacing_fixed = "Enter Dia Bar"
                    reinforcement_spacing_simply = "Enter Dia Bar"
                    rounded_spacing_fixed = "Pending Calculation"
                    rounded_spacing_simply = "Pending Calculation"
                    actual_ast_fixed = "Pending Calculation"
                    actual_ast_simply = "Pending Calculation"
                    conclusion_fixed = "Pending Calculation"
                    conclusion_simply = "Pending Calculation"

            # Additional: Distribution Reinforcement Calculations
            # If the user enters a distribution bar diameter (dia_bar_dist), then calculate spacing.
            dia_bar_dist_str = request.form.get("dia_bar_dist", "")
            if dia_bar_dist_str:
                dia_bar_dist = float(dia_bar_dist_str)
                # astd_val (ASTD) is already computed from D above.
                distribution_spacing_val = (1000 * (math.pi * (dia_bar_dist ** 2) / 4)) / astd_val
                if distribution_spacing_val <= 500:
                    distribution_rounded_spacing = f"{math.floor(distribution_spacing_val / 50) * 50} mm"
                else:
                    distribution_rounded_spacing = "500 mm"
                distribution_conclusion = f"Provide {dia_bar_dist} mm dia of bars @ {distribution_rounded_spacing} c/c"
                distribution_spacing = f"{distribution_spacing_val:.2f} mm"
            else:
                distribution_spacing = "Pending Calculation"
                distribution_rounded_spacing = "Pending Calculation"
                distribution_conclusion = "Pending Calculation"

        except ValueError as e:
            result = f"<p style='color:red;'>Invalid input detected: {e}</p>"
        except ZeroDivisionError:
            result = "<p style='color:red;'>Error: Division by zero encountered in calculations.</p>"

    # End of calculations – passing all variables to the template
    return render_template(
        "index.html",
        result=result,
        show_load_inputs=show_load_inputs,
        load_results=load_results,
        table_results=table_results,
        limiting_mr_result=limiting_mr_result,
        ast_fixed_support=ast_fixed_support_result,
        ast_simply_supported=ast_simply_supported_result,
        spacing_fixed=reinforcement_spacing_fixed,
        spacing_simply=reinforcement_spacing_simply,
        rounded_spacing_fixed=rounded_spacing_fixed,
        rounded_spacing_simply=rounded_spacing_simply,
        actual_ast_fixed=actual_ast_fixed,
        actual_ast_simply=actual_ast_simply,
        conclusion_fixed=conclusion_fixed,
        conclusion_simply=conclusion_simply,
        distribution_reinf=distribution_reinf,
        distribution_spacing=distribution_spacing,
        distribution_rounded_spacing=distribution_rounded_spacing,
        distribution_conclusion=distribution_conclusion,
        form_data=form_data  # Pass the form data to the template
    )

if __name__ == "__main__":
    app.run(debug=True)