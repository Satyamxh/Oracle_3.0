# page: Batch Processing for further Analysis

# pages/batch.py

"""
this page represents the batch processing

the user can select parameters to fix and free parameters with a range and grid size
"""

import streamlit as st
import numpy as np

# st.set_page_config(page_title="Batch Processor")

st.title("Batch Simulation Processor")

st.sidebar.header("Batch Configuration")

# Sidebar controls specific to batch logic
st.sidebar.markdown("Select ranges or fixed values:")

# fixed/flexible sidebar

# number of jurors (M)
fixed_jurors = st.sidebar.checkbox(r"Fix number of jurors ($M$)", value=True)

if fixed_jurors:
    juror_range = [st.sidebar.slider(r"Number of Jurors $M$", 3, 51, 9, step=1)]
else:
    min_jurors = st.sidebar.number_input(r"Min jurors ($M$)", 3, 51, 3, step=1)
    max_jurors = st.sidebar.number_input(r"Max jurors ($M$)", min_jurors, 51, 21, step=1)
    step_jurors = st.sidebar.number_input(r"increment size for ($M$)", 1, 10, 2, step=1)
    juror_range = list(range(min_jurors, max_jurors + 1, step_jurors))

# base reward (p)
fixed_p = st.sidebar.checkbox(r"Fix base reward ($p$)", value=True)

if fixed_p:
    p_range = [st.sidebar.slider(r"Base reward ($p$)", 0.0, 5.0, 1.0, step=0.1)]
else:
    min_p = st.sidebar.number_input(r"Min base reward ($p$)", 0.0, 5.0, 0.5, step=0.1)
    max_p = st.sidebar.number_input(r"Max base reward ($p$)", 0.0, 5.0, 1.5, step=0.1)
    step_p = st.sidebar.number_input(r"increment size for $p$", 0.01, 1.0, 0.1, step=0.01)
    p_range = list(np.arange(min_p, max_p + step_p, step_p))

# deposit (d)
fixed_d = st.sidebar.checkbox(r"Fix deposit ($d$)", value=True)
if fixed_d:
    d_range = [st.sidebar.slider(r"Deposit ($d$)", 0.0, 5.0, 0.0, step=0.1)]
else:
    min_d = st.sidebar.number_input(r"Min $d$", 0.0, 5.0, 0.0)
    max_d = st.sidebar.number_input(r"Max $d$", 0.0, 5.0, 1.0)
    step_d = st.sidebar.number_input(r"increment size for $d$", 0.01, 1.0, 0.1)
    d_range = list(np.arange(min_d, max_d + step_d, step_d))

# Lambda (QRE)
fixed_lambda = st.sidebar.checkbox(r"Fix $\lambda$ (QRE sensitivity)", value=True)
if fixed_lambda:
    lambda_range = [st.sidebar.slider(r"$\lambda$", 0.1, 5.0, 1.5, step=0.1)]
else:
    min_l = st.sidebar.number_input(r"Min $\lambda$", 0.1, 5.0, 1.0)
    max_l = st.sidebar.number_input(r"Max $\lambda$", 0.1, 5.0, 2.0)
    step_l = st.sidebar.number_input(r"increment size for $\lambda$", 0.01, 1.0, 0.1)
    lambda_range = list(np.arange(min_l, max_l + step_l, step_l))

# Noise
fixed_noise = st.sidebar.checkbox("Fix noise", value=True)
if fixed_noise:
    noise_range = [st.sidebar.slider("Noise", 0.0, 1.0, 0.1, step=0.01)]
else:
    min_n = st.sidebar.number_input("Min noise", 0.0, 1.0, 0.1)
    max_n = st.sidebar.number_input("Max noise", 0.0, 1.0, 0.3)
    step_n = st.sidebar.number_input("increment size for noise", 0.001, 1.0, 0.01)
    noise_range = list(np.arange(min_n, max_n + step_n, step_n))

# x_mean
fixed_x = st.sidebar.checkbox(r"Fix $x$ (expected coherence)", value=True)
if fixed_x:
    x_range = [st.sidebar.slider(r"$x$", 0.0, 1.0, 0.5, step=0.01)]
else:
    min_x = st.sidebar.number_input(r"Min $x$", 0.0, 1.0, 0.4)
    max_x = st.sidebar.number_input(r"Max $x$", 0.0, 1.0, 0.6)
    step_x = st.sidebar.number_input(r"increment size for $x$", 0.001, 1.0, 0.01)
    x_range = list(np.arange(min_x, max_x + step_x, step_x))

payoff_type = st.sidebar.selectbox("Payoff Type", ["Basic", "Redistributive", "Symbiotic"])

num_simulations = st.sidebar.number_input("Simulations per combination", 10, 1000, 100, step=10)
st.sidebar.warning("⚠️ Large grids with many free parameters and small increment sizes may take a long time.")

if st.sidebar.button("Run Batch Simulation"):
    st.write(" Running simulations... (This will be implemented)")
    # Your batch simulation logic goes here
else:
    st.info("Set parameters and click 'Run Batch Simulation' to begin.")

# Optional: CSV upload for analysis
st.markdown("### Upload CSV File to Analyze Results")
uploaded_file = st.file_uploader("Upload a CSV file from batch results")

if uploaded_file:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    st.success("CSV loaded successfully!")
    st.dataframe(df.head())
