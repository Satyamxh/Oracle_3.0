# page: Batch Processing for further Analysis

# pages/batch.py

"""
this page represents the batch processing

the user can select parameters to fix and free parameters with a range and grid size
"""

import streamlit as st
import numpy as np
import pandas as pd
import itertools
from stqdm import stqdm
from multiprocessing import cpu_count
import altair as alt

# this file is in a folder called pages for streamlit to detect it as a new page
# so functions need to have the file path written

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from batch_runner import run_batch_parallel  

st.set_page_config(page_title="Batch Processor")
st.title("Batch Simulation Processor")
st.sidebar.header("Batch Configuration")
st.sidebar.markdown("Select ranges or fixed values:")

# ========== Parameter Selection UI ==========

def range_input(label, fixed, min_val, max_val, default, step, key, force_float=False):
    use_float = force_float or any(isinstance(v, float) for v in [min_val, max_val, default, step])

    if fixed:
        return [st.sidebar.slider(label, min_val, max_val, default, step=step, key=f"{key}_fixed")]

    min_v = st.sidebar.number_input(
        f"Min {label}",
        float(min_val) if use_float else int(min_val),
        float(max_val) if use_float else int(max_val),
        float(min_val) if use_float else int(min_val),
        step=float(step) if use_float else int(step),
        key=f"{key}_min"
    )

    max_v = st.sidebar.number_input(
        f"Max {label}",
        float(min_val) if use_float else int(min_val),
        float(max_val) if use_float else int(max_val),
        float(max_val) if use_float else int(max_val),
        step=float(step) if use_float else int(step),
        key=f"{key}_max"
    )

    inc = st.sidebar.number_input(
        f"Increment size for {label}",
        float(step) if use_float else int(step),
        float(max_val - min_val) if use_float else int(max_val - min_val),
        float(step) if use_float else int(step),
        step=float(step) if use_float else int(step),
        key=f"{key}_step"
    )

    return list(np.arange(min_v, max_v + inc, inc)) if use_float else list(range(int(min_v), int(max_v) + 1, int(inc)))

# Juror number (M)
fixed_jurors = st.sidebar.checkbox(r"Fix number of jurors ($M$)", value=True)
juror_range = range_input(r"Number of Jurors ($M$)", fixed_jurors, 1, 31, 9, 1, r"$M$", force_float=False)

# Base reward (p)
fixed_p = st.sidebar.checkbox(r"Fix base reward ($p$)", value=True)
p_range = range_input(r"base reward ($p$)", fixed_p, 0.0, 100.0, 33.40, 0.1, r"$p$")

# Deposit (d)
fixed_d = st.sidebar.checkbox(r"Fix deposit ($d$)", value=True)
d_range = range_input(r"deposit ($d$)", fixed_d, 0.0, 100.0, 99.49, 0.1, r"$d$")

# Lambda (QRE)
fixed_lambda = st.sidebar.checkbox(r"Fix $\lambda$ (QRE sensitivity)", value=True)
log_lambda_label = r"log$_{10}(\lambda)$"

if fixed_lambda:
    lambda_val = st.sidebar.slider(log_lambda_label, -3.0, 0.5, value=0.0, step=0.01, key="log_lambda_fixed")
    lambda_range = [10 ** lambda_val]
else:
    min_log = st.sidebar.number_input("Min log$_{10}(\lambda)$", -3.0, 0.5, -3.0, step=0.01, key="log_lambda_min")
    max_log = st.sidebar.number_input("Max log$_{10}(\lambda)$", -3.0, 0.5, 0.5, step=0.01, key="log_lambda_max")
    log_step = st.sidebar.number_input("Step size (log$_{10}(\lambda)$)", 0.01, 1.0, 0.1, step=0.01, key="log_lambda_step")

    lambda_range = [10 ** val for val in np.arange(min_log, max_log + log_step, log_step)]

# Noise
fixed_noise = st.sidebar.checkbox("Fix noise", value=True)
noise_range = range_input("noise", fixed_noise, 0.0, 1.0, 0.1, 0.01, "noise")

