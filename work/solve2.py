import os
import numpy as np
from Reader import ReadU
from ops import MakeR, Fidelity
from utils import Minimize, QSystem, RLayer, CLayer

INPUT_TXT = 'Questions/Question_2_Unitary.txt'
ANSWER_TXT = '../Answer/Question_2_Answer.txt'

def main(in_txt=INPUT_TXT, out_txt=ANSWER_TXT):
    MakeSystem = lambda t1,t2,t3,t4:QSystem([
            RLayer([t1, t2], quantum_count=2),
            CLayer(0, 1, quantum_count=2),
            RLayer([t3, t4], quantum_count=2),
        ])

    U = ReadU(in_txt)
    best_score = 0
    np.random.seed(2021)
    for epoch in range(10000):
        params = np.random.uniform(0, 2*np.pi, size=[4])
        model = MakeSystem(*list(params))
        M = model.matrix
        score = 2*Fidelity(U, M)
        if score>best_score:
            # print('epoch_%d, score = %g'%(epoch, score))
            best_score = score
            best_ans = params
    # print(x)
    for eps in [1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]:
        for epoch in range(1000):
            dt = np.random.uniform(-eps, eps, size=[4])
            params = best_ans+dt
            model = MakeSystem(*list(params))
            score = 2*Fidelity(U, model.matrix)
            if score>best_score:
                # print('eps=%g, epoch=%d, score = %g'%(eps, epoch, score))
                best_score = score
                best_ans = params
    print('In question 2: best_score = %g'%(best_score))
    with open(out_txt, 'w') as f:
        f.write(MakeSystem(*list(best_ans)).string)

if __name__ == '__main__':
    if not os.path.exists('../Answer'):
        os.makedirs('../Answer')
    main()
