import argparse
import time
import sys
from . import kidney_digraph
from . import kidney_ip
from . import kidney_utils
from . import kidney_ndds
from kidney_solver.kidney_solver import solve_kep
# solve using PICEF w/ edge probability 1
# then eval structure using given edge probabilities by cycle/chain

def start():
    parser = argparse.ArgumentParser("Solve a kidney-exchange instance")
    parser.add_argument("cycle_cap", type=int,
                        help="The maximum permitted cycle length")
    parser.add_argument("chain_cap", type=int,
                        help="The maximum permitted number of edges in a chain")
    parser.add_argument("formulation",
                        help="The IP formulation (uef, eef, eef_full_red, hpief_prime, hpief_2prime, hpief_prime_full_red, hpief_2prime_full_red, picef, cf)")
    parser.add_argument("--use-relabelled", "-r", required=False,
                        action="store_true",
                        help="Relabel vertices in descending order of in-deg + out-deg")
    parser.add_argument("--eef-alt-constraints", "-e", required=False,
                        action="store_true",
                        help="Use slightly-modified EEF constraints (ignored for other formulations)")
    parser.add_argument("--timelimit", "-t", required=False, default=None,
                        type=float,
                        help="IP solver time limit in seconds (default: no time limit)")
    parser.add_argument("--verbose", "-v", required=False,
                        action="store_true",
                        help="Log Gurobi output to screen and log file")
    parser.add_argument("--edge-success-prob", "-p", required=False,
                        type=float, default=1.0,
                        help="Edge success probability, for failure-aware matching. " +
                             "This can only be used with PICEF and cycle formulation. (default: 1)")
    parser.add_argument("--lp-file", "-l", required=False, default=None,
                        metavar='FILE',
                        help="Write the IP model to FILE, then exit.")
    parser.add_argument("--relax", "-x", required=False,
                        action='store_true',
                        help="Solve the LP relaxation.")
    input_lines = [line for line in sys.stdin if len(line.strip()) > 0]
    n_digraph_edges = int(input_lines[0].split()[1])
    digraph_lines = input_lines[:n_digraph_edges + 2]

    d = kidney_digraph.read_digraph(digraph_lines)
    if len(input_lines) > len(digraph_lines):
        ndd_lines = input_lines[n_digraph_edges + 2:]
        altruists = kidney_ndds.read_ndds(ndd_lines, d)
    else:
        altruists = []
    args = parser.parse_args()
    args.formulation = args.formulation.lower()
    start_time = time.time()
    # optimize as if success prob is 1.0
    cfg = kidney_ip.OptConfig(d, altruists, args.cycle_cap, args.chain_cap, args.verbose,
                              args.timelimit, 1.0, args.eef_alt_constraints,
                              args.lp_file, args.relax)

    opt_solution = solve_kep(cfg, 'picef', args.use_relabelled)
    print(opt_solution)

if __name__ == '__main__':
    start()
