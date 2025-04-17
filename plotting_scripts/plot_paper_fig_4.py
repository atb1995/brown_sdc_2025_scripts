"""
Plotting script for figure 4 in the paper
This script plots the temperature and pressure fields for the dry baroclinic channel test case.
"""

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from os.path import abspath, dirname
from tomplot import (set_tomplot_style, tomplot_contours, tomplot_cmap,
                     plot_contoured_field, add_colorbar_ax,
                     tomplot_field_title, extract_gusto_coords,
                     reshape_gusto_data,
                     extract_gusto_vertical_slice,
                     extract_gusto_field, apply_gusto_domain)
def vertical_interpolation(field_data, coords_X, coords_Y, coords_Z, level):
    coords_X = coords_X[:,0]
    coords_Y = coords_Y[:,0]
    field_data_interp = np.zeros((field_data.shape[0],))
    for i in range(field_data.shape[0]):
        field_data_interp[i] = np.interp(level, coords_Z[i, :], field_data[i, :])
    field_data = field_data_interp
    return field_data, coords_X, coords_Y
# ---------------------------------------------------------------------------- #
# Directory for results and plots
# ---------------------------------------------------------------------------- #
# When copying this example these should not be relative to this file
results_dir = "../test_cases/results/dry_baroclinic_channel_imex_sdc"

plot_dir =  "../plots"
results_file_name = f'{results_dir}/field_output.nc'
plot_name = f'{plot_dir}/paper_fig_4'
# ---------------------------------------------------------------------------- #
# Things that should be altered based on the plot
# ---------------------------------------------------------------------------- #
# Specify lists for variables that are different between subplots
field_names = ['Temperature','Pressure_Vt']
colour_schemes = ['Greens','Greens']
field_labels = [ r"$T \ / $ K",r"$P \ / $ Pa"]

# Things that are the same for both subplots
time_idxs = [-1]
levels = [0]
contour_method = 'tricontour'
fig, ax = plt.subplots(2, 1, figsize=(30, 15), sharey='row')
for time_idx in time_idxs:
    for level in levels:
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
            field_data = extract_gusto_field(data_file, field_name, time_idx=time_idx) #- extract_gusto_field(data_file, field_name, time_idx=0)
            coords_X, coords_Y, coords_Z = extract_gusto_coords(data_file, field_name)
            field_data_new, coords_X, coords_Y, coords_Z = reshape_gusto_data(field_data, coords_X, coords_Y, coords_Z,
                        other_arrays=None)
            if (field_name=='Temperature'):
                level_val = level
            else:
                level_val = level

            time = data_file['time'][time_idx]
            z = 0.5
            field_data, coords_X, coords_Y = vertical_interpolation(field_data_new, coords_X, coords_Y, coords_Z, z)
            # ------------------------------------------------------------------------ #
            # Plot data
            # ------------------------------------------------------------------------ #
            contours = tomplot_contours(field_data)
            # print(contours)
            if field_name == 'Temperature':
                contours = np.linspace(268, 306, 20)
            else:
                contours = np.linspace(92600, 95800, 17)
            cmap, lines = tomplot_cmap(contours, colour_scheme)
            cf, _ = plot_contoured_field(ax[i], coords_X, coords_Y, field_data, contour_method,
                                        contours, cmap=cmap, line_contours=lines)
            add_colorbar_ax(ax, cf, field_label, cbar_labelpad=-15)
            # Stop ylabel being generated for second plot
            ylabel = True if i == 0 else None

            ax[i].set_ylabel('y / m')
        # ---------------------------------------------------------------------------- #
        # Save figure
        # ---------------------------------------------------------------------------- #
        ax[1].set_xlabel('x / m')
        plot_name_new = plot_name+".png"
        print(f'Saving figure to {plot_name_new}')
        fig.savefig(plot_name_new, bbox_inches='tight')
        plt.close()


