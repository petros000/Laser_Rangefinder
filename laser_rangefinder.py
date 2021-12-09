import sys
from PyQt5 import QtWidgets
import form_LRF
from atm_transmission import AtmospTrans
from snr import SNR

class LRF_App(QtWidgets.QMainWindow, form_LRF.Ui_MainWindow):

    def __init__(self):
        super().__init__()      # доступ к перменным, методам в form_LRF.py
        self.setupUi(self)      # инициализация дизайна
        self.input_data = {}    # инициализация словаря входных данных
        # Запуск расчета
        self.pushButton_start.clicked.connect(self.start_calculation)

    def create_input_data(self):
        """Создание словаря входных данных"""
        self.input_data = {
            # параметры атмосферы
            "tmp": (int(self.spinBox_tmp.text()), self.label_tmp.text()),
            "mdv": (int(self.spinBox_mdv.text()), self.label_mdv.text()),
            "hum": (int(self.spinBox_hum.text()), self.label_hum.text()),
            "pres": (int(self.spinBox_pres.text()), self.label_pres.text()),
            # параметры цели
            "area_tgt": (float(self.doubleSpinBox_area_tgt.text().replace(',', '.')), self.label_area_tgt.text()),
            "H_tgt": (int(self.spinBox_H_tgt.text()), self.label_H_tgt.text()),
            "r_tgt": (float(self.doubleSpinBox_r_tgt.text().replace(',', '.')), self.label_r_tgt.text()),
            "angle_tgt": (int(self.spinBox_angle_tgt.text()), self.label_angle_tgt.text()),
            "type_tgt": ("air_tgt" if self.radioButton_air_tgt
                         else "earth_tgt", self.label_type_tgt.text()),
            # параметры приемника
            "D_pld": (float(self.doubleSpinBox_D_pld.text().replace(',', '.')), self.label_D_pld.text()),
            "H_pld": (int(self.spinBox_H_pld.text()), self.label_H_pld.text()),
            "fi_pld": (int(self.spinBox_fi_pld.text()), self.label_fi_lpd.text()),
            "Pdark_pld": (float(self.doubleSpinBox_Pdark_pld.text().replace(',', '.')), self.label_Pdark_pld.text()),
            "S_pld": (float(self.doubleSpinBox_S_pld.text().replace(',', '.')), self.label_S_pld.text()),
            "tau_pld": (float(self.doubleSpinBox_tau_pld.text().replace(',', '.')), self.label_tau_pld.text()),
            "SNR": (float(self.doubleSpinBox_SNR.text().replace(',', '.')), self.label_SNR.text()),
            # параметры лазера
            "lmd_las": (int(self.spinBox_lmd_las.text()), self.label_lmd_las.text()),
            "fi_las": (float(self.doubleSpinBox_fi_las.text().replace(',', '.')), self.label_fi_las.text()),
            "t_las": (int(self.spinBox_t_las.text()), self.label_t_las.text()),
            "W_las": (float(self.doubleSpinBox_W_las.text().replace(',', '.')), self.label_W_las.text()),
            "tau_las": (float(self.doubleSpinBox_tau_las.text().replace(',', '.')), self.label_tau_las.text())
        }

    def start_calculation(self):
        """Запуск расчета"""
        # Создание словаря входных данных
        self.create_input_data()
        atm_trans = AtmospTrans(self.input_data, 24100)
        k_atm_trans = atm_trans.calculation_transmission()
        self.input_data["k_atm"] = (k_atm_trans, "Коэффициент пропускания атмосферы")
        print(self.input_data)
        snr = SNR(self.input_data, 24100)
        a = snr.calculation_SNR()
        self.label.setText(str(a))


def main():
    """"Инициализация класса"""
    app = QtWidgets.QApplication(sys.argv)
    window = LRF_App()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

