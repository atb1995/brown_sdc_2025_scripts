"""
Plotting script for figure 3 in the paper.
This script plots two solutions of the moist Bryan-Fritsch test case side by side.
The first solution is the one with the LU + FE Qdelta matrices
and the second one is the one with the MIN-SR-FLEX + MIN-SR-NS Qdelta matrices.
"""

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from os.path import abspath, dirname
from tomplot import (set_tomplot_style, tomplot_contours, tomplot_cmap,
                     plot_contoured_field, add_colorbar_ax,
                     tomplot_field_title, extract_gusto_coords,
                     extract_gusto_field, apply_gusto_domain, add_colorbar_fig)
fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey='row')
plot_dir =  "../plots"
plot_name = f'{plot_dir}/paper_fig_3'
dirs = ["moist_bryan_fritsch_imex_sdc","moist_bryan_fritsch_imex_sdc_paralell"]
fig_titles=[r"$Q^{LU}_{\Delta}$ and $Q^{FE}_{\Delta}$",r"$Q^{MIN-SR-FLEX}_{\Delta}$ and $Q^{MIN-SR-NS}_{\Delta}$"]
field_name = 'Theta_e'
colour_scheme = 'Blues'
field_label = r"$\theta_e \ / $ K"
time_idx = -1
contour_method = 'tricontour'
set_tomplot_style()
for i ,(dir, fig_title) in enumerate(zip(dirs, fig_titles)):
    # ---------------------------------------------------------------------------- #
    # Directory for results and plots
    # ---------------------------------------------------------------------------- #
    # When copying this example these should not be relative to this file
    results_dir = f"../test_cases/results/{dir}"
    results_file_name = f'{results_dir}/field_output.nc'

    data_file = Dataset(results_file_name, 'r')

    # ------------------------------------------------------------------------ #
    # Data extraction
    # ------------------------------------------------------------------------ #
    field_data = extract_gusto_field(data_file, field_name, time_idx=time_idx) #- extract_gusto_field(data_file, field_name, time_idx=0)
    coords_X, coords_Z = extract_gusto_coords(data_file, field_name)
    time = data_file['time'][time_idx]
    # ------------------------------------------------------------------------ #
    # Plot data
    # ------------------------------------------------------------------------ #
    contours = np.linspace(319.,325.,13)
    cmap, lines = tomplot_cmap(contours, colour_scheme, remove_contour=320.0)
    cf, _ = plot_contoured_field(ax[i], coords_X, coords_Z, field_data, contour_method,
                                contours, cmap=cmap, line_contours=lines)
    if i == 1:
        add_colorbar_fig(fig, cf, field_label, cbar_labelpad=-15)
    # Stop ylabel being generated for second plot
    ylabel = True if i == 0 else None
    apply_gusto_domain(ax[i], data_file, ylabel=ylabel, xlabelpad=-10, ylabelpad=-20)
    tomplot_field_title(ax[i], fig_title)
# ---------------------------------------------------------------------------- #
# Save figure
# ---------------------------------------------------------------------------- #
plot_name_new = plot_name+"_"+".png"
print(f'Saving figure to {plot_name_new}')
fig.savefig(plot_name_new, bbox_inches='tight')
plt.close()


