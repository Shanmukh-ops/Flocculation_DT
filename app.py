import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Hydraulic Flocculator Digital Twin", layout="wide")

st.title("Hydraulic Flocculator Digital Twin (Demo GUI)")

# -----------------------------
# Sidebar Inputs
# -----------------------------
st.sidebar.header("Inlet Inputs")

U_in = st.sidebar.slider("Inlet Velocity U_in (m/s)", 0.1, 1.0, 0.4, 0.01)
C_in = st.sidebar.slider("Inlet Concentration C_in (mg/L)", 10, 500, 200, 5)

st.sidebar.header("Simulation Settings")
t_end = st.sidebar.slider("Simulation Time (s)", 10, 120, 60, 5)
dt = st.sidebar.selectbox("Time Step (s)", [0.1, 0.2, 0.5, 1.0], index=1)

run_pred = st.sidebar.button("Predict Outlet Response")

# -----------------------------
# Dummy Transient Data Generator
# -----------------------------
time = np.arange(0, t_end + dt, dt)

# Dummy response behavior (only for GUI demo)
G_out = 50 + 500*(U_in) * (1 - np.exp(-time/10))
d32_out = 1e-6 + (U_in * 10e-6) * (1 - np.exp(-time/15))
d43_out = 2e-6 + (U_in * 15e-6) * (1 - np.exp(-time/18))

# Add effect of concentration
d32_out = d32_out * (1 + 0.001 * (C_in/10))
d43_out = d43_out * (1 + 0.0015 * (C_in/10))

# -----------------------------
# PSD Curves (Dummy)
# -----------------------------
bins = np.arange(1, 21)
diameters = np.logspace(-6, -3, 20)  # 1 micron to 1000 micron (in meters)

# inlet PSD (peak at small sizes)
inlet_psd = np.exp(-((np.log10(diameters) - np.log10(3e-6))**2) / (2*(0.25**2)))
inlet_psd = inlet_psd / inlet_psd.sum()

# outlet PSD (shift right depending on velocity and concentration)
shift_factor = 1 + 2.5*(U_in-0.1) + 0.002*(C_in-10)
outlet_center = 3e-6 * shift_factor

outlet_psd = np.exp(-((np.log10(diameters) - np.log10(outlet_center))**2) / (2*(0.30**2)))
outlet_psd = outlet_psd / outlet_psd.sum()

# -----------------------------
# Main Display
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Outlet Velocity Gradient (G_out vs Time)")
    fig, ax = plt.subplots()
    ax.plot(time, G_out)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("G_out (1/s)")
    ax.grid(True)
    st.pyplot(fig)

with col2:
    st.subheader("Mean Diameters vs Time")
    fig, ax = plt.subplots()
    ax.plot(time, d32_out * 1e6, label="d32_out (µm)")
    ax.plot(time, d43_out * 1e6, label="d43_out (µm)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Diameter (µm)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

st.subheader("Particle Size Distribution (Inlet vs Outlet)")

fig, ax = plt.subplots()
ax.plot(diameters * 1e6, inlet_psd, marker="o", label="Inlet PSD")
ax.plot(diameters * 1e6, outlet_psd, marker="o", label="Outlet PSD")
ax.set_xscale("log")
ax.set_xlabel("Particle Diameter (µm)")
ax.set_ylabel("Bin Fraction")
ax.legend()
ax.grid(True, which="both")
st.pyplot(fig)

# -----------------------------
# Display Final Values
# -----------------------------
st.subheader("Final Outlet Values (at last timestep)")
st.write(f"**Final G_out:** {G_out[-1]:.2f} 1/s")
st.write(f"**Final d32_out:** {d32_out[-1]*1e6:.3f} µm")
st.write(f"**Final d43_out:** {d43_out[-1]*1e6:.3f} µm")

# -----------------------------
# Table Output
# -----------------------------
st.subheader("Outlet PSD Table (Bin Fractions)")
st.write("This is the predicted outlet bin fraction distribution:")

psd_table = {
    "Bin": bins,
    "Diameter (µm)": diameters * 1e6,
    "Inlet Fraction": inlet_psd,
    "Outlet Fraction": outlet_psd
}

st.dataframe(psd_table)
