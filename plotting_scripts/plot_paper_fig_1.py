"""
Plotting script for the paper figure 1.
This script loads the true solution and the computed solutions from checkpoint files,
computes the errors, and generates convergence plots for the errors.
The test case is the Williamson 1 advection problem on the sphere.
"""
from firedrake import *
import matplotlib.pyplot as plt
import numpy as np
import os


def load_true_solution(file_path, true_data_name, file_name):
    true_data_path = os.path.join(file_path, true_data_name, file_name)
    print(f"Loading true solution from: {true_data_path}")
    with CheckpointFile(true_data_path, 'r') as afile:
        mesh = afile.load_mesh("firedrake_default")
        D_true = afile.load_function(mesh, "D")
        u_true = afile.load_function(mesh, "u")
        t = afile.get_attr("/", "time")
        step = afile.get_attr("/", "step")
        print(f"TIme and Step: {t,step}")
    return D_true, u_true, mesh

def compute_errors(data_names, file_path, file_name, true_data):
    errors_D = []
    errors_u = []
    D_true= true_data[0]
    u_true = true_data[1]
    mesh_true = true_data[2]

    for scheme_data_names in data_names:
        error_D_scheme = []
        error_u_scheme = []

        for data_name in scheme_data_names:
            data_path = os.path.join(file_path, data_name, file_name)
            print(f"Loading data from: {data_path}")
            with CheckpointFile(data_path, 'r') as afile:
                mesh = afile.load_mesh("firedrake_default")
                D = afile.load_function(mesh, "D")
                u = afile.load_function(mesh, "u")
                t = afile.get_attr("/", "time")
                step = afile.get_attr("/", "step")
                print(f"TIme and Step: {t,step}")
                D_sol = Function(D.function_space())
                u_sol = Function(u.function_space())
                D_sol.dat.data[:] = D_true.dat.data[:]
                u_sol.dat.data[:] = u_true.dat.data[:]

                error_D = errornorm(D_sol, D, mesh=mesh)/ norm(D_sol, mesh=mesh)
                error_u = errornorm(u_sol, u, mesh=mesh)/ norm(u_sol, mesh=mesh)
                error_D_scheme.append(error_D)
                error_u_scheme.append(error_u)
                print(f"Error D: {error_D}, Error u: {error_u}")

        errors_D.append(error_D_scheme)
        errors_u.append(error_u_scheme)

    return errors_D, errors_u

def plot_errors(dts, errors_D, scheme_names, fig_title, cols,ticks):
    fig, ax = plt.subplots()
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["figure.dpi"] = 300
    for i, (scheme_name, error_D) in enumerate(zip(scheme_names, errors_D)):
        x = np.log(dts)
        y = np.log(error_D)
        ax.scatter(x, y, label=scheme_name, color=cols[i], marker=ticks[i])

        # Calculate and plot best fit line
        if (i==2):
            slope, intercept = np.polyfit(x, y, 1)
        else:
            slope, intercept = np.polyfit(x, y, 1)
        print(f"Slope: {slope}, Intercept: {intercept}")
        ax.plot(x, slope * x + intercept, color=cols[i], label=f'{scheme_name} (slope={slope:.2f})', marker='None', linewidth=1.5)

    ax.set_xlabel(r'$\mathrm{ln}(\Delta t)$', fontsize=12)
    ax.set_ylabel(r'$\mathrm{ln}(\left \| D_{\Delta t}-D_{true} \right \|)$', fontsize=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(scheme_names), labelspacing=0.1, fontsize='small')
    plt.tight_layout()
    plt.subplots_adjust(left=0.2, right=0.8)
    plt.legend()
    plt.savefig("../plots/"+ fig_title)
    print(f"Figure saved as {fig_title}")

def main():
    # Configuration
    dt_true = 0.5
    ref_level = 5
    degree = 1
    scheme_indicies = [0, 1, 2]
    scheme_names = ["SDC(2,3)", "SDC(3,5)", "SDC(4,7)"]
    dts= [2400., 1800., 1200., 900.]
    cols = ['r', 'b', 'g']
    ticks = ['o', '^', 'x']
    file_path = "../test_cases/results/"
    file_name = "chkpt.h5"
    true_data_name = f"williamson_1_true_paper_ref{ref_level}_dt{dt_true}_deg{degree}"
    data_names=[]
    for id in scheme_indicies:
        data_name = [f"williamson_1_EX_SDC_paper_ref{ref_level}_dt{dt}_k{id}_deg{degree}" for dt in dts]
        data_names.append(data_name)
    fig_title = f"paper_fig_1"

    # Load true solution
    true_data = load_true_solution(file_path, true_data_name, file_name)

    # Compute errors
    errors_D, errors_u = compute_errors(data_names, file_path, file_name, true_data)

    # Plot errors
    plot_errors(dts, errors_D, scheme_names, fig_title, cols, ticks)


if __name__ == "__main__":
    main()
