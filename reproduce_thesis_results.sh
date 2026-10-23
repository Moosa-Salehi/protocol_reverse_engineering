#!/bin/bash
# Reproduce every result number in the thesis (archive/thesis/thesis_report) and rebuild it.
#
#   ./reproduce_thesis_results.sh numbers       regenerate all LaTeX number files from the existing runs and rebuild
#                                               (minutes). Runs: dol/final-v4, dol/thesis-final-zs, dol/baseline-comparison,
#                                               dol/heldout.
#   ./reproduce_thesis_results.sh full [tag]    rerun everything from the extracted corpora into dol/repro-<tag>/...
#                                               (several hours, sequential: the 8 GB WSL VM cannot run jobs in parallel),
#                                               then regenerate and rebuild. The tool baselines (NEMESYS, Netzob, NetPlier)
#                                               and the held-out runs are rerun in place (deterministic).
#
# Environments: ~/.venvs/protocol_re (pipeline), ~/.venvs/nemesys39 (NEMESYS, Netzob 2.0), ~/.venvs/netplier39
# (NetPlier, Netzob 1.0.2) with MAFFT wrappers in ~/.local/baseline-tools/bin; TinyTeX + ~/.local/thesis-build/build.sh.
# Data: dol/benchmark-14-protocols (14 benchmark corpora), truth_files/, dol/accuracy-push/{annotations-truthconv,
# integrated-labels*}, assets/pre_trained (zero-shot training set), finetuning/cluster-free-dataset/annotations (parser annotations),
# dol/modbus1, dol/finetuned-modbus-small, dol/sajjad, dol/goose (supplementary), dol/heldout (held-out protocols).
set -e
cd "$(dirname "$0")"
PY=~/.venvs/protocol_re/bin/python
T=archive/thesis/thesis_report/chapters
mode=${1:-numbers}
if [ "$mode" = full ]; then
  tag=${2:-$(date +%Y%m%d)}
  export THESIS_RUNS=repro-$tag/benchmark THESIS_FINAL=repro-$tag/final
  mkdir -p dol/repro-$tag/benchmark/sample-runs
  bash dol/hdbscan-global/run_final.sh $THESIS_RUNS            # 14 protocols x all configurations + samples
  bash dol/thesis-numbers/run_thesis_final.sh $THESIS_FINAL      # case study, supplementary corpora, runtime
  ( cd dol/baseline-comparison/scripts
    ~/.venvs/nemesys39/bin/python run_nemesys.py
    for p in bacnet cip dnp3 enip ethercat goose hart_ip iec104 mms modbus opcua powerlink s7comm zigbee; do
      ./budget.sh netzob $p 1800 ~/.venvs/nemesys39/bin/python run_netzob.py
      MAFFT_AS_LIMIT_KB=3145728 ./budget.sh netplier $p 1800 ~/.venvs/netplier39/bin/python run_netplier.py
    done )
  python3 dol/heldout/prepare.py
  python3 dol/heldout/prepare_new.py doip cnip
  bash dol/heldout/run_all_ours.sh
  ( cd dol/baseline-comparison/scripts
    ~/.venvs/nemesys39/bin/python run_nemesys.py synphasor ams doip cnip
    for p in synphasor ams doip cnip; do
      ./budget.sh netzob $p 1800 ~/.venvs/nemesys39/bin/python run_netzob.py
      MAFFT_AS_LIMIT_KB=3145728 ./budget.sh netplier $p 1800 ~/.venvs/netplier39/bin/python run_netplier.py
    done )
fi
RUNS=${THESIS_RUNS:-final-v4}
$PY dol/thesis-numbers/gen_main.py $RUNS $T/results_main_data.tex
$PY dol/thesis-numbers/gen_errors.py $RUNS $T/results_errors_data.tex > /dev/null
$PY dol/thesis-numbers/gen_final.py $T/results_final_data.tex
( cd dol/baseline-comparison/scripts
  $PY -W ignore score.py > ../scores.txt
  $PY summarize.py > ../summary.txt
  $PY gen_tex.py ../../../$T/results_baselines_data.tex > /dev/null )
$PY -W ignore dol/heldout/score.py > /dev/null
$PY dol/thesis-numbers/gen_heldout.py $T/results_heldout_data.tex
~/.local/thesis-build/build.sh
cp ~/.local/thesis-build/out/thesis.pdf archive/thesis/thesis_report/thesis.pdf
echo "thesis rebuilt: archive/thesis/thesis_report/thesis.pdf"
