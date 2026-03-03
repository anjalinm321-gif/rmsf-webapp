import streamlit as st
import MDAnalysis as mda
import numpy as np
import plotly.graph_objects as go

st.title("Protein RMSF Interactive Plot Generator")
st.write("Upload one or more PARM7 and AGR files")

# Upload multiple files
parm7_files = st.file_uploader("Upload PARM7 files", type=["parm7"], accept_multiple_files=True)
agr_files = st.file_uploader("Upload AGR RMSF files", type=["agr"], accept_multiple_files=True)

if parm7_files and agr_files:

    if len(parm7_files) != len(agr_files):
        st.error("Number of PARM7 files must match number of AGR files.")
    else:

        for i in range(len(parm7_files)):

            st.subheader(f"RMSF Plot {i+1}")

            # Load topology
            u = mda.Universe(parm7_files[i])
            calphas = u.select_atoms("protein and name CA")

            resids = calphas.resids
            resnames = calphas.resnames
            labels = [f"{resnames[j]}{resids[j]}" for j in range(len(resids))]

            # Read RMSF
            rmsf_values = []
            for line in agr_files[i]:
                line = line.decode("utf-8")
                if not line.startswith(("@", "#")):
                    parts = line.split()
                    if len(parts) == 2:
                        rmsf_values.append(float(parts[1]))

            rmsf_values = np.array(rmsf_values)

            # Find highest residue
            max_index = np.argmax(rmsf_values)
            max_residue = labels[max_index]
            max_value = rmsf_values[max_index]

            st.write(f"Highest Fluctuating Residue: **{max_residue}** → {round(max_value, 2)} Å")

            # Plot
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=labels,
                y=rmsf_values,
                mode='lines+markers',
                name='RMSF'
            ))

            fig.add_trace(go.Scatter(
                x=[labels[max_index]],
                y=[max_value],
                mode='markers+text',
                marker=dict(size=12, color='red'),
                text=[max_residue],
                textposition="top center",
                name='Highest RMSF'
            ))

            fig.update_layout(
                title=f"Interactive Residue-wise Cα RMSF ({parm7_files[i].name})",
                xaxis_title="Residue Name",
                yaxis_title="RMSF (Å)",
                xaxis=dict(tickangle=90),
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)