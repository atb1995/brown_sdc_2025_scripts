"""
Time and space convergence for the non-linear gravity wave test case of Skamarock and Klemp (1994).

Potential temperature is transported using SUPG.

This is for order 5 finite elements.
"""
from petsc4py import PETSc
PETSc.Sys.popErrorHandler()
from gusto import *
import itertools
from firedrake import (as_vector, SpatialCoordinate, PeriodicIntervalMesh,
                       ExtrudedMesh, exp, sin, Function, pi, COMM_WORLD)
import numpy as np
import sys

# ---------------------------------------------------------------------------- #
# Test case parameters
# ---------------------------------------------------------------------------- #

L = 3.0e5  # Domain length
H = 1.0e4  # Height position of the model top

if '--running-tests' in sys.argv:
    nlayers = 5
    columns = 30
    tmax = dt
    dumpfreq = 1
else:
    nlayers = 10
    columns = [120.,  60., 30.]
    dts = [0.46875, 0.9375, 1.875]
    cfl = 0.0015
    u0_val = 20.0
    tmax = 3000.0
for column, dt in zip(columns,dts):
    dx = float(float(L)/float(column))
    # ---------------------------------------------------------------------------- #
    # Set up model objects
    # ---------------------------------------------------------------------------- #
    dumpfreq = int(tmax / (dt))
    # Domain -- 3D volume mesh
    m = PeriodicIntervalMesh(column, L)
    mesh = ExtrudedMesh(m, layers=nlayers, layer_height=H/nlayers)
    domain = Domain(mesh, dt, "CG", 5)
    u_eqn_type = 'vector_advection_form'

    # Equation
    Tsurf = 300.
    parameters = CompressibleParameters(mesh=mesh)
    eqns = CompressibleEulerEquations(domain, parameters, u_transport_option=u_eqn_type)
    eqns = split_continuity_form(eqns)
    eqns = split_hv_advective_form(eqns, "rho")
    eqns = split_hv_advective_form(eqns, "theta")
    opts =SUPGOptions(suboptions={"theta": [transport]})
    print("Opt Cores:", eqns.X.function_space().dim()/50000.)

    # I/O
    points_x = np.linspace(0., L, 100)
    points_z = [H/2.]
    points = np.array([p for p in itertools.product(points_x, points_z)])
    deltax = L/column
    dirname = 'gravity_wave_imex_sdc_paper_o5_dx_%s_dt_%s' %(deltax,dt)

    diagnostic_fields = [CourantNumber(), Gradient('u'), Perturbation('theta'),
                        Gradient('theta_perturbation'), Perturbation('rho'),
                        RichardsonNumber('theta', parameters.g/Tsurf), Gradient('theta')]
    output = OutputParameters(dirname=dirname,
                            dumpfreq=dumpfreq,
                            checkpoint=True,
                            dump_nc=True,
                            dump_vtus=False,
                            checkpoint_method="checkpointfile",
                            chkptfreq=dumpfreq,
                            dumplist=['u','theta','rho'])
    io = IO(domain, output, diagnostic_fields=diagnostic_fields)

    # Transport schemes
    transport_methods = [DGUpwind(eqns, "u"),
                        SplitDGUpwind(eqns, "rho"),
                        SplitDGUpwind(eqns, "theta", ibp=SUPGOptions.ibp)]

    nl_solver_parameters = {
    "snes_converged_reason": None,
    "snes_lag_preconditioner_persists":None,
    "snes_lag_preconditioner":-2,
    "snes_lag_jacobian": -2,
    "snes_lag_jacobian_persists": None,
    'ksp_ew': None,
    'ksp_ew_version': 1,
    "ksp_ew_threshold": 1e-2,
    "ksp_ew_rtol0": 1e-3,
    "mat_type": "matfree",
    "ksp_type": "gmres",
    "ksp_converged_reason": None,
    "ksp_atol": 1e-4,
    "ksp_rtol": 1e-4,
    "snes_atol": 1e-4,
    "snes_rtol": 1e-4,
    "ksp_max_it": 400,
    "pc_type": "python",
    "pc_python_type": "firedrake.AssembledPC","assembled": {
        "pc_type": "python",
        "pc_python_type": "firedrake.ASMStarPC",
        "pc_star": {
            "construct_dim": 0,
            "sub_sub": {
                "pc_type": "lu",
                "pc_factor_mat_ordering_type": "rcm",
                "pc_factor_reuse_ordering": None,
                "pc_factor_reuse_fill": None,
                "pc_factor_fill": 1.2
            }
        },
    },}
    linear_solver_parameters = {'snes_type': 'ksponly',
                            'ksp_rtol': 1e-5,
                            'ksp_rtol': 1e-7,
                            'ksp_type': 'cg',
                            'pc_type': 'bjacobi',
                            'sub_pc_type': 'ilu'}
    eqns.label_terms(lambda t: not any(t.has_label(time_derivative, transport)), implicit)
    eqns.label_terms(lambda t: t.has_label(transport), explicit)
    eqns.label_terms(lambda t: t.has_label(transport) and t.has_label(horizontal_transport), explicit)
    eqns.label_terms(lambda t: t.has_label(transport) and t.has_label(vertical_transport), implicit)
    eqns.label_terms(lambda t: t.has_label(transport) and not any(t.has_label(horizontal_transport, vertical_transport)), explicit)
    base_scheme = IMEX_Euler(domain, options=opts,nonlinear_solver_parameters=nl_solver_parameters)
    node_type = "LEGENDRE"
    qdelta_exp = "FE"
    quad_type = "RADAU-RIGHT"
    M = 4
    k = 7
    qdelta_imp = "LU"
    scheme =SDC(base_scheme, domain, M, k, quad_type, node_type, qdelta_imp,
                        qdelta_exp, formulation="Z2N", options=opts, nonlinear_solver_parameters=nl_solver_parameters,final_update=False, initial_guess="copy")
    # Time stepper
    stepper = Timestepper(eqns, scheme, io, transport_methods)
    
    # ---------------------------------------------------------------------------- #
    # Initial conditions
    # ---------------------------------------------------------------------------- #

    u0 = stepper.fields("u")
    rho0 = stepper.fields("rho")
    theta0 = stepper.fields("theta")

    # spaces
    Vu = domain.spaces("HDiv")
    Vt = domain.spaces("theta")
    Vr = domain.spaces("DG")

    # Thermodynamic constants required for setting initial conditions
    # and reference profiles
    g = parameters.g
    N = parameters.N

    x, z = SpatialCoordinate(mesh)

    # N^2 = (g/theta)dtheta/dz => dtheta/dz = theta N^2g => theta=theta_0exp(N^2gz)
    thetab = Tsurf*exp(N**2*z/g)

    theta_b = Function(Vt).interpolate(thetab)
    rho_b = Function(Vr)

    # Calculate hydrostatic exner
    compressible_hydrostatic_balance(eqns, theta_b, rho_b)

    a = 5.0e3
    deltaTheta = 1.0e-2
    theta_pert = deltaTheta*sin(pi*z/H)/(1 + (x - L/2)**2/a**2)
    theta0.interpolate(theta_b + theta_pert)
    rho0.assign(rho_b)
    u0.project(as_vector([20.0, 0.0]))

    stepper.set_reference_profiles([('rho', rho_b),
                                    ('theta', theta_b)])

    # ---------------------------------------------------------------------------- #
    # Run
    # ---------------------------------------------------------------------------- #

    stepper.run(t=0, tmax=tmax)
