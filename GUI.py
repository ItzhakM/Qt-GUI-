import sys
from tkinter import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (QWidget)
from tkinter import messagebox
fh = open('App_Record', 'w')


class LOGIN_UI(QWidget):
    """This class initialize the Login phase"""
    def __init__(self):
        super(LOGIN_UI, self).__init__()
        ui_path = r"YOUR PATH"
        uic.loadUi(ui_path, self)

    def db_login(self, username="username", password="password"):
        """This function connect to 'testing equipment DB' """
        self._db.connect(username, password, "Testing_Equip")

    def get_due_calibration(self, sn, type):
        """This function get an equipment calibration date"""
        query = self._db.get(type, {"Serial Number": sn})  # This function returns an error when there is no item in DB
        if len(query) == 0:
            return None
        due_cal_date = query[0]['Due calibration date']
        return due_cal_date

    def add_equipment(self, sn, type, due):
        """This function add equipment to the database"""
        self._db.insert(collection=type, obj=[{f'Serial Number': sn, 'Due calibration date': due}])
        pre_check = self._db.get(type, {"Serial Number": sn})  # This function check for duplicating items
        if len(pre_check) == 0:
            return None

    def delete_equipment(self, sn, type):
        """This function delete equipment from the database"""
        self._db.delete_one(collection=type, query={'Serial Number': sn})

    def update_equipment(self, sn, type, due):
        """This function edit equipment in the database"""
        self._db.update(collection=type, query={'Serial Number': sn}, update_value={'Due calibration date': due})


class EQ_UI(QWidget):
    """This class initialize the main UI"""
    def __init__(self):
        super(EQ_UI, self).__init__()
        ui_path = r"your path"
        uic.loadUi(ui_path, self)
        self.ui = self

