#! /usr/bin/env python3.5
import re
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import rcParams

rcParams.update({'figure.autolayout': True})


class EventLine:
    datetime = ""
    station = ""
    syscode = ""
    type = ""
    event = ""
    eventclass =""

    def __init__(self):
        pass

    def __init__(self, ar):
        self.datetime = ar[0]
        self.station = ar[1]
        self.syscode = ar[2]
        self.type = ar[3]
        self.event = self.clear_event(ar[4])
        self.eventclass = "Другие"

    def clear_event(self, strline):
        p = re.compile('(\d{2,2}.\d{2,2}.\d{4,4} \d{2,2}:\d{2,2}:\d{2,2})')
        s = p.sub('', strline)
        p = re.compile('(\t)')
        s = p.sub('', s)
        return s

class LogAnalitic:
    eventdata = {}

    def __init__(self, fpath):
        self.eventdata['datetime'] = []
        self.eventdata['station'] = []
        self.eventdata['syscode'] = []
        self.eventdata['type'] = []
        self.eventdata['event'] = []
        self.eventdata['source'] = []
        self.eventdata['eventclass'] = []
        self.fpath = fpath
        pass

    def push_event_line(self,event_line,source):
        self.eventdata['datetime'].append(event_line.datetime)
        self.eventdata['station'].append(event_line.station)
        self.eventdata['syscode'].append(event_line.syscode)
        self.eventdata['type'].append(event_line.type)
        self.eventdata['event'].append(event_line.event)
        self.eventdata['eventclass'].append(event_line.eventclass)
        self.eventdata['source'].append(source)

    def load_file(self, filename):
        f = open(filename, 'r', encoding='cp1251')
        self.parse_log_file(f)
        f.close()

    def parse_log_file(self, f):
        for line in f:
            ar = self.splitline(line)
            if len(ar) < 5:
                pass
                # print(line+"\n\n\n\n")
            else:
                event_line = EventLine(ar)
                # ar[4] = self.clear_event(ar[4])

                if event_line.type == 'ОC СM' or event_line.type == 'ПC CМ':

                    is128, num = self.is_ev128_129(event_line.event)

                    if is128:
                        event_line.event = 'Перенахождение'
                        event_line.station = num
                        event_line.eventclass = 'Перестроение'

                    if self.is_ev_connect(event_line.event):
                        event_line.event = 'Восстановление связи с ПС'
                        event_line.eventclass = 'Связь с ПС'

                    if r"Потеря связи с ПС" in event_line.event:
                        event_line.eventclass = 'Связь с ПС'

                    if r"220В" in event_line.event:
                        event_line.eventclass = 'Неисправность'

                    if r"Корпус" in event_line.event:
                            event_line.eventclass = 'Неисправность'

                    if r"аккум" in event_line.event:
                            event_line.eventclass = 'Неисправность'

                    if self.is_ev_station_on(event_line.event):
                        event_line.event = 'Включение станции'
                        event_line.eventclass = 'Неисправность'

                    isSub, num = self.is_ev_substitution(event_line.event)

                    if isSub:
                        event_line.event = 'Попытка подмены станции'
                        event_line.station = num
                        event_line.eventclass = 'Подмена станции'
                        self.push_event_line(event_line,line)

                else:
                    event_line.event = 'Событие от: ' + event_line.type
                    event_line.eventclass = 'От объект. оборудования'


                if r"Потеря связи с устройством оповещения" in event_line.event:
                    event_line.event = r"Потеря связи с БСМС"
                    event_line.eventclass = 'Неисправность'

                if r"Восстановление связи с устройством оповещения" in event_line.event:
                    event_line.event = r"Восстановление связи с БСМС"
                    event_line.eventclass = 'Неисправность'

                if r"Потеря связи с объектовым оборудованием" in event_line.event:
                    event_line.event = r"Потеря связи с ОО"
                    event_line.eventclass = 'Неисправность'

                if r"Восстановление связи с объектовым оборудованием" in event_line.event:
                    event_line.event = r"Восстановление связи с ОО"
                    event_line.eventclass = 'Неисправность'

                if r"Сообщение получено" in event_line.event:
                    event_line.event = r"Сообщение получено"
                    event_line.eventclass = 'Оповещение'

                self.push_event_line(event_line, line)

                # print(ar)

    def get_syscode_count(self):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        vc = df['syscode'].value_counts()
        dvc = dict(vc)
        return len(dvc)

    def get_events_count(self):
        df = pd.DataFrame(self.eventdata)

        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        # df = df[df['station'] == 878]
        vc = df['event'].value_counts(ascending=True)
        dvc = dict(vc)
        # dvc['total'] = len(self.eventdata['event'])
        dvc['total'] = df['event'].count()
        plt.gcf().clear()

        vc = df['eventclass'].value_counts(ascending=True)
        vc.plot(stacked=True, linestyle="dotted", kind='barh', rot=00)

        # vc = df['eventclass'].value_counts(ascending=True)
        # vc.plot(stacked=True, legend=True, kind='hist', rot=00, color='b')
        fig = plt.gcf()
        fig.set_figheight(4)
        fig.set_figwidth(5)
        fig.savefig(self.fpath + 'event.png')

        return dvc

    def get_events_syscode_count(self):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        # vc = df.pivot_table(index = ['syscode','event'],values=['station'],aggfunc= np.count_nonzero)
        vc = df.pivot_table(index=['syscode', 'event'], values=['station'], aggfunc={'station': 'count'})

        dvc = vc['station'].to_dict()
        plt.gcf().clear()

        vc.plot(stacked=True, legend=True, linestyle="dotted", kind='barh', rot=00, color='b')
        fig = plt.gcf()
        fig.set_figheight(7)
        fig.savefig(self.fpath + 'syscode_event.png')

        return dvc

    def get_stations_count(self):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        vc = df['station'].value_counts(ascending=True)

        dvc = dict(vc)

        dvc10 = dict(sorted(dvc.items(), key=lambda item: item[1], reverse=True))
        dvc = dict()
        ind = 0
        for item in dvc10.items():
            dvc[item[0]] = item[1]
            ind = ind + 1
            if ind == 20:
                break


        vc = pd.Series(dvc,name='station').sort_values()
        plt.gcf().clear()
        vc.plot(stacked=True, linestyle="dotted", kind='barh', rot=00)
        fig = plt.gcf()
        fig.set_figheight(4)
        fig.set_figwidth(5)

        fig.savefig(self.fpath + 'station.png')

        return dvc

    def get_os_events_count(self,os):
        df = pd.DataFrame(self.eventdata)

        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        df = df[df['station'] == os]
        vc = df['event'].value_counts(ascending=True)
        dvc = dict(vc)
        dvc['total'] = df['event'].count()
        # plt.gcf().clear()
        #
        # vc.plot(stacked=True, legend=True, linestyle="dotted", kind='barh', rot=00, color='b')
        # fig = plt.gcf()
        # fig.set_figheight(7)
        # fig.set_figwidth(9)
        # fig.savefig(self.fpath + 'event.png')

        return dvc

    def get_events_stations_count(self,ev):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        df = df[df['event'] == ev]
        vc = df['station'].value_counts(ascending=True)

        dvc = dict(vc)

        dvc10 = dict(sorted(dvc.items(), key=lambda item: item[1], reverse=True))
        dvc = dict()
        ind = 0
        for item in dvc10.items():
            dvc[item[0]] = item[1]
            ind = ind + 1
            if ind == 10:
                break

        return dvc

    def save_as_xlsx(self, xlsname):
        df = pd.DataFrame(self.eventdata)
        df['syscode'] = df['syscode'].astype('int64')
        df['station'] = df['station'].astype('int64')
        writer = pd.ExcelWriter(self.fpath + xlsname, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='data', index=False,
                    columns=['datetime', 'syscode', 'type', 'station', 'event', 'source'])

        worksheet = writer.sheets['data']
        worksheet.set_column('A:A', 30, None)
        worksheet.set_column('B:B', 10, None)
        worksheet.set_column('C:C', 20, None)
        worksheet.set_column('D:D', 10, None)
        worksheet.set_column('E:E', 50, None)
        worksheet.set_column('F:F', 50, None)
        writer.save()

    def splitline(self, strline):
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



    def is_ev128_129(self, strline):
        regex = r"Служ[а-яА-Я,a-zA-Z,:,\s]+\d{3,3}\s(\d{1,5})"
        matches = re.findall(regex, strline)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, 0

    def is_ev_connect(self, strline):
        regex = r"Восстановление связи с ПС"
        if regex in strline:
            return True
        else:
            return False

    def is_ev_station_on(self, strline):
        regex = r"Включение станции"
        if regex in strline:
            return True
        else:
            return False

    def is_ev_substitution(self, strline):
        regex = r"Попытка подмены станции\s(\d{1,5})"
        matches = re.findall(regex, strline)
        if len(matches) > 0:
            return True, matches[0]
        else:
            return False, 0
