import streamlit as st
import requests

import os

API_URL = os.getenv("API_URL", "https://ai-fitness-backend-9x8z.onrender.com")

st.set_page_config(page_title="AI Fitness Tracker", page_icon="💪", layout="centered")
st.title("💪 AI Fitness & Diet Recommendation System")

# ==========================================
# RENDER COLD START HANDLING
# ==========================================
# Ping the backend in the background to wake it up if it's on a free Render tier.
try:
    # Try to ping with a very short timeout (e.g., 2 seconds)
    # If the backend is awake, it will respond instantly.
    # If it's asleep, the request will timeout, and we know we need to show a warning.
    requests.get(f"{API_URL}/all-users", timeout=2, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"})
except requests.exceptions.Timeout:
    st.warning("⏳ Our servers are waking up from sleep! Your first request might take 1-2 minutes to complete. Please be patient.", icon="⚠️")
except requests.exceptions.RequestException:
    # Ignore other connection errors here, let the actual forms handle them
    pass

tab1, tab2, tab3 = st.tabs(["🆕 Create Profile", "🔄 Update My Stats", "🍽️ Get Diet Plan"])

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
            response = requests.post(f"{API_URL}/health-report", json=payload, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"})

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
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                except Exception:
                    error_detail = f"Server returned {response.status_code}: {response.text}"
                st.error(f"Error: {error_detail}")


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
                    f"{API_URL}/update-report/{update_email}", json=update_payload, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
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
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                    except Exception:
                        error_detail = f"Server returned {response.status_code}: {response.text}"
                    st.error(f"Error: {error_detail}")


# ==========================================
# TAB 3: GET DIET PLAN
# ==========================================
with tab3:
    st.write("Generate a personalized diet plan based on your calculated macros!")

    plan_email = st.text_input("Your Registered Email", key="plan_email")

    with st.form("diet_plan_form"):
        col1, col2 = st.columns(2)
        with col1:
            diet_pref = st.selectbox(
                "Dietary Preference",
                ["veg", "non_veg", "vegan"],
                format_func=lambda x: x.replace("_", "-").title(),
            )
        with col2:
            duration = st.selectbox(
                "Plan Duration",
                ["1_day", "1_week"],
                format_func=lambda x: x.replace("_", " ").title(),
            )

        generate_submitted = st.form_submit_button("Generate Diet Plan 🍱")

    if generate_submitted:
        if not plan_email:
            st.warning("Please enter your email first!")
        else:
            with st.spinner("Our AI Nutritionist is crafting your plan. This may take a few seconds..."):
                payload = {
                    "diet_preference": diet_pref,
                    "plan_duration": duration,
                }
                
                response = requests.post(
                    f"{API_URL}/diet-plan/{plan_email}", json=payload, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
                )

                if response.status_code == 200:
                    plan_data = response.json()
                    st.success("Diet Plan Generated Successfully! 🎉")
                    
                    for day_plan in plan_data.get("days", []):
                        with st.expander(f"📅 Day {day_plan['day']}", expanded=(duration == "1_day")):
                            meals = day_plan.get("meals", {})
                            
                            for meal_type, meal_info in meals.items():
                                st.markdown(f"**{meal_type.title()}**: {meal_info['name']}")
                                st.caption(meal_info['description'])
                                
                                m1, m2, m3, m4 = st.columns(4)
                                m1.metric("Calories", f"{meal_info['calories']} kcal")
                                m2.metric("Protein", f"{meal_info['protein_g']}g")
                                m3.metric("Fat", f"{meal_info['fat_g']}g")
                                m4.metric("Carbs", f"{meal_info['carbs_g']}g")
                                st.divider()
                                
                            daily_total = day_plan.get("daily_total", {})
                            st.info(f"**Daily Total**: {daily_total.get('calories', 0)} kcal | Protein: {daily_total.get('protein_g', 0)}g | Fat: {daily_total.get('fat_g', 0)}g | Carbs: {daily_total.get('carbs_g', 0)}g")

                else:
                    try:
                        error_detail = response.json().get('detail', 'Unknown error')
                    except Exception:
                        error_detail = f"Server returned {response.status_code}: {response.text}"
                    st.error(f"Error: {error_detail}")