class EQ_APP():
    """This class represent the application functionality"""
    def __init__(self):
        """This function link between Qt buttons and their functions"""
        self.login_ui = LOGIN_UI()
        self.login_ui.show()
        self.login_ui.Ok_B.clicked.connect(lambda: self.connect_to_dbs())

        self.ui = EQ_UI()
        self.get_clicked, self.add_clicked = False, False
        self.get_performed_before_change = False  # get first and delete/update are secondaries
        self.ui.Delete.hide()
        self.ui.Edit.hide()
        self.ui.Delete.setDisabled(True)
        self.ui.Edit.setDisabled(True)
        self.ui.cbStart.clicked.connect(self.get_clicked_event)
        self.ui.cbCont_2.clicked.connect(self.add_clicked_event)
        self.ui.Edit.clicked.connect(self.edit_clicked_event)
        self.ui.Delete.clicked.connect(self.delete_clicked_event)
        self.ui.finish.clicked.connect(self.perform_clicked)


    def connect_to_dbs(self):
        """This function connect between the two UIs"""
        password = self.login_ui.Password_B.text()
        username = self.login_ui.Username_B.text()
        if (username == "username" and password == "pssword") or (username == "" and password == ""):
            self.login_ui.hide()
            self.db = Equipment_DB()
            self.db.db_login()
            self.ui.show()
        else:
            self.Message('Error', "Wrong Username/Password")

    def _unset_all(self):
        """This function initializes the app to start"""
        self.get_clicked = False
        self.add_clicked = False
        self.edit_clicked = False
        self.delete_clicked = False

    def Message(self, title, txt):
        """This function creates a messagebox"""
        root = Tk()
        root.withdraw()
        messagebox.showinfo(title, txt)
        root.destroy()

    def yes_no_msg(self, title, txt):
        """This function raise a second type of messagebox"""
        root = Tk()
        root.withdraw()
        ans = messagebox.askyesno(title=title, message=txt)
        root.destroy()
        return ans

    def get_clicked_event(self):
        """This function transfer to the get function if clicked"""
        self._unset_all()
        self.get_clicked = True

    def add_clicked_event(self):
        """This function transfer to the add function if clicked"""
        self._unset_all()
        self.add_clicked = True
        self.ui.Delete.setDisabled(True)
        self.ui.Edit.setDisabled(True)
        self.ui.Delete.hide()
        self.ui.Edit.hide()

    def edit_clicked_event(self):
        """This function transfer to the edit function if clicked"""
        self._unset_all()
        self.edit_clicked = True
        self.perform_clicked()

    def delete_clicked_event(self):
        """This function transfer to the delete function if clicked"""
        self._unset_all()
        self.get_clicked_event()
        self.delete_clicked = True
        self.perform_clicked()

    def perform_clicked(self):
        """Main Back-end. This object initializes all the functions and their functionalities"""
        rbtn1 = self.ui.cbStart.isChecked()
        rbtn2 = self.ui.cbCont_2.isChecked()
        if rbtn1 == rbtn2:
            self.Message('Error', 'Choose and operator: Get/Add !')
            return

        type = self.ui.ASREV_2.currentText()
        if '' == type:
            self.Message('Error', 'Choose system type !')
            return

        serial_number = self.ui.ASSN_2.text()
        if '' == serial_number:
            self.Message('Error', 'Enter serial number !')
            return

        due_calibration = self.ui.ASSN_3.text()
        if not self.get_clicked:
            if '' == due_calibration:
                self.Message('Error', 'Enter calibration date !')
                return

        performed_by = self.ui.MTESTER.currentText()
        if '' == performed_by and not self.get_clicked:
            self.Message('Error', 'Choose a performer !')
            return

        if self.get_clicked:
            date_cal = self.db.get_due_calibration(serial_number, type)
            if date_cal == None:
                self.Message('Error', 'Serial number does not exist !')
                return
            self.ui.ASSN_3.setText(self.db.get_due_calibration(serial_number, type))
            self.get_performed_before_change = True
            fh = open('App_Record.txt', 'a')
            fh.write('\n\nOperator: Get an equipment')
            fh.write('\nType: ' + type)
            fh.write('\nSerial: ' + serial_number)
            fh.write('\nCalibration: ' + due_calibration)
            fh.write('\nPerformed By: ' + performed_by)
            fh.close()
            self.ui.Delete.setDisabled(False)
            self.ui.Edit.setDisabled(False)
            self.ui.Delete.show()
            self.ui.Edit.show()

            if self.delete_clicked:
                type = self.ui.ASREV_2.currentText()
                if '' == type:
                    self.Message('Error', 'Choose system type !')
                    return

                serial_number = self.ui.ASSN_2.text()
                if '' == serial_number:
                    self.Message('Error', 'Enter serial number !')
                    return

                due_calibration = self.ui.ASSN_3.text()
                if not self.get_clicked:
                    if '' == due_calibration:
                        self.Message('Error', 'Enter calibration date !')
                        return

                performed_by = self.ui.MTESTER.currentText()
                if '' == performed_by:
                    self.Message('Error', 'Choose a performer !')
                    return

                if self.delete_clicked:
                    self.db.delete_equipment(serial_number, type)
                    self.Message('Success', 'Delete succeeded')
                    fh = open('App_Record.txt', 'a')
                    fh.write('\n\nOperator: delete a equipment')
                    fh.write('\nType: ' + type)
                    fh.write('\nSerial: ' + serial_number)
                    fh.write('\nCalibration: ' + due_calibration)
                    fh.write('\nPerformed By: ' + performed_by)
                    fh.close()
                    # self.ui.Delete.setDisabled(True)
                    # self.ui.Edit.setDisabled(True)
                    self.ui.Delete.hide()
                    self.ui.Edit.hide()
                    self.delete_clicked = False


        elif self.add_clicked:
            data_cal = self.db.get_due_calibration(serial_number, type)
            if data_cal == None:
                self.db.add_equipment(serial_number, type, due_calibration)
                self.Message('Success', 'Add succeeded')
                fh = open('App_Record.txt', 'a')
                fh.write('\n\nOperator: Add a new equipment')
                fh.write('\nType: ' + type)
                fh.write('\nSerial: ' + serial_number)
                fh.write('\nCalibration: ' + due_calibration)
                fh.write('\nPerformed By: ' + performed_by)
                fh.close()
                self.add_clicked = True
                self.add_clicked_event()
            else:
                ans = self.yes_no_msg('WARNING', f'This equipment already exist !\n\n Type:  {type}\n Serial:  {serial_number}\n \
due:  {data_cal}\n By clicking "yes" you will replace this item while the old one will delete')
                if ans == True:
                    # self.db.delete_equipment(serial_number, type)
                    # self.db.add_equipment(serial_number, type, due_calibration)
                    self.db.update_equipment(serial_number, type, due_calibration)
                    self.Message('Success', 'Add succeeded')
                    fh = open('App_Record.txt', 'a')
                    fh.write('\n\nOperator: Edit equipment')
                    fh.write('\nType: ' + type)
                    fh.write('\nSerial: ' + serial_number)
                    fh.write('\nCalibration: ' + due_calibration)
                    fh.write('\nPerformed By: ' + performed_by)
                    fh.close()
                    self.add_clicked = True
                    self.add_clicked_event()


        elif self.edit_clicked:
            self.db.update_equipment(serial_number, type, due_calibration)
            self.Message('Success', 'Edit succeeded')
            self.db.get_due_calibration(serial_number, type)
            # self.ui.Delete.setDisabled(True)
            # self.ui.Edit.setDisabled(True)
            fh = open('App_Record.txt', 'a')
            fh.write('\n\nOperator: Edit equipment')
            fh.write('\nType: ' + type)
            fh.write('\nSerial: ' + serial_number)
            fh.write('\nCalibration: ' + due_calibration)
            fh.write('\nPerformed By: ' + performed_by)
            fh.close()
            self.ui.Delete.hide()
            self.ui.Edit.hide()
            self.get_clicked_event()


if __name__ == '__main__':  # Execute the Front-end
    app = QtWidgets.QApplication(sys.argv)
    sw = EQ_APP()
    sys.exit(app.exec_())
