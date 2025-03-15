'''
Copyright (c) 2021 Björn Ottosson

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import math

# Data structures
class Lab:
    def __init__(self, L, a, b):
        self.L = L
        self.a = a
        self.b = b
    
    def __str__(self):
        return f"L:{self.L},a:{self.a},b:{self.b}"

class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"r:{self.r},g:{self.g},b:{self.b}"

class HSV:
    def __init__(self, h, s, v):
        self.h = h
        self.s = s
        self.v = v

    def __str__(self):
        return f"h:{self.h},s:{self.s},v:{self.v}"

class HSL:
    def __init__(self, h, s, l):
        self.h = h
        self.s = s
        self.l = l

    def __str__(self):
        return f"h:{self.h},s:{self.s},l:{self.l}"

class LC:
    def __init__(self, L, C):
        self.L = L
        self.C = C

class ST:
    def __init__(self, S, T):
        self.S = S
        self.T = T

class Cs:
    def __init__(self, C0, Cmid, Cmax):
        self.C0 = C0
        self.Cmid = Cmid
        self.Cmax = Cmax

pi = math.pi

def clamp(x, minVal, maxVal):
    if x < minVal:
        return minVal
    if x > maxVal:
        return maxVal
    return x

def sgn(x):
    return (1 if x > 0 else 0) - (1 if x < 0 else 0)

def srgbTransferFunction(a: float):
    if a <= 0.0031308:
        return 12.92 * a
    else:
        return 1.055 * (a ** 0.4166666666666667) - 0.055

def srgbTransferFunctionInv(a: float):
    if a > 0.04045:
        return ((a + 0.055) / 1.055) ** 2.4
    else:
        return a / 12.92

def cubeRoot(x: float):
    return math.copysign(abs(x) ** (1/3), x)

def linearSrgbToOklab(c: RGB):
    l = 0.4122214708 * c.r + 0.5363325363 * c.g + 0.0514459929 * c.b
    m = 0.2119034982 * c.r + 0.6806995451 * c.g + 0.1073969566 * c.b
    s = 0.0883024619 * c.r + 0.2817188376 * c.g + 0.6299787005 * c.b

    l_ = cubeRoot(l)
    m_ = cubeRoot(m)
    s_ = cubeRoot(s)

    return Lab(
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    )

def oklabToLinearSrgb(c: Lab):
    l_ = c.L + 0.3963377774 * c.a + 0.2158037573 * c.b
    m_ = c.L - 0.1055613458 * c.a - 0.0638541728 * c.b
    s_ = c.L - 0.0894841775 * c.a - 1.2914855480 * c.b

    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3

    return RGB(
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    )

def computeMaxSaturation(a, b):
    if (-1.88170328 * a - 0.80936493 * b) > 1:
        k0, k1, k2, k3, k4 = 1.19086277, 1.76576728, 0.59662641, 0.75515197, 0.56771245
        wl, wm, ws = 4.0767416621, -3.3077115913, 0.2309699292
    elif (1.81444104 * a - 1.19445276 * b) > 1:
        k0, k1, k2, k3, k4 = 0.73956515, -0.45954404, 0.08285427, 0.12541070, 0.14503204
        wl, wm, ws = -1.2684380046, 2.6097574011, -0.3413193965
    else:
        k0, k1, k2, k3, k4 = 1.35733652, -0.00915799, -1.15130210, -0.50559606, 0.00692167
        wl, wm, ws = -0.0041960863, -0.7034186147, 1.7076147010

    S = k0 + k1 * a + k2 * b + k3 * a * a + k4 * a * b

    kL = 0.3963377774 * a + 0.2158037573 * b
    kM = -0.1055613458 * a - 0.0638541728 * b
    kS = -0.0894841775 * a - 1.2914855480 * b

    l_ = 1 + S * kL
    m_ = 1 + S * kM
    s_ = 1 + S * kS

    lVal = l_ ** 3
    mVal = m_ ** 3
    sVal = s_ ** 3

    lDS = 3 * kL * (l_ ** 2)
    mDS = 3 * kM * (m_ ** 2)
    sDS = 3 * kS * (s_ ** 2)

    lDS2 = 6 * (kL ** 2) * l_
    mDS2 = 6 * (kM ** 2) * m_
    sDS2 = 6 * (kS ** 2) * s_

    f = wl * lVal + wm * mVal + ws * sVal
    f1 = wl * lDS + wm * mDS + ws * sDS
    f2 = wl * lDS2 + wm * mDS2 + ws * sDS2

    S = S - f * f1 / (f1 * f1 - 0.5 * f * f2)
    return S

def findCusp(a, b):
    S_cusp = computeMaxSaturation(a, b)
    rgbAtMax = oklabToLinearSrgb(Lab(1, S_cusp * a, S_cusp * b))
    maxVal = max(rgbAtMax.r, rgbAtMax.g, rgbAtMax.b)
    L_cusp = cubeRoot(1 / maxVal)
    C_cusp = L_cusp * S_cusp
    return LC(L_cusp, C_cusp)

def findGamutIntersectionWithCusp(a, b, L1, C1, L0, cusp):
    if ((L1 - L0) * cusp.C - (cusp.L - L0) * C1) <= 0:
        t = cusp.C * L0 / (C1 * cusp.L + cusp.C * (L0 - L1))
    else:
        t = cusp.C * (L0 - 1) / (C1 * (cusp.L - 1) + cusp.C * (L0 - L1))
        dL = L1 - L0
        dC = C1
        kL = 0.3963377774 * a + 0.2158037573 * b
        kM = -0.1055613458 * a - 0.0638541728 * b
        kS = -0.0894841775 * a - 1.2914855480 * b

        lDt = dL + dC * kL
        mDt = dL + dC * kM
        sDt = dL + dC * kS

        L_val = L0 * (1 - t) + t * L1
        C_val = t * C1

        l_ = L_val + C_val * kL
        m_ = L_val + C_val * kM
        s_ = L_val + C_val * kS

        lCubed = l_ ** 3
        mCubed = m_ ** 3
        sCubed = s_ ** 3

        lDtVal = 3 * lDt * (l_ ** 2)
        mDtVal = 3 * mDt * (m_ ** 2)
        sDtVal = 3 * sDt * (s_ ** 2)

        lDt2 = 6 * (lDt ** 2) * l_
        mDt2 = 6 * (mDt ** 2) * m_
        sDt2 = 6 * (sDt ** 2) * s_

        r_val = 4.0767416621 * lCubed - 3.3077115913 * mCubed + 0.2309699292 * sCubed - 1
        r1 = 4.0767416621 * lDtVal - 3.3077115913 * mDtVal + 0.2309699292 * sDtVal
        r2 = 4.0767416621 * lDt2 - 3.3077115913 * mDt2 + 0.2309699292 * sDt2
        u_r = r1 / (r1 * r1 - 0.5 * r_val * r2) if (r1 * r1 - 0.5 * r_val * r2) != 0 else 0
        t_r = -r_val * u_r if u_r >= 0 else float('inf')

        g_val = -1.2684380046 * lCubed + 2.6097574011 * mCubed - 0.3413193965 * sCubed - 1
        g1 = -1.2684380046 * lDtVal + 2.6097574011 * mDtVal - 0.3413193965 * sDtVal
        g2 = -1.2684380046 * lDt2 + 2.6097574011 * mDt2 - 0.3413193965 * sDt2
        u_g = g1 / (g1 * g1 - 0.5 * g_val * g2) if (g1 * g1 - 0.5 * g_val * g2) != 0 else 0
        t_g = -g_val * u_g if u_g >= 0 else float('inf')

        b_val = -0.0041960863 * lCubed - 0.7034186147 * mCubed + 1.7076147010 * sCubed - 1
        b1 = -0.0041960863 * lDtVal - 0.7034186147 * mDtVal + 1.7076147010 * sDtVal
        b2 = -0.0041960863 * lDt2 - 0.7034186147 * mDt2 + 1.7076147010 * sDt2
        u_b = b1 / (b1 * b1 - 0.5 * b_val * b2) if (b1 * b1 - 0.5 * b_val * b2) != 0 else 0
        t_b = -b_val * u_b if u_b >= 0 else float('inf')

        t += min(t_r, t_g, t_b)
    return t

def findGamutIntersection(a, b, L1, C1, L0, cusp=None):
    if cusp is None:
        cusp = findCusp(a, b)
    return findGamutIntersectionWithCusp(a, b, L1, C1, L0, cusp)

def gamutClipPreserveChroma(rgb):
    if 0 < rgb.r < 1 and 0 < rgb.g < 1 and 0 < rgb.b < 1:
        return rgb
    lab = linearSrgbToOklab(rgb)
    L = lab.L
    eps = 0.00001
    C = max(eps, math.sqrt(lab.a * lab.a + lab.b * lab.b))
    a_ = lab.a / C
    b_ = lab.b / C
    L0 = clamp(L, 0, 1)
    t = findGamutIntersection(a_, b_, L, C, L0)
    LClipped = L0 * (1 - t) + t * L
    CClipped = t * C
    return oklabToLinearSrgb(Lab(LClipped, CClipped * a_, CClipped * b_))

def gamutClipProjectTo05(rgb):
    if 0 < rgb.r < 1 and 0 < rgb.g < 1 and 0 < rgb.b < 1:
        return rgb
    lab = linearSrgbToOklab(rgb)
    L = lab.L
    eps = 0.00001
    C = max(eps, math.sqrt(lab.a * lab.a + lab.b * lab.b))
    a_ = lab.a / C
    b_ = lab.b / C
    L0 = 0.5
    t = findGamutIntersection(a_, b_, L, C, L0)
    LClipped = L0 * (1 - t) + t * L
    CClipped = t * C
    return oklabToLinearSrgb(Lab(LClipped, CClipped * a_, CClipped * b_))

def gamutClipProjectToLCusp(rgb):
    if 0 < rgb.r < 1 and 0 < rgb.g < 1 and 0 < rgb.b < 1:
        return rgb
    lab = linearSrgbToOklab(rgb)
    L = lab.L
    eps = 0.00001
    C = max(eps, math.sqrt(lab.a * lab.a + lab.b * lab.b))
    a_ = lab.a / C
    b_ = lab.b / C
    cusp = findCusp(a_, b_)
    L0 = cusp.L
    t = findGamutIntersection(a_, b_, L, C, L0)
    LClipped = L0 * (1 - t) + t * L
    CClipped = t * C
    return oklabToLinearSrgb(Lab(LClipped, CClipped * a_, CClipped * b_))

def gamutClipAdaptiveL0_05(rgb, alpha=0.05):
    if 0 < rgb.r < 1 and 0 < rgb.g < 1 and 0 < rgb.b < 1:
        return rgb
    lab = linearSrgbToOklab(rgb)
    L = lab.L
    eps = 0.00001
    C = max(eps, math.sqrt(lab.a * lab.a + lab.b * lab.b))
    a_ = lab.a / C
    b_ = lab.b / C
    Ld = L - 0.5
    e1 = 0.5 + abs(Ld) + alpha * C
    L0 = 0.5 * (1 + sgn(Ld) * (e1 - math.sqrt(e1 * e1 - 2 * abs(Ld))))
    t = findGamutIntersection(a_, b_, L, C, L0)
    LClipped = L0 * (1 - t) + t * L
    CClipped = t * C
    return oklabToLinearSrgb(Lab(LClipped, CClipped * a_, CClipped * b_))

def gamutClipAdaptiveL0LCusp(rgb, alpha=0.05):
    if 0 < rgb.r < 1 and 0 < rgb.g < 1 and 0 < rgb.b < 1:
        return rgb
    lab = linearSrgbToOklab(rgb)
    L = lab.L
    eps = 0.00001
    C = max(eps, math.sqrt(lab.a * lab.a + lab.b * lab.b))
    a_ = lab.a / C
    b_ = lab.b / C
    cusp = findCusp(a_, b_)
    Ld = L - cusp.L
    k = 2 * (1 - cusp.L if Ld > 0 else cusp.L)
    e1 = 0.5 * k + abs(Ld) + alpha * C / k
    L0 = cusp.L + 0.5 * (sgn(Ld) * (e1 - math.sqrt(e1 * e1 - 2 * k * abs(Ld))))
    t = findGamutIntersection(a_, b_, L, C, L0)
    LClipped = L0 * (1 - t) + t * L
    CClipped = t * C
    return oklabToLinearSrgb(Lab(LClipped, CClipped * a_, CClipped * b_))

def toe(x):
    k1 = 0.206
    k2 = 0.03
    k3 = (1 + k1) / (1 + k2)
    return 0.5 * (k3 * x - k1 + math.sqrt((k3 * x - k1) ** 2 + 4 * k2 * k3 * x))

def toeInv(x):
    k1 = 0.206
    k2 = 0.03
    k3 = (1 + k1) / (1 + k2)
    return (x * x + k1 * x) / (k3 * (x + k2))

def toST(cusp):
    return ST(cusp.C / cusp.L, cusp.C / (1 - cusp.L))

def getSTMid(a_, b_):
    S_val = 0.11516993 + 1 / (7.44778970 + 4.15901240 * b_ + a_ * (
        -2.19557347 + 1.75198401 * b_ + a_ * (
            -2.13704948 - 10.02301043 * b_ + a_ * (
                -4.24894561 + 5.38770819 * b_ + 4.69891013 * a_))))
    T_val = 0.11239642 + 1 / (1.61320320 - 0.68124379 * b_ + a_ * (
        0.40370612 + 0.90148123 * b_ + a_ * (
            -0.27087943 + 0.61223990 * b_ + a_ * (
                0.00299215 - 0.45399568 * b_ - 0.14661872 * a_))))
    return ST(S_val, T_val)

def getCs(L, a_, b_):
    cusp = findCusp(a_, b_)
    Cmax = findGamutIntersection(a_, b_, L, 1, L, cusp)
    ST_max = toST(cusp)
    k = Cmax / min(L * ST_max.S, (1 - L) * ST_max.T)
    ST_mid = getSTMid(a_, b_)
    C_a = L * ST_mid.S
    C_b = (1 - L) * ST_mid.T
    C_mid = 0.9 * k * math.sqrt(math.sqrt(1 / ((1 / (C_a ** 4)) + (1 / (C_b ** 4)))))
    C_a0 = L * 0.4
    C_b0 = (1 - L) * 0.8
    C0 = math.sqrt(1 / ((1 / (C_a0 ** 2)) + (1 / (C_b0 ** 2))))
    return Cs(C0, C_mid, Cmax)

def okhslToSrgb(hsl):
    h = hsl.h
    s = hsl.s
    l_val = hsl.l
    if l_val == 1:
        return RGB(1, 1, 1)
    if l_val == 0:
        return RGB(0, 0, 0)
    a_ = math.cos(2 * pi * h)
    b_ = math.sin(2 * pi * h)
    L = toeInv(l_val)
    cs = getCs(L, a_, b_)
    C0, Cmid, Cmax = cs.C0, cs.Cmid, cs.Cmax
    mid = 0.8
    midInv = 1.25
    if s < mid:
        t = midInv * s
        k1 = mid * C0
        k2 = 1 - k1 / Cmid
        C_val = t * k1 / (1 - k2 * t)
    else:
        t = (s - mid) / (1 - mid)
        k0 = Cmid
        k1 = (1 - mid) * Cmid * Cmid * midInv * midInv / C0
        k2 = 1 - (k1 / (Cmax - Cmid))
        C_val = k0 + t * k1 / (1 - k2 * t)
    lab = Lab(L, C_val * a_, C_val * b_)
    rgbLinear = oklabToLinearSrgb(lab)
    return RGB(
        srgbTransferFunction(rgbLinear.r),
        srgbTransferFunction(rgbLinear.g),
        srgbTransferFunction(rgbLinear.b)
    )

def srgbToOkhsl(rgb: RGB):
    lab = linearSrgbToOklab(RGB(
        srgbTransferFunctionInv(rgb.r),
        srgbTransferFunctionInv(rgb.g),
        srgbTransferFunctionInv(rgb.b)
    ))
    C_val = math.sqrt(lab.a * lab.a + lab.b * lab.b)
    a_ = lab.a / C_val if C_val != 0 else 0
    b_ = lab.b / C_val if C_val != 0 else 0
    L = lab.L
    h = 0.5 + 0.5 * math.atan2(-lab.b, -lab.a) / pi
    cs = getCs(L, a_, b_)
    C0, Cmid, Cmax = cs.C0, cs.Cmid, cs.Cmax
    mid = 0.8
    midInv = 1.25
    if C_val < Cmid:
        k1 = mid * C0
        k2 = 1 - k1 / Cmid
        t = C_val / (k1 + k2 * C_val) if (k1 + k2 * C_val) != 0 else 0
        s = t * mid
    else:
        k0 = Cmid
        k1 = (1 - mid) * Cmid * Cmid * midInv * midInv / C0
        k2 = 1 - (k1 / (Cmax - Cmid)) if (Cmax - Cmid) != 0 else 0
        t = (C_val - k0) / (k1 + k2 * (C_val - k0)) if (k1 + k2 * (C_val - k0)) != 0 else 0
        s = mid + (1 - mid) * t
    l_final = toe(L)
    return HSL(h, s, l_final)

def okhsvToSrgb(hsv):
    h = hsv.h
    s = hsv.s
    v = hsv.v
    a_ = math.cos(2 * pi * h)
    b_ = math.sin(2 * pi * h)
    cusp = findCusp(a_, b_)
    ST_max = toST(cusp)
    S_max, T_max = ST_max.S, ST_max.T
    S0 = 0.5
    k = 1 - S0 / S_max
    L_v = 1 - s * S0 / (S0 + T_max - T_max * k * s)
    C_v = s * T_max * S0 / (S0 + T_max - T_max * k * s)
    L_val = v * L_v
    C_val = v * C_v
    L_vt = toeInv(L_v)
    C_vt = C_v * L_vt / L_v if L_v != 0 else 0
    L_new = toeInv(L_val)
    C_val = C_val * L_new / L_val if L_val != 0 else 0
    L_val = L_new
    rgbScale = oklabToLinearSrgb(Lab(L_vt, a_ * C_vt, b_ * C_vt))
    scaleL = cubeRoot(1 / max(max(rgbScale.r, rgbScale.g), max(rgbScale.b, 0)))
    L_val *= scaleL
    C_val *= scaleL
    rgbLinear = oklabToLinearSrgb(Lab(L_val, C_val * a_, C_val * b_))
    return RGB(
        srgbTransferFunction(rgbLinear.r),
        srgbTransferFunction(rgbLinear.g),
        srgbTransferFunction(rgbLinear.b)
    )

def srgbToOkhsv(rgb):
    lab = linearSrgbToOklab(RGB(
        srgbTransferFunctionInv(rgb.r),
        srgbTransferFunctionInv(rgb.g),
        srgbTransferFunctionInv(rgb.b)
    ))
    C_val = math.sqrt(lab.a * lab.a + lab.b * lab.b)
    a_ = lab.a / C_val if C_val != 0 else 0
    b_ = lab.b / C_val if C_val != 0 else 0
    L = lab.L
    h = 0.5 + 0.5 * math.atan2(-lab.b, -lab.a) / pi
    cusp = findCusp(a_, b_)
    ST_max = toST(cusp)
    S_max, T_max = ST_max.S, ST_max.T
    S0 = 0.5
    k = 1 - S0 / S_max
    t = T_max / (C_val + L * T_max) if (C_val + L * T_max) != 0 else 0
    L_v = t * L
    C_v = t * C_val
    L_vt = toeInv(L_v)
    C_vt = C_v * L_vt / L_v if L_v != 0 else 0
    rgbScale = oklabToLinearSrgb(Lab(L_vt, a_ * C_vt, b_ * C_vt))
    scaleL = cubeRoot(1 / max(max(rgbScale.r, rgbScale.g), max(rgbScale.b, 0)))
    L /= scaleL
    C_val /= scaleL
    C_val = C_val * toe(L) / L if L != 0 else 0
    L = toe(L)
    v = L / L_v if L_v != 0 else 0
    s_val = (S0 + T_max) * C_v / (T_max * S0 + T_max * k * C_v) if (T_max * S0 + T_max * k * C_v) != 0 else 0
    return HSV(h, s_val, v)