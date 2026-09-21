"""Independent KCL verification of L003's linear model; not device simulation."""
import numpy as np

GM, RO, RD = 0.005, 20000.0, 10000.0

def check(rs, rl):
    gload = 1 / RD + (0 if rl is None else 1 / rl)
    if rs == 0:
        av = -GM / (gload + 1 / RO)
        rout = 1 / (1 / RD + 1 / RO)
    else:
        # KCL at D and S, with vg=1 V as a normalized linear-model input.
        matrix = np.array([[gload + 1 / RO, -1 / RO - GM],
                           [-1 / RO, 1 / rs + 1 / RO + GM]])
        vd, vs = np.linalg.solve(matrix, [-GM, GM])
        assert np.allclose(matrix @ [vd, vs], [-GM, GM])
        av = vd
        # Remove RL; vg=0; inject a normalized 1 A test current at D.
        matrix[0, 0] = 1 / RD + 1 / RO
        rout, vs_test = np.linalg.solve(matrix, [1, 0])
        assert np.allclose(matrix @ [rout, vs_test], [1, 0])
    r = 1 / gload
    expected_av = -GM * RO * r / (RO + r + rs * (1 + GM * RO))
    transistor_rout = RO + rs * (1 + GM * RO)
    expected_rout = 1 / (1 / RD + 1 / transistor_rout)
    assert np.isclose(av, expected_av)
    assert np.isclose(rout, expected_rout)
    print(f'Rs={rs:g} ohm, RL={rl}: Av={av:.9f}, Rout={rout:.6f} ohm')
    return av, rout

if __name__ == '__main__':
    for rs, rl in [(0, None), (0, 10000), (1000, None), (1000, 10000),
                   (0, 5000), (2000, 10000)]:
        check(rs, rl)
    print('All KCL/formula comparisons passed. Test amplitudes are normalization only.')
