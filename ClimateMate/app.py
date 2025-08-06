import streamlit as st
import matplotlib.pyplot as plt
import json
import os
from together import Together

# -----------------------
# CONFIGURATION
# -----------------------
TOGETHER_API_KEY = "b9e71cfd72d3d70dc0b33a602128fe313ac70b585b4d4eefec3fb6d63a3219c0"  # <-- Replace with your key
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
client = Together(api_key=TOGETHER_API_KEY)
DATA_FILE = "climate_history.json"

# -----------------------
# DATA FUNCTIONS
# -----------------------
def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history, f, indent=2)

# -----------------------
# FOOTPRINT CALCULATION
# -----------------------
def calculate_footprint(transport_km, electricity_kwh, meat_meals):
    transport_emission = transport_km * 0.12 * 52 / 1000    # tons CO2/year
    electricity_emission = electricity_kwh * 0.233 * 12 / 1000
    food_emission = meat_meals * 0.007 * 365 / 1000
    total = transport_emission + electricity_emission + food_emission
    return transport_emission, electricity_emission, food_emission, total

# -----------------------
# AI RECOMMENDATIONS
# -----------------------
def get_ai_recommendations(total, t, e, f, region, goal):
    prompt = (
        f"My annual carbon footprint is {total:.2f} tons CO2.\n"
        f"- Transport: {t:.2f} tons\n"
        f"- Electricity: {e:.2f} tons\n"
        f"- Food: {f:.2f} tons\n"
        f"I live in {region}.\n"
        f"My goal is to reduce my footprint by {goal}% in the next 6 months.\n"
        "Give a detailed, step-by-step action plan with estimated CO2 and cost savings. "
        "End your response with a clear summary of how these actions will help me reach my goal."
    )
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful climate action assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800  # Increased to prevent truncation
    )
    return response.choices[0].message.content

# -----------------------
# STREAMLIT APP
# -----------------------
st.title("Advanced Climate Action AI Agent")
st.write("Track your carbon footprint, set reduction goals, and get region‑specific AI advice.")

# Step 1. User inputs
st.header("Step 1: Enter Your Details")
region = st.text_input("Your Country or City", "India")
goal_percent = st.slider("Reduction Goal (%)", 5, 50, 20)
transport_km = st.number_input("Average car/bike travel per week (km)", min_value=0, value=50)
electricity_kwh = st.number_input("Average electricity usage per month (kWh)", min_value=0, value=150)
meat_meals = st.number_input("Number of non-veg meals per week", min_value=0, value=5)

if st.button("Calculate & Get Action Plan"):
    # Step 2. Calculate footprint
    transport_emission, electricity_emission, food_emission, total = calculate_footprint(
        transport_km, electricity_kwh, meat_meals
    )

    # Step 3. Store history
    history = load_history()
    history.append({"total": total})
    save_history(history)

    # Step 4. Show breakdown
    st.subheader("Your Estimated Carbon Footprint")
    st.write(f"**Total:** {total:.2f} tons CO₂/year")
    st.write(f"- Transport: {transport_emission:.2f} tons")
    st.write(f"- Electricity: {electricity_emission:.2f} tons")
    st.write(f"- Food: {food_emission:.2f} tons")

    # Step 5. Show chart
    labels = ['Transport', 'Electricity', 'Food']
    values = [transport_emission, electricity_emission, food_emission]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=["#4CAF50", "#2196F3", "#FF9800"])
    ax.set_ylabel("Tons CO₂/year")
    ax.set_title("Your Carbon Footprint Breakdown")
    st.pyplot(fig)

    # Step 6. Show progress chart if history exists
    if len(history) > 1:
        st.subheader("Your Progress Over Time")
        totals = [h["total"] for h in history]
        fig2, ax2 = plt.subplots()
        ax2.plot(range(1, len(totals)+1), totals, marker='o', color="#673AB7")
        ax2.set_xlabel("Session")
        ax2.set_ylabel("Total CO₂ (tons/year)")
        ax2.set_title("Footprint Trend")
        st.pyplot(fig2)

    # Step 7. AI Recommendations
    st.subheader("AI Action Plan (Region‑Specific)")
    advice = get_ai_recommendations(total, transport_emission, electricity_emission, food_emission, region, goal_percent)
    st.write(advice)