# x_mean
fixed_x = st.sidebar.checkbox(r"Fix $x$ (expected coherence)", value=True)
x_range = range_input(r"$x$", fixed_x, 0.0, 1.0, 0.5, 0.01, r"$x$")

# payoff type
payoff_type = st.sidebar.selectbox("Payoff Type", ["Basic", "Redistributive", "Symbiotic"])

# attack_mode
attack_mode = st.sidebar.checkbox(r"Enable p+$\varepsilon$ Attack", value=False)

# epsilon
if attack_mode:
    fixed_epsilon = st.sidebar.checkbox(r"Fix $\varepsilon$ (Bribe amount)", value=True)
    epsilon_range = range_input(r"$\varepsilon$", fixed_epsilon, 0.0, 5.0, 0.0, 0.1, r"$\varepsilon$")

# number of simulations
num_simulations = st.sidebar.number_input("Simulations per combination", 10, 1000, 100, step=10)
st.sidebar.warning("⚠️ Large grids with many parameters and small increments may take a long time.")

epsilon_vals = epsilon_range if attack_mode else [0.0] # makes values 0 if attack_mode is disabled

# ========== Button and Simulation Trigger ==========

if st.sidebar.button("Run Batch Simulation"):
    process=7 # for 8 cpu cores otherwise use more or less
    param_list = []
    for M, p, d, lam, n, x, eps in itertools.product(juror_range, p_range, d_range, lambda_range, noise_range, x_range, epsilon_vals):
        param_list.append({
            "num_jurors": M,
            "p": p,
            "d": d,
            "lambda_qre": lam,
            "noise": n,
            "x_mean": x,
            "payoff_type": payoff_type,
            "attack": attack_mode,
            "epsilon": eps,
            "num_simulations": num_simulations
        })

    total_batches = len(param_list)
    st.info(f"Running {total_batches} batches x {num_simulations} simulations...")

    chunksize = 750  # must match what's used in batch_runner.py
    approx_chunks = (total_batches + chunksize - 1) // chunksize
    st.info(f"Using {process} processes with approx. {approx_chunks} chunks")
    
    # Parallel call

    output_file = "batch_results.csv"
    run_batch_parallel(param_list, processes=process, output_file=output_file)

    # Load only head for preview
    df_preview = pd.read_csv(output_file, nrows=10)
    st.success("Simulations complete")
    st.dataframe(df_preview)

    # Download button
    with open(output_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=output_file, mime="text/csv")

# ========== CSV Upload to analyses results ==========

