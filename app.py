##############################################################
###                                                        ###
###  This Code was developed by Toluwase H. Fatoki         ###
###  Linkedin: https://www.linkedin.com/in/hezekiahfatoki  ###
###                                                        ###
##############################################################


from flask import Flask, render_template, request, flash
import json, requests, time, re

app = Flask(__name__)
app.secret_key = "secret_key_for_flask_session"

SUBMIT_URL = "https://script.google.com/macros/s/AKfycbwK-HLLx3NsxzbzEap-77pyr9Ez8jYZdQDdy4gi3-XEVgYs4qQShsk3IzqxSVZh4sjucw/exec"

# Load JSON form definition
with open("applied_bioinformatics_form.json") as f:
    form_json = json.load(f)

REQUIRED_FIELDS = [
    "Full Name",
    "Email Address",
    "WhatsApp Number",
    "University Attended",
    "Statement of Interest: Why do you want to join this mentorship program? (max. 200 words)",
    "Are you able to commit to the mentorship, training sessions, and collaborative research project?",
    "Age",
    "Gender"
]

A_T = "g2026thf8816"

def validate_form(data):
    missing = [f for f in REQUIRED_FIELDS if f not in data or not str(data[f]).strip()]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["Email Address"]):
        return False, "Invalid email format."

    # WhatsApp number validation
    if not re.match(r"^\+?\d{8,}$", data["WhatsApp Number"]):
        return False, "Invalid WhatsApp number. Use digits only, at least 8 digits."

    # Commitment check
    if data["Are you able to commit to the mentorship, training sessions, and collaborative research project?"].lower() != "yes":
        return False, "You must confirm commitment (Yes) to apply."

    # Age validation
    try:
        age = int(data["Age"])
        if age <= 0:
            return False, "Age must be a positive number."
    except ValueError:
        return False, "Age must be a number."

    # Gender validation
    if data["Gender"].lower() not in ["male", "female"]:
        return False, "Gender must be Male, Female."

    return True, ""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form_data = {}

        # Collect form values
        for item in form_json['items']:
            key = item['title']
            form_data[key] = request.form.get(key, "").strip()

        valid, msg = validate_form(form_data)
        if not valid:
            flash(msg, "error")
            return render_template("form.html", form=form_json['items'], values=form_data, A_T=A_T)

        # Add token and tracking ID
        form_data["auth_token"] = A_T
        timestamp = time.strftime("%Y%m%d%H%M%S")
        first_name = form_data.get("Full Name", "Applicant").split()[0]
        tracking_id = f"{first_name}_{timestamp}"
        form_data["Tracking ID"] = tracking_id

        # Submit to Google Apps Script
        try:
            r = requests.post(SUBMIT_URL, json=form_data)
            if r.status_code != 200:
                flash(f"Submission failed: {r.text}", "error")
                return render_template("form.html", form=form_json['items'], values=form_data, A_T=A_T)
        except Exception as e:
            flash(f"Submission error: {e}", "error")
            return render_template("form.html", form=form_json['items'], values=form_data, A_T=A_T)

        # Render success page with tracking ID
        return render_template("success.html", tracking_id=tracking_id)

    return render_template("form.html", form=form_json['items'], values={}, A_T=A_T)

if __name__ == "__main__":
    app.run(debug=True)
