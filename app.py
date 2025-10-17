import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────
# Page setup
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="MPT Diversification – Two Securities", layout="wide")
st.title("📈 Diversification of Risk – Modern Portfolio Theory (MPT)")

st.markdown("""
Enter or edit **5 years of annual returns (%)** for two securities **S** and **T**.  
You can use the *Watson & Head (2023)* test data or input your own to replicate **Table 8.3**.
""")

# ──────────────────────────────────────────────────────────────
# Step 1 – Input Data
# ──────────────────────────────────────────────────────────────
st.subheader("Step 1 – Input Data")

# Watson & Head test data – Corporate Finance (8th Edition)
watson_head_data = pd.DataFrame({
    "S": [6.6, 5.6, -9.0, 12.6, 14.0],
    "T": [24.5, -5.9, 19.9, -7.8, 14.8]
})

data_choice = st.radio(
    "Choose input mode:",
    ["Use Watson & Head (2023) test data", "Enter my own data"]
)

if data_choice == "Use Watson & Head (2023) test data":
    df = watson_head_data.copy()
else:
    st.write("Edit the spreadsheet below:")
    df = st.data_editor(
        pd.DataFrame({"S": [None]*5, "T": [None]*5}),
        num_rows="fixed",
        use_container_width=True
    )

# ──────────────────────────────────────────────────────────────
# Step 2 – Run Analysis
# ──────────────────────────────────────────────────────────────
if st.button("Run Analysis", type="primary"):
    df = df.dropna()
    df = df.astype(float) / 100  # convert % → decimal

    mean_s, mean_t = df["S"].mean(), df["T"].mean()
    sd_s, sd_t = df["S"].std(ddof=0), df["T"].std(ddof=0)
    corr = df["S"].corr(df["T"])

    st.success("✅ Calculation complete.")

    # Summary Statistics
    st.subheader("Summary Statistics")
    summary = pd.DataFrame({
        "Mean Return": [f"{mean_s*100:.2f}%", f"{mean_t*100:.2f}%"],
        "Standard Deviation": [f"{sd_s*100:.2f}%", f"{sd_t*100:.2f}%"]
    }, index=["S", "T"])
    st.dataframe(summary, use_container_width=True)
    st.metric("Correlation (r)", f"{corr:.2f}")

    # Portfolio weights – Watson & Head pattern
    weights = [(1.0, 0.0), (0.8, 0.2), (0.6, 0.4), (0.4, 0.6), (0.2, 0.8), (0.0, 1.0)]
    labels = ["All S (100/0)", "A (80/20)", "B (60/40)", "C (40/60)", "D (20/80)", "All T (0/100)"]

    results = []
    sd_values = []
    for (w_s, w_t), label in zip(weights, labels):
        port_return = w_s * mean_s + w_t * mean_t
        port_var = w_s**2 * sd_s**2 + w_t**2 * sd_t**2 + 2*w_s*w_t*sd_s*sd_t*corr
        port_sd = np.sqrt(port_var)
        sd_values.append(port_sd)
        results.append([label, f"{port_return*100:.2f}%", f"{port_sd*100:.2f}%"])

    table_df = pd.DataFrame(results, columns=["Portfolio", "Mean Return (%)", "Standard Deviation (%)"])

    # Portfolio Risk & Return Table
    st.subheader("Portfolio Risk and Return Table (Table 8.3 Format)")
    st.dataframe(table_df, use_container_width=True)

    # Efficient Frontier
    st.subheader("Efficient Frontier Graph")
    x = [float(v.strip('%')) for v in table_df["Standard Deviation (%)"]]
    y = [float(v.strip('%')) for v in table_df["Mean Return (%)"]]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(x, y, marker="o")
    for i, row in table_df.iterrows():
        ax.annotate(row["Portfolio"], (x[i], y[i]), fontsize=8)
    ax.set_xlabel("Risk (Standard Deviation %)")
    ax.set_ylabel("Expected Return (%)")
    ax.grid(True)
    st.pyplot(fig)

    # ──────────────────────────────────────────────────────────────
    # Step 3 – Interpret Diversification Benefit
    # ──────────────────────────────────────────────────────────────
    min_portfolio_risk = min(sd_values) * 100
    s_risk_reduction = sd_s * 100 - min_portfolio_risk
    t_risk_reduction = sd_t * 100 - min_portfolio_risk

    st.subheader("Diversification Benefit Analysis")
    st.write(f"Security **S** risk reduced by: **{s_risk_reduction:.2f}%**")
    st.write(f"Security **T** risk reduced by: **{t_risk_reduction:.2f}%**")

    st.info(
        f"📉 Minimum portfolio risk: **{min_portfolio_risk:.2f}%**, compared to "
        f"S risk (**{sd_s*100:.2f}%**) and T risk (**{sd_t*100:.2f}%**). "
        "This confirms that diversification has successfully reduced overall risk."
    )
