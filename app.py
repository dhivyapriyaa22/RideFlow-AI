import streamlit as st
import pickle
import numpy as np
import pandas as pd

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="RideFlow AI",
    page_icon="🚕",
    layout="wide"
)

# -------------------------
# LOAD MODELS
# -------------------------
@st.cache_resource
def load_models():
    demand = pickle.load(open("models/demand.pkl","rb"))
    supply = pickle.load(open("models/supply.pkl","rb"))
    cancel = pickle.load(open("models/cancel.pkl","rb"))
    return demand, supply, cancel

model_demand, model_supply, model_cancel = load_models()

# -------------------------
# CUSTOM CSS (Uber-like)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.metric-box {
    background: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
.big-title {
    font-size: 40px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown('<p class="big-title">🚕 RideFlow AI Dashboard</p>', unsafe_allow_html=True)
st.caption("Smart Demand • Pricing • Cancellation Intelligence")

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.header("⚙️ Ride Controls")

hour = st.sidebar.slider("Hour", 0, 23)
traffic = st.sidebar.selectbox("Traffic", ["Low","Medium","High"])
weather = st.sidebar.selectbox("Weather", ["Clear","Rain","Storm"])
fare = st.sidebar.slider("Base Fare", 50, 500, 150)
eta = st.sidebar.slider("ETA (minutes)", 1, 30, 10)

traffic_val = {"Low":1,"Medium":2,"High":3}[traffic]

# -------------------------
# BUTTON
# -------------------------
if st.sidebar.button("🚀 Run Prediction"):

    # -------------------------
    # MODEL PREDICTIONS
    # -------------------------
    demand = model_demand.predict([[hour]])[0]
    supply = model_supply.predict([[hour]])[0]

    surge = min(max(demand / max(supply,1),1),3)

    cancel_prob = model_cancel.predict_proba(
        [[fare, traffic_val, surge, eta]]
    )[0][1]

    # -------------------------
    # METRICS (TOP)
    # -------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📊 Demand", int(demand))
    col2.metric("🚗 Supply", int(supply))
    col3.metric("💰 Surge", round(surge,2))
    col4.metric("❌ Cancel Risk", f"{round(cancel_prob*100,2)}%")

    # -------------------------
    # CHART
    # -------------------------
    st.subheader("📈 24-Hour Demand vs Supply")

    hours = np.arange(24)
    demand_list = [model_demand.predict([[h]])[0] for h in hours]
    supply_list = [model_supply.predict([[h]])[0] for h in hours]

    df_chart = pd.DataFrame({
        "Hour": hours,
        "Demand": demand_list,
        "Supply": supply_list
    }).set_index("Hour")

    st.line_chart(df_chart)

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.subheader("🧠 AI Insights")

    if surge > 2:
        st.error("🔥 High Surge → Increase drivers immediately")
    elif surge > 1.2:
        st.warning("⚠️ Moderate imbalance detected")
    else:
        st.success("✅ System stable")

    if cancel_prob > 0.7:
        st.error("❌ High cancellation probability")
    elif cancel_prob > 0.4:
        st.warning("⚠️ Medium cancellation risk")
    else:
        st.success("✅ Low cancellation risk")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.caption("Built with AI for Ride Optimization 🚀")