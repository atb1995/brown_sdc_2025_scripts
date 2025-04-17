"""
Plotting script for figure 2 in the paper
This script loads the true solution and the computed solutions from checkpoint files,
computes the errors, and generates convergence plots for the errors.
The test case is the gravity wave test case.
The script also plots the gravity wave solution at a specific time.
"""

import matplotlib.pyplot as plt
from os.path import abspath, dirname
from firedrake import *
import numpy as np
from netCDF4 import Dataset
import os
import pandas as pd
from tomplot import (set_tomplot_style, plot_convergence,
                     only_minmax_ticklabels, tomplot_legend_ax,
                     tomplot_legend_fig,
                     set_tomplot_style, tomplot_contours, tomplot_cmap,
                     plot_contoured_field, add_colorbar_ax,
                     tomplot_field_title, extract_gusto_coords,
                     extract_gusto_field, apply_gusto_domain)


def load_true_solution(field_name, file_path, dx, dt, file_name):
    true_data_path = os.path.join(file_path+dx+ "_dt_"+dt, file_name)
    print(f"Loading true solution from: {true_data_path}")
    with CheckpointFile(true_data_path, 'r') as afile:

        mesh = afile.load_mesh("firedrake_default_extruded")
        field_true = afile.load_function(mesh, field_name)
        t = afile.get_attr("/", "time")
        step = afile.get_attr("/", "step")
        print(f"Time and Step: {t,step}")
    return field_true, mesh

def compute_errors(field_name, dxs, dts, file_path, file_name, true_data):
    errors = []
    field_true= true_data[0]
    mesh_true = true_data[1]
    for dx, dt in zip(dxs, dts):
        data_path = os.path.join(file_path+dx+ "_dt_"+dt, file_name)
        print(f"Loading data from: {data_path}")
        with CheckpointFile(data_path, 'r') as afile:
            mesh = afile.load_mesh("firedrake_default_extruded")
            field = afile.load_function(mesh, field_name)
            t = afile.get_attr("/", "time")
            step = afile.get_attr("/", "step")
            print(f"Time and Step: {t,step}")
            field_sol = Function(field.function_space())
            field_sol.interpolate(field_true)

            error = errornorm(field, field_sol, mesh=mesh)/norm(field_sol, mesh=mesh)
            errors.append(error)
            print(f"Error: {error}")

    return errors
# ---------------------------------------------------------------------------- #
# Some dummy data
# ---------------------------------------------------------------------------- #
# This should be replaced with your own data if you start from this example!
# This is not actually meaningful data, just some made up numbers
orders = [1, 3, 5]

field_name= "theta"

# ---------------------------------------------------------------------------- #
# Directory for results and plots
# ---------------------------------------------------------------------------- #
# When copying this example these should not be relative to this file
plot_dir = f'{abspath(dirname(__file__))}/'
plot_dir =  "../plots/"
plot_name = f'{plot_dir}/paper_fig_2'
# ---------------------------------------------------------------------------- #
# Data extraction
# ---------------------------------------------------------------------------- #
all_error_data = []
dx_data = []
for order in orders:
    field_path = "../test_cases/results/gravity_wave_imex_sdc_paper_o%s_dx_"%(order)
    true_field_path = "../test_cases/results/gravity_wave_imex_sdc_paper_o%s_dx_"%(order)
    dt_true = "0.15"
    dt_values=       [  "6.0",  "3.0", "1.5", "1.0"]
    if order == 1:
        dx_true = "50.0"
        dt_values=       [  "3.75", "1.875", "0.9375"]
        dx_values =      [  "1250.0", "625.0","312.5"]
        dx_real_values = [ 1250., 625.,312.5]
        data_2 = []
        a = 10000.
        a = 1.0
    elif order == 2:
        dx_true = "100.0"
        dt_values=       [  "3.75", "1.875", "0.9375", "0.46875"]
        dx_values =      [  "1250.0", "625.0","312.5"]
        dx_real_values = [  1250., 625.,312.5]
    elif order == 3:
        dx_true = "200.0"
        dx_values =      [  "5000.0", "2500.0","1250.0"]
        dx_real_values = [  5000.,  2500., 1250.]
        dt_values=       [ "3.75", "1.875", "0.9375"]

    elif order == 5:
        dx_true = "800.0"
        dx_values =      [  "10000.0", "5000.0", "2500.0"]
        dx_real_values = [  10000.,  5000., 2500.]
        dt_values=       [   "1.875", "0.9375", "0.46875"]

    true_sol = load_true_solution(field_name, true_field_path, dx_true, dt_true, "chkpt.h5")
    data= compute_errors(field_name, dx_values, dt_values, field_path, "chkpt.h5", true_sol)
    all_error_data.append(data)
    dx_data.append(dx_real_values)

