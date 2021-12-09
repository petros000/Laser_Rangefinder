import math

class SNR():
    """Класс для расчета SNR"""

    def __init__(self, data, range):
        self.fi_las = math.radians(data["fi_las"][0] / 60)
        self.tau_las = data["tau_las"][0]
        self.P_las = data["W_las"][0] * (10**-3) / (data["t_las"][0] * (10**-9)) * self.tau_las

        self.k_atm = data["k_atm"][0]
        self.range = range

        self.r_tgt = data["r_tgt"][0]
        self.angle_tgt = math.radians(data["angle_tgt"][0])
        self.S_tgt = data["area_tgt"][0]

        self.D_pld = data["D_pld"][0] * (10**-3)
        self.fi_pld = math.radians(data["fi_pld"][0] / 60)
        self.S_pld = data["S_pld"][0]
        self.tau_pld = data["tau_pld"][0]
        self.Pdark_pld = data["Pdark_pld"][0] * (10**-9)

    def calc_P_tgt(self):
        """Расчет мощности отраженной от цели на приемнике"""
        E_las = self.P_las * self.k_atm / (math.pi / 4 * (self.fi_las**2) * (self.range**2))
        I_tgt = E_las / math.pi * self.r_tgt * self.S_tgt * math.cos(self.angle_tgt)
        P_tgt = I_tgt * (math.pi / 4 * self.D_pld**2) * self.tau_pld * self.k_atm / (self.range**2)
        return P_tgt

    def calculation_SNR(self):
        """Расчет SNR"""
        i_dark_pld = self.S_pld * self.Pdark_pld
        i_p_tgt = self.calc_P_tgt() * self.S_pld
        snr = i_p_tgt / i_dark_pld
        return round(snr, 2)