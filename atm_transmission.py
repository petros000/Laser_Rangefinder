import math


class AtmospTrans():
    """Класс для расчета коэффициента пропускания атмосферы"""

    def __init__(self, data, range):
        self.mdv = data["mdv"][0]       # мдв, км
        self.tmp = data["tmp"][0]       # температура, С
        self.hum = data["hum"][0]       # влажность, %
        self.press = data["pres"][0]    # давление, мбар
        self.h_tgt = data["H_tgt"][0]   # высота цели, м
        self.h_ld = data["H_pld"][0]     # высота ЛД, м
        self.lmd = data["lmd_las"][0]       # длина волны, нм
        self.range = range              # дальность, м
        self.del_h = 100                # шаг расчетов по высоте для наклонной трассы, м

    def func_tmp_for_h(self, h):
        """Возвращает температуру воздуха на разной высоте"""
        tmp_h = round(self.tmp + 273 - 0.0065 * h, 3)
        return tmp_h

    def func_pres_for_h(self, h):
        """Возвращает давление воздуха на разной высоте"""
        press_h = round(self.press * ((1 - (h/44308)) ** 5.255), 3)
        return press_h

    def calc_k_mdv(self):
        """Возвращает поправочный коэффицциент для расчет аэрозольного ослабления"""
        k = 0
        if self.mdv < 6:
            k = 0.585 * (self.mdv ** (1/3))
        elif 6 <= self.mdv <= 20:
            k = 1.3
        elif self.mdv > 20:
            k = 1.5
        return round(k, 3)

    def calc_k_h(self):
        """Поправочный коэффициент для МДВ от высоты"""
        k_h = round(5 / (6.65 - math.log(self.mdv)), 3)
        return k_h

    def alp_aerosol_scattering(self, h):
        """Вовзращает показатель аэрозольного ослабления"""
        k_mdv = self.calc_k_mdv()
        k_h = self.calc_k_h()
        alp = (3.9 / self.mdv) * ((0.55 / (self.lmd * 10**-3)) ** k_mdv) * math.exp(- (h * 10**-3) / k_h) * 10**-3
        return alp

    def calc_aerosol_scattering(self):
        """Вовзращает коэффициент пропускания за счет аэрозольного рассеяния"""
        del_h_tgt_ld = abs(self.h_tgt - self.h_ld)
        if del_h_tgt_ld == 0:
            alp = self.alp_aerosol_scattering(self.h_tgt)
            tau = math.exp(- alp * self.range)
        else:
            tau = 1
            n_h = del_h_tgt_ld // self.del_h
            r_h = self.range // n_h
            for i in range(n_h):
                alp = self.alp_aerosol_scattering(i * self.del_h + min(self.h_tgt, self.h_ld))
                tau = tau * math.exp(- alp * r_h)
        return round(tau, 3)

    def betta_molecul_scattering(self, h):
        """Вовзращает показатель молекулярного ослабления"""
        press_h = self.func_pres_for_h(h)
        tmp_h = self.func_tmp_for_h(h)
        betta = 1.09 * (10**-3) * press_h * (self.tmp + 273) / tmp_h / self.press * ((self.lmd * (10**-3)) ** -4) * (10 ** -3)
        return betta

    def calc_molecul_scattering(self):
        """Вовзращает коэффициент пропускания за счет молекулярного рассеяния"""
        del_h_tgt_ld = abs(self.h_tgt - self.h_ld)
        if del_h_tgt_ld == 0:
            betta = self.betta_molecul_scattering(self.h_tgt)
            tau = math.exp(- betta * self.range)
        else:
            tau = 1
            n_h = del_h_tgt_ld // self.del_h
            r_h = self.range // n_h
            for i in range(n_h):
                betta = self.betta_molecul_scattering(i * self.del_h + min(self.h_tgt, self.h_ld))
                tau = tau * math.exp(- betta * r_h)
        return round(tau, 3)

    def calculation_transmission(self):
        res = self.calc_aerosol_scattering() * self.calc_aerosol_scattering()
        return round(res, 3)

