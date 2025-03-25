from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        value1 = request.form.get("input_value1")
        value2 = request.form.get("input_value2")
        if value1 and value2:  # Ensure both inputs are provided
            try:
                result = int(value1) + int(value2)  # Convert to integers and add
            except ValueError:
                result = "Invalid input. Please enter numbers only."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
