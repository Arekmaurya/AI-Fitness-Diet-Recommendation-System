import streamlit as st
import requests

API_URL = "http://backend:8000"

st.set_page_config(page_title="AI Fitness Tracker", page_icon="💪", layout="centered")
st.title("💪 AI Fitness & Diet Recommendation System")

tab1, tab2 = st.tabs(["🆕 Create Profile", "🔄 Update My Stats"])

# ==========================================
# TAB 1: CREATE NEW USER
# ==========================================
with tab1:
    st.write("Enter your details to generate your custom health report!")
    with st.form("create_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email (Gmail only)")
            age = st.number_input("Age", min_value=1, max_value=120, value=25)
            gender = st.selectbox("Gender", ["male", "female"])
        with col2:
            height = st.number_input(
                "Height (cm)", min_value=50.0, max_value=300.0, value=170.0
            )
            weight = st.number_input(
                "Weight (kg)", min_value=20.0, max_value=300.0, value=70.0
            )
            activity = st.selectbox(
                "Activity Level",
                ["sedentary", "light", "moderate", "active", "very_active"],
            )
            goal = st.selectbox(
                "Fitness Goal", ["fat_loss", "maintenance", "muscle_gain"]
            )

        submitted = st.form_submit_button("Generate Report 🚀")

    if submitted:
        payload = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "height": height,
            "weight": weight,
            "activity": activity,
            "goal": goal,
        }
        with st.spinner("Calculating..."):
            response = requests.post(f"{API_URL}/health-report", json=payload)

            if response.status_code == 200:
                data = response.json()
                st.success("Profile Created! Check your metrics below.")

                # --- DISPLAY RESULTS USING THE NEW NESTED KEYS ---
                st.divider()
                st.subheader(f"📊 Results for {data['profile']['name']}")

                m1, m2, m3 = st.columns(3)
                m1.metric("BMI", data["metrics"]["bmi"])
                m2.metric("BMI Category", data["metrics"]["bmi_category"])
                m3.metric(
                    "Daily Calories", f"{data['metrics']['recommended_calories']} kcal"
                )

                st.write("### 🥑 Recommended Daily Macros")
                mac1, mac2, mac3 = st.columns(3)
                mac1.metric("Protein", f"{data['metrics']['macros']['protein_g']} g")
                mac2.metric("Fats", f"{data['metrics']['macros']['fat_g']} g")
                mac3.metric("Carbs", f"{data['metrics']['macros']['carbs_g']} g")

                st.caption(f"Profile created at: {data['account']['created_at']}")

            else:
                st.error(f"Error: {response.json().get('detail')}")


# ==========================================
# TAB 2: UPDATE EXISTING USER
# ==========================================
with tab2:
    st.write(
        "Log in with your email to update your current weight, activity, or goals!"
    )

    update_email = st.text_input("Your Registered Email", key="update_email")

    with st.form("update_form"):
        st.caption(
            "Only fill out the fields you want to change. Leave the rest exactly as they are."
        )

        new_weight = st.number_input(
            "New Weight (kg) - Leave as 0.0 if unchanged",
            min_value=0.0,
            max_value=300.0,
            value=0.0,
        )
        new_activity = st.selectbox(
            "New Activity Level",
            ["Unchanged", "sedentary", "light", "moderate", "active", "very_active"],
        )
        new_goal = st.selectbox(
            "New Fitness Goal", ["Unchanged", "fat_loss", "maintenance", "muscle_gain"]
        )

        update_submitted = st.form_submit_button("Update My Report 🔄")

    if update_submitted:
        if not update_email:
            st.warning("Please enter your email first!")
        else:
            update_payload = {}
            if new_weight > 0:
                update_payload["weight"] = new_weight
            if new_activity != "Unchanged":
                update_payload["activity"] = new_activity
            if new_goal != "Unchanged":
                update_payload["goal"] = new_goal

            with st.spinner("Recalculating your metrics..."):
                response = requests.put(
                    f"{API_URL}/update-report/{update_email}", json=update_payload
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Successfully updated! Here are your new metrics:")

                    # --- DISPLAY UPDATED RESULTS USING NESTED KEYS ---
                    m1, m2, m3 = st.columns(3)
                    m1.metric("New BMI", data["metrics"]["bmi"])
                    m2.metric(
                        "New Daily Calories",
                        f"{data['metrics']['recommended_calories']} kcal",
                    )
                    m3.metric(
                        "Protein Goal", f"{data['metrics']['macros']['protein_g']} g"
                    )

                    st.caption(f"Last updated at: {data['account']['updated_at']}")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
