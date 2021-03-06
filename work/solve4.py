import os
import numpy as np
from Reader import ReadU, ReadSystem

import paddle

from ops import Fidelity
from utils import RandomCNOTs, EnumAllCNOT, CostCompute
from ArchitectureSearch import RandomSearch, SequenceJitter
from paddle_model import BackwardParams, ParseFromQSystem, GetQSystem, TryRemoveZeros

INPUT_TXT = 'Questions/Question_4_Unitary.txt'
ANSWER_TXT = '../Answer/Question_4_Answer.txt'
TMP_TXT = 'tmp/Question_4_tmp.txt'

LAYER_COUNT = 6
quantum_count = 3

paddle.set_device('cpu')

def EnumProcess(in_txt=INPUT_TXT, out_txt=ANSWER_TXT):
    U = ReadU(in_txt)
    np.random.seed(2021)
    cnot_creater = EnumAllCNOT(quantum_count, LAYER_COUNT)
    solver = lambda cnot:BackwardParams(U, quantum_count, cnot_layers=cnot)
    print('Need Search %d epochs.'%(len(cnot_creater)))
    best_score, model_str = RandomSearch(
        cnot_creater = cnot_creater,
        solver = solver,
        epochs = len(cnot_creater),
        save_path = out_txt
    )
    print('In question 4: best_score = %g'%(best_score))
    with open(out_txt, 'w') as f:
        f.write(model_str)

def RandomSearchProcess(in_txt=INPUT_TXT, out_txt=ANSWER_TXT):
    U = ReadU(in_txt)
    np.random.seed(2021)
    cnot_creater = lambda:RandomCNOTs(quantum_count, layer_count=LAYER_COUNT)
    solver = lambda cnot:BackwardParams(U, quantum_count, cnot_layers=cnot)
    best_score, model_str = RandomSearch(
        cnot_creater = cnot_creater,
        solver = solver,
        epochs = 200,
        save_path = out_txt
    )
    print('In question 4: best_score = %g'%(best_score))
    with open(out_txt, 'w') as f:
        f.write(model_str)

def JitterSearch(in_txt=INPUT_TXT, out_txt=ANSWER_TXT):
    U = ReadU(in_txt)
    np.random.seed(2021)
    best_score = 0
    for _ in range(20):
        solver = lambda cnot:BackwardParams(U, quantum_count, cnot_layers=cnot)
        sc, model, _ = SequenceJitter(
            quantum_count=quantum_count,
            layer_count = LAYER_COUNT,
            solver = solver,
            epochs = 2,
            save_path = out_txt,
            global_best_score = best_score,
        )
        if sc>best_score:
            best_score = sc
            best_model_str = model
            # best_cnot = cnot
    # solver_better = lambda cnot:BackwardParams(U, quantum_count, cnot_layers=cnot, learning_rate=0.1, iterations=500, verbose=10)
    # best_score, best_model_str = solver_better(best_cnot)
    print('In question 4: best_score = %g'%(best_score))
    with open(out_txt, 'w') as f:
        f.write(best_model_str)

def RemoveZeros(u_txt=INPUT_TXT, in_txt=ANSWER_TXT, out_txt=ANSWER_TXT):
    np.random.seed(2021)
    U = ReadU(u_txt)
    M = ReadSystem(in_txt, quantum_count)
    model = ParseFromQSystem(M)
    F_scale = 11
    cost_scale = 1/400
    eval_func = lambda F, cost:F_scale*(F-cost*cost_scale) if F>0.75 else 0
    model, best_score = TryRemoveZeros(U, model, quantum_count, eval_func)
    qsystem = GetQSystem(model)
    model_str = qsystem.string
    f = Fidelity(U, qsystem.matrix)
    c = CostCompute(qsystem.string)
    print('score = ', eval_func(f, c))
    print('In question 4: final_score = %g'%(best_score))
    print(model_str)
    with open(out_txt, 'w') as f:
        f.write(model_str)


if __name__ == '__main__':
    if not os.path.exists('../Answer'):
        os.makedirs('../Answer')
    # RandomSearchProcess()
    # JitterSearch()
    # EnumProcess()
    JitterSearch(out_txt=TMP_TXT)

    RemoveZeros(in_txt=TMP_TXT)
