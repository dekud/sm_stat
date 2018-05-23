#! /usr/bin/env python3.5

import os, uuid
import tornado.ioloop
import tornado.web
import logАnalitic as la
current_xls_file  = ""

class Event:
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
        _file_path = "%s/%s" % (_file_dir, file_name)
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
        cname = fname +".log"
        fh = open(cname, 'wb')
        fh.write(fileinfo['body'])


        loga = la.LogAnalitic()
        loga.load_file(cname)
        current_xls_file = fname + ".xlsx"
        loga.save_as_xlsx(current_xls_file)


        events_dict =loga.get_events_count()
        events = []

        for v in sorted(events_dict, key = events_dict.__getitem__, reverse= True):
            ev = Event()
            ev.name = v
            ev.count= events_dict[v]
            events.append(ev)

        self.render('statistic.html', events=events, filename = current_xls_file)

        return


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/getfile", DownloadHandler),
        (r"/upload", UploadHandler)
    ])



if __name__ == "__main__":
    print('main')

    app = make_app()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
