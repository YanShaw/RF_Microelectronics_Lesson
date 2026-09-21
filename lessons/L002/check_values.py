"""Independent arithmetic checks for L002; not a transistor simulation."""
import math
import xml.etree.ElementTree as ET
from pathlib import Path

def close(actual, expected):
    assert math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-12), (actual, expected)

close(2 * 0.0005 / 0.2, 0.005)
close(1 / (0.1 * 0.0005), 20000)
close(1.07 / (0.1 * 0.0005), 21400)
close(0.005 * 0.001, 5e-6)
close(0.0005**2 * 1000 + 0.7 * 0.0005, 1.2 * 0.0005)
k, ov, supply, resistance = 0.025, 0.2, 1.2, 2200
roots = [(12 + sign * math.sqrt(12**2 - 4 * 27.5 * 1.2)) / 55 for sign in (-1, 1)]
valid = [v for v in roots if 0 <= v < ov]
assert len(valid) == 1
v = valid[0]
current = (supply - v) / resistance
close(current, k * (ov * v - v**2 / 2))
close(v, 0.15519815245204086)
close(current, 0.0004749099307036177)
close((1.2 - 0.2) / 0.0005, 2000)
close(2 * 0.00025 / 0.25, 0.002)
close(1 / (0.08 * 0.00025), 50000)
close(1.056 / (0.08 * 0.00025), 52800)
close(0.002 * 0.005, 10e-6)
for ov, expected_i, expected_k, expected_r in [(0.2, 0.0005, 0.025, 2000), (0.1, 0.00025, 0.05, 4400)]:
    current = 0.005 * ov / 2
    close(current, expected_i)
    close(0.005 / ov, expected_k)
    close((supply - ov) / current, expected_r)
ET.parse(Path(__file__).with_name('bias.svg'))
print('PASS: example and exercise arithmetic, region checks, power balance, SVG XML.')
print(f'Triode solution: VDS={v:.9f} V; ID={(supply-v)/resistance*1000:.9f} mA')