st.markdown("### Upload CSV File to Analyse Results")
uploaded_file = st.file_uploader("Upload a CSV file from batch results")
if uploaded_file:
    df = pd.read_csv(uploaded_file, low_memory=False)
    st.success("CSV loaded successfully")
    st.dataframe(df.head())

    df = df.rename(columns={"Number of Jurors": "num_jurors"})

    # Filter only valid outcomes once for reuse (removes tie)
    filtered_df = df[df["Majority"].isin(["X", "Y"])]

    # ========== HEATMAP: Majority = X Rate ==========
    majority_rate = (
        filtered_df.groupby(["lambda_qre", "x_mean"])["Majority"]
        .apply(lambda x: (x == "X").mean())
        .reset_index(name="X_win_rate")
    )

    heatmap = alt.Chart(majority_rate).mark_rect().encode(
        x=alt.X("lambda_qre:Q", title="QRE Sensitivity (λ)"),
        y=alt.Y("x_mean:Q", title="Expected Coherence (x)"),
        color=alt.Color("X_win_rate:Q", scale=alt.Scale(scheme="blues"), title="% Majority X"),
        tooltip=["lambda_qre", "x_mean", "X_win_rate"]
    ).properties(title=" Heatmap of X Majority Rate")

    st.altair_chart(heatmap, use_container_width=True)

    # ========== QRE Curve ==========
    avg_qre = (
        df.groupby(["lambda_qre", "x_mean"])["avg_qre_prob_X"]
        .mean()
        .reset_index()
    )

    qre_chart = alt.Chart(avg_qre).mark_line().encode(
        x="lambda_qre:Q",
        y="avg_qre_prob_X:Q",
        color="x_mean:O",
        tooltip=["lambda_qre", "x_mean", "avg_qre_prob_X"]
    ).properties(title="🧠 Average QRE Probability of Voting X")

    st.altair_chart(qre_chart, use_container_width=True)

    # ========== PAYOFF CHART ==========
    payoff_df = (
        df.groupby(["lambda_qre", "payoff_type"])[["avg_payoff_X", "avg_payoff_Y"]]
        .mean()
        .reset_index()
        .melt(id_vars=["lambda_qre", "payoff_type"], var_name="Type", value_name="Payoff")
    )

    payoff_chart = alt.Chart(payoff_df).mark_line().encode(
        x="lambda_qre:Q",
        y="Payoff:Q",
        color="Type:N",
        strokeDash="Type:N",
        tooltip=["lambda_qre", "Payoff", "Type"]
    )

    st.altair_chart(
        payoff_chart.facet("payoff_type:N", columns=1).properties(title=" Avg Payoffs by λ and Payoff Type"),
        use_container_width=True
    )

    # ========== Majority X vs x ==========
    x_majority_by_x = (
        filtered_df.groupby("x_mean")["Majority"]
        .apply(lambda col: (col == "X").mean())
        .reset_index(name="X_majority_rate")
    )

    st.altair_chart(
        alt.Chart(x_majority_by_x).mark_line(point=True).encode(
            x=alt.X("x_mean:Q", title="Expected Coherence (x)"),
            y=alt.Y("X_majority_rate:Q", title="Proportion of Majority = X"),
            tooltip=["x_mean", "X_majority_rate"]
        ).properties(title=" Majority = X vs Expected Coherence (x)"),
        use_container_width=True
    )

    # Compute normalized counts using only filtered outcomes (no Ties)
    outcome_counts = (
        filtered_df["Majority"]
        .value_counts(normalize=True)
        .reset_index(name="Proportion")
        .rename(columns={"index": "Majority"})
    )

    # Ensure type is nominal
    outcome_counts["Majority"] = outcome_counts["Majority"].astype(str)

    # Plot
    outcome_bar = alt.Chart(outcome_counts).mark_bar().encode(
        x="Majority:N",
        y="Proportion:Q",
        color="Majority:N",
        tooltip=["Majority", "Proportion"]
    ).properties(title="Overall Distribution of Majority Outcomes (Excluding Ties)")

    st.altair_chart(outcome_bar, use_container_width=True)

     # ========== Outcome by x ==========
    outcome_dist = (
        filtered_df.groupby(["x_mean", "Majority"])
        .size()
        .reset_index(name="count")
    )
    outcome_dist["total"] = outcome_dist.groupby("x_mean")["count"].transform("sum")
    outcome_dist["proportion"] = outcome_dist["count"] / outcome_dist["total"]

    st.altair_chart(
        alt.Chart(outcome_dist).mark_area().encode(
            x=alt.X("x_mean:Q", title="Expected Coherence (x)"),
            y=alt.Y("proportion:Q", stack="normalize", title="Proportion"),
            color=alt.Color("Majority:N", title="Majority Outcome"),
            tooltip=["x_mean", "Majority", "proportion"]
        ).properties(title=" Distribution of Majority Outcome by x"),
        use_container_width=True
    )

    # Group by jurors and x, calculate rate of majority = X
    juror_heatmap = (
        filtered_df.groupby(["num_jurors", "x_mean"])["Majority"]
        .apply(lambda col: (col == "X").mean())
        .reset_index(name="X_majority_rate")
    )

    st.altair_chart(
        alt.Chart(juror_heatmap).mark_rect().encode(
            x=alt.X("num_jurors:O", title="Number of Jurors"),
            y=alt.Y("x_mean:Q", title="Expected Coherence (x)"),
            color=alt.Color("X_majority_rate:Q", title="% Majority = X", scale=alt.Scale(scheme="greens")),
            tooltip=["num_jurors", "x_mean", "X_majority_rate"]
        ).properties(
            title=" Majority = X Rate by Number of Jurors and x"
        ),
        use_container_width=True
    )


