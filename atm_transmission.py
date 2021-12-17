import math
from scipy import interpolate

class AtmospTrans():
    """Класс для расчета коэффициента пропускания атмосферы"""

    def __init__(self, data):
        self.mdv = data["mdv"][0]       # мдв, км
        self.tmp = data["tmp"][0]       # температура, С
        self.hum = data["hum"][0]       # влажность, %
        self.press = data["pres"][0]    # давление, мбар
        self.h_tgt = data["H_tgt"][0]   # высота цели, м
        self.h_ld = data["H_pld"][0]     # высота ЛД, м
        self.lmd = data["lmd_las"][0]       # длина волны, нм
        #self.range = range              # дальность, м
        self.del_h = 100                # шаг расчетов по высоте для наклонной трассы, м
        self.del_h_tgt_ld = abs(self.h_tgt - self.h_ld)

    def func_tmp_for_h(self, h):
        """Возвращает температуру воздуха на разной высоте"""
        tmp_h = round(self.tmp + 273 - 0.0065 * h, 4)
        return tmp_h

    def func_pres_for_h(self, h):
        """Возвращает давление воздуха на разной высоте"""
        press_h = round(self.press * ((1 - (h/44308)) ** 5.255), 4)
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
        return round(k, 4)

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

    def calc_aerosol_scattering(self, rang):
        """Вовзращает коэффициент пропускания за счет аэрозольного рассеяния"""
        if self.del_h_tgt_ld == 0:
            alp = self.alp_aerosol_scattering(self.h_tgt)
            tau = math.exp(- alp * rang)
        else:
            tau = 1
            n_h = self.del_h_tgt_ld // self.del_h
            r_h = rang // n_h
            for i in range(n_h):
                alp = self.alp_aerosol_scattering(i * self.del_h + min(self.h_tgt, self.h_ld))
                tau = tau * math.exp(- alp * r_h)
        return round(tau, 4)

    def betta_molecul_scattering(self, h):
        """Вовзращает показатель молекулярного ослабления"""
        press_h = self.func_pres_for_h(h)
        tmp_h = self.func_tmp_for_h(h)
        betta = 1.09 * (10**-3) * press_h * (self.tmp + 273) / tmp_h / self.press * ((self.lmd * (10**-3)) ** -4) * (10 ** -3)
        return betta

    def calc_molecul_scattering(self, rang):
        """Вовзращает коэффициент пропускания за счет молекулярного рассеяния"""
        if self.del_h_tgt_ld == 0:
            betta = self.betta_molecul_scattering(self.h_tgt)
            tau = math.exp(- betta * rang)
        else:
            tau = 1
            n_h = self.del_h_tgt_ld // self.del_h
            r_h = rang // n_h
            for i in range(n_h):
                betta = self.betta_molecul_scattering(i * self.del_h + min(self.h_tgt, self.h_ld))
                tau = tau * math.exp(- betta * r_h)
        return round(tau, 4)

    def calc_water(self):
        """Расчет количесвта воды вдоль трассы"""
        tmp_x = [-50, -30, -20, -10, 10, 20, 30, 50]
        e_y = [6.356 * 10**-6, 5.088 * 10**-5, 1.254 * 10**-4, 2.863 * 10**-4, 1.227 * 10**-3, 2.337 * 10**-3, 4.243 * 10**-3, 1.234 * 10**-2]
        e_interp = interpolate.interp1d(tmp_x, e_y, kind='cubic')
        res = e_interp(self.tmp)
        return res

    def calc_molecul_absorption(self):
        """Возвращает коэффициент пропускания за счет молекулярного поглощения (только вода)"""
        print(self.calc_water())

    def calculation_transmission(self, rang):
        #self.calc_molecul_absorption()
        res = self.calc_aerosol_scattering(rang) * self.calc_molecul_scattering(rang)
        return round(res, 4)

