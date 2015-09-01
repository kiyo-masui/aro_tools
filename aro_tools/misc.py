import numpy as np



DM0 = 4148.808


def diag_dm(delta_t, delta_f, freq):
    return abs(delta_t) * freq**3 / 2 / abs(delta_f) / DM0



def disp_delay(dm, freq):
    return DM0 * dm / freq**2
