#! /usr/bin/env python3.5
import re
import pandas as pd


import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

class LogAnalitic:
    eventdata = {}

    def __init__(self):
        self.eventdata['datetime'] = []
        self.eventdata['station'] = []
        self.eventdata['syscode'] = []
        self.eventdata['type'] = []
        self.eventdata['event'] = []
        self.eventdata['source'] = []
        pass

    def load_file(self, filename):
        f = open(filename,'r', encoding='cp1251')
        for line in f:
            ar = self.splitline(line)

            if len(ar) < 5:
                pass
                # print(line+"\n\n\n\n")
            else:
                ar[4] = self.clear_event(ar[4])

                if ar[3] == 'ОC СM' or ar[3] == 'ПC CМ':
                    is128, num = self.ev128_129(ar[4])
                    if is128:
                        ar[4] = 'Перенахождение'
                        ar[1] = num

                    if self.ev_connect(ar[4]):
                        ar[4] = 'Восстановление связи с ПС'

                    if self.ev_station_on(ar[4]):
                        ar[4] = 'Включение станции'
                    isSub, num = self.ev_substitution(ar[4])
                    if isSub:
                        ar[4] = 'Попытка подмены станции'
                        self.eventdata['datetime'].append(ar[0])
                        self.eventdata['station'].append(num)
                        self.eventdata['syscode'].append(ar[2])
                        self.eventdata['type'].append(ar[3])
                        self.eventdata['event'].append(ar[4])
                        self.eventdata['source'].append(line)

                else:
                    ar[4] = 'Событие от объектового оборудования: ' + ar[3]

                self.eventdata['datetime'].append(ar[0])
                self.eventdata['station'].append(ar[1])
                self.eventdata['syscode'].append(ar[2])
                self.eventdata['type'].append(ar[3])
                self.eventdata['event'].append(ar[4])
                self.eventdata['source'].append(line)

                # print(ar)

        f.close()

    def get_events_count(self):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        vc = df['event'].value_counts()
        dvc = dict(vc)

        vc.plot(stacked = True, legend = True, linestyle = "dotted",kind='bar', rot=90)
        fig = plt.gcf()
        # fig.set_figwidth(500)
        # fig.set_figheight(600)
        fig.savefig('output.png')

        return dvc

    def get_stations_count(self):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        vc = df['station'].value_counts()
        dvc = dict(vc)
        return dvc

    def save_as_xlsx(self,xlsname):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        writer = pd.ExcelWriter(xlsname, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='data', index = False, columns=['datetime','syscode','type','station','event','source'])
        workbook = writer.book
        worksheet = writer.sheets['data']
        worksheet.set_column('A:A',30,None)
        worksheet.set_column('B:B',10,None)
        worksheet.set_column('C:C',20,None)
        worksheet.set_column('D:D',10,None)
        worksheet.set_column('E:E',50,None)
        worksheet.set_column('F:F',50,None)
        writer.save()

    def splitline(self,strline):
        regex = r"(\d{2,2}.\d{2,2}.\d{4,4} \d{2,2}:\d{2,2}:\d{2,2})[\s,\t]+([0-9]{1,5})[\s,\t]+.([1-9]{1,3}).[\s,\t]+\d{2,2}.[\s,\t]" \
                r"([а-я,А-Я,a-z,A-Z]{2,6}[ ]*[а-я,А-Я,a-z,A-Z]{0,6})" \
                r"[\s,\t]+(.+)"
        matches = re.finditer(regex, strline)
        ar = []
        for match in matches:
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                ar.append(match.group(groupNum))
        return ar

    def clear_event(self,strline):
        p = re.compile('(\d{2,2}.\d{2,2}.\d{4,4} \d{2,2}:\d{2,2}:\d{2,2})')
        s = p.sub('',strline)
        p = re.compile('(\t)')
        s = p.sub('',s)
        return s

    def ev128_129(self,strline):
        regex = r"Служ[а-яА-Я,a-zA-Z,:,\s]+\d{3,3}\s(\d{1,5})"
        matches = re.findall(regex, strline)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, 0

    def ev_connect(self, strline):
        regex = r"Восстановление связи с ПС"
        if regex in strline :
            return True
        else:
            return False

    def ev_station_on(self, strline):
        regex = r"Включение станции"
        if regex in strline :
            return True
        else:
            return False

    def ev_substitution(self,strline):
        regex = r"Попытка подмены станции\s(\d{1,5})"
        matches = re.findall(regex, strline)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, 0