# ---------------------------------------------------------------------------- #
# Things that should be altered based on the plot
# ---------------------------------------------------------------------------- #
# Three data sets: three colours, markers and labels
colours = ['red', 'blue', 'green']
markers = ["s", "s", "s"]
line_styles = ["-", "-", "-"]
base_labels = ['p = 1', 'p = 3', 'p = 5']
labels1 = [base_label+', gradient =' for base_label in base_labels]
# Convergence plot options that we generally want to use
log_by = 'data'
xlabel = r"$\mathrm{ln}(\Delta x)$"
ylabel = r"$\mathrm{ln}(\left \| \theta_{\Delta t}-\theta_{true} \right \|) \; / \; \mathrm{ln}(\left \| \theta_{true} \right \|)$"
legend_loc = 'lower left'
# ---------------------------------------------------------------------------- #
# Things that are likely the same for all plots
# ---------------------------------------------------------------------------- #
set_tomplot_style()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5), gridspec_kw={'width_ratios': [1, 1.5]})
ax1.set_ylim(bottom=-29, top=-15)
# ---------------------------------------------------------------------------- #
# Plot data
# ---------------------------------------------------------------------------- #
for error_data, dx, colour, marker, label, line_style in \
        zip(all_error_data, dx_data, colours, markers, labels1, line_styles):
    plot_convergence(ax1, dx, error_data, linestyle = line_style, label=label,
                    color=colour, marker=marker, log_by=log_by)


only_minmax_ticklabels(ax1)
tomplot_legend_ax(ax1)
ax1.legend(loc=legend_loc)
ax1.set_xlabel(xlabel)
ax1.set_ylabel(ylabel)

# ---------------------------------------------------------------------------- #
# Plot gravity wave solution
# ---------------------------------------------------------------------------- #
results_dir = "../test_cases/results/skamarock_klemp_nonhydrostatic"

results_file_name = f'{results_dir}/field_output.nc'
# ---------------------------------------------------------------------------- #
# Things that should be altered based on the plot
# ---------------------------------------------------------------------------- #
# Specify lists for variables that are different between subplots
field_names = ['theta_perturbation']
colour_schemes = ['OrRd']
field_labels = [ r"$\theta' \ / $ K"]
# Things that are the same for both subplots
time_idxs = [-1]
contour_method = 'tricontour'
final_contours = np.linspace(-3.0e-3, 3.0e-3, 13)
final_contour_to_remove = 0.0
ylims = [0, 10.0]
x_offset = -3000.0*20/1000.0
xlims = [-x_offset, 300.0-x_offset]
for time_idx in time_idxs:
    # ---------------------------------------------------------------------------- #
    # Things that are likely the same for all plots
    # ---------------------------------------------------------------------------- #
    set_tomplot_style()
    data_file = Dataset(results_file_name, 'r')

    # Loop through subplots
    for i, (field_name, field_label, colour_scheme) in \
        enumerate(zip(field_names, field_labels, colour_schemes)):
        # ------------------------------------------------------------------------ #
        # Data extraction
        # ------------------------------------------------------------------------ #
        field_data = extract_gusto_field(data_file, field_name, time_idx=time_idx)

        coords_X, coords_Y = extract_gusto_coords(data_file, field_name)
        time = data_file['time'][time_idx]
        # Wave has wrapped around periodic boundary, so shift the coordinates
        coords_X = np.where(coords_X < xlims[0], coords_X + 300.0, coords_X)
        # Sort data given the change in coordinates
        data_dict = {
            'X': coords_X,
            'Y': coords_Y,
            'field': field_data
        }
        data_frame = pd.DataFrame(data_dict)
        data_frame.sort_values(by=['X', 'Y'], inplace=True)
        coords_X = data_frame['X'].values[:]
        coords_Y = data_frame['Y'].values[:]
        field_data = data_frame['field'].values[:]

        # ------------------------------------------------------------------------ #
        # Plot data
        # ------------------------------------------------------------------------ #
        cmap, lines = tomplot_cmap(
        final_contours, colour_scheme, remove_contour=final_contour_to_remove
        )
        cf, lines = plot_contoured_field(
        ax2, coords_X, coords_Y, field_data, contour_method, final_contours,
        cmap=cmap, line_contours=lines
        )
        add_colorbar_ax(ax2, cf, field_label, cbar_labelpad=-15)
        ax2.set_ylabel(r'$z$ (km)', labelpad=-20)
        ax2.set_ylim(ylims)
        ax2.set_yticks(ylims)
        ax2.set_yticklabels(ylims)
# ---------------------------------------------------------------------------- #
# Save figure
# ---------------------------------------------------------------------------- #
plot_name_new = plot_name+".png"
print(f'Saving figure to {plot_name_new}')
fig.savefig(plot_name_new, bbox_inches='tight')
plt.close()


