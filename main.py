#! /usr/bin/env python3.5

import os, uuid
import tornado.ioloop
import tornado.web
import logАnalitic as la
current_xls_file  = ""

class Event:
    name = ""
    count = 0

class SyscodeEvent:
    sys_code = 0
    name = ""
    count = 0

class Station:
    name = ""
    count = 0

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        pass
        self.render('index.html')



class DownloadHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.request)
        file_name = self.get_argument('filename')
        # file_name = "log.xlsx"
        # print(current_xls_file)
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
        fileinfo = self.request.files['myFile'][0]
        print("fileinfo is", fileinfo)
        fname = fileinfo['filename']
        extn = os.path.splitext(fname)[1]
        cname = "./uploads/" +fname +".log"
        fh = open(cname, 'wb')
        fh.write(fileinfo['body'])


        loga = la.LogAnalitic("./uploads/")
        loga.load_file(cname)
        current_xls_file = fname + ".xlsx"
        loga.save_as_xlsx(current_xls_file)

        sc_dict = loga.get_syscode_count()
        sc_count = len(sc_dict)

        if(sc_count == 1):
            events_dict =loga.get_events_count()
            events = []

            for v in sorted(events_dict, key = events_dict.__getitem__, reverse= True):
                if v != 'total':
                    ev = Event()
                    ev.name = v
                    ev.count= events_dict[v]
                    events.append(ev)

            ev = Event()
            ev.name = 'total'
            ev.count = events_dict['total']
            events.append(ev)

            stations_dict = loga.get_stations_count()
            stations = []

            for v in sorted(stations_dict, key = stations_dict.__getitem__, reverse= True):
                st = Station()
                st.name = v
                st.count= stations_dict[v]
                stations.append(st)

            self.render('statistic.html', events=events, filename = current_xls_file, stations = stations )
        else:

            scevents_dict = loga.get_events_syscode_count()

            scevents = []

            for v in sorted(scevents_dict, key = scevents_dict.__getitem__, reverse= True):
                ev = SyscodeEvent()
                ev.name = v[1]
                ev.sys_code = v[0]
                ev.count= scevents_dict[v]
                scevents.append(ev)

            self.render('statistic.html', filename = current_xls_file, scevents = scevents)

        return


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/getfile", DownloadHandler),
        (r"/upload", UploadHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r'/uploads/(.*)', tornado.web.StaticFileHandler, {'path': 'uploads/'})
    ])


if __name__ == "__main__":
    print('main')

    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
