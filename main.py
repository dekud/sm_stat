#! /usr/bin/env python3.5

import os, uuid
import tornado.ioloop
import tornado.web
import logAnalitic as la

class Event:
    name = ""
    count = 0
    id = 0
    stations = []

class SyscodeEvent:
    sys_code = 0
    name = ""
    count = 0

class Station:
    name = ""
    count = 0
    events = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        pass
        self.render('index.html')



class DownloadHandler(tornado.web.RequestHandler):
    def get(self):
        file_name = self.get_argument('filename')
        _file_dir = os.path.abspath("") + "/"
        _file_path = "%s/%s" % (_file_dir, "/uploads/"+file_name)
        if not file_name or not os.path.exists(_file_path):
            raise tornado.web.HTTPError(404)
        self.set_header('Content-Type', 'application/force-download')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        with open(_file_path, "rb") as f:
            try:
                while True:
                    _buffer = f.read(4096)
                    if _buffer:
                        self.write(_buffer)
                    else:
                        f.close()
                        self.finish()
                        return
            except:
                raise tornado.web.HTTPError(404)

        raise tornado.web.HTTPError(500)

class UploadHandler(tornado.web.RequestHandler):
    def post(self):

        loga = la.LogAnalitic("./uploads/")

        try:
            for fi in self.request.files['myFile']:
                print(fi['filename'])
                f = fi['body'].decode('cp1251')
                loga.parse_log_file(f.splitlines())

            fileinfos = self.request.files['myFile']
            fname = fileinfos[0]['filename']
        except:
            self.redirect("/")

        if len(fileinfos) > 1:
            fn_start = fileinfos[0]['filename']
            fn_end = fileinfos[-1]['filename']
            fname = fn_start[:-4]+"_"+fn_end[:-4]

        current_xls_file = fname + ".xlsx"
        loga.save_as_xlsx(current_xls_file)

        sc_count = loga.get_syscode_count()

        if sc_count == 1:
            events = self.event_list(loga)
            stations = self.station_list(loga)
            self.render('statistic.html', events=events, stations=stations,filename = current_xls_file)
        else:
            scevents = self.sc_event_list(loga)
            self.render('statistic.html', filename = current_xls_file, scevents = scevents)

        return

    def sc_event_list(self, loga):
        scevents_dict = loga.get_events_syscode_count()
        scevents = []
        for v in sorted(scevents_dict, key=scevents_dict.__getitem__, reverse=True):
            ev = SyscodeEvent()
            ev.name = v[1]
            ev.sys_code = v[0]
            ev.count = scevents_dict[v]
            scevents.append(ev)
        return scevents

    def station_list(self, loga):
        stations_dict = loga.get_stations_count()
        stations = []
        for s in sorted(stations_dict, key=stations_dict.__getitem__, reverse=True):
            st = Station()
            st.name = s
            st.count = stations_dict[s]
            ed = loga.get_os_events_count(s)
            evs = []
            for v in sorted(ed, key=ed.__getitem__, reverse=True):
                if v != 'total':
                    e = Event()
                    e.name = v
                    e.count = ed[v]
                    evs.append(e)

            e = Event()
            e.name = 'total'
            e.count = ed['total']
            evs.append(e)
            st.events = evs
            stations.append(st)
        return stations

    def event_list(self, loga):
        events_dict = loga.get_events_count()
        print(events_dict)
        events = []
        ind = 0
        for v in sorted(events_dict, key=events_dict.__getitem__, reverse=True):
            if v != 'total':
                stdict = loga.get_events_stations_count(v)
                ev = Event()
                ev.id = ind + 0xDA
                ind = ind + 1
                ev.name = v
                ev.count = events_dict[v]
                ev_s = []
                for s in sorted(stdict, key=stdict.__getitem__, reverse=True):
                    st = Station()
                    st.name = s
                    st.count = stdict[s]
                    ev_s.append(st)

                ev.stations = ev_s
                print(ev.stations)

                events.append(ev)
        ev = Event()
        ev.name = 'total'
        ev.count = events_dict['total']
        events.append(ev)
        return events


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # self.set_header("Cache-control", "no-cache")
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/getfile", DownloadHandler),
        (r"/upload", UploadHandler),
        (r'/static/(.*)', NoCacheStaticFileHandler, {'path': 'static/'}),
        (r'/uploads/(.*)', NoCacheStaticFileHandler, {'path': 'uploads/'})
    ])


if __name__ == "__main__":
    print('main')

    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
