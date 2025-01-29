import os



def get_files(parent):
    files = os.listdir(parent)
    out = {}
    while True:
        if len(files) == 0:
            return(out)

        path = os.path.join(parent, files[0])
        if os.path.isfile(path):
            out[path] = {'lm': os.path.getmtime(path), 'size': os.path.getsize(path)}
            files.pop(0)
        else:
            for e in os.listdir(path):
                files.append(os.path.join(files[0], e))
            files.pop(0)
    return(out)

class Watcher:
    #should this even be its own class?
    def __init__(self, config_path, watchee):
        self.watchee = watchee
        self.flist = get_files(watchee)

    def update(self, current):
        changed = False
        for f in current:
            try:
                m = os.path.getmtime(f)
                s = os.path.getsize(f)
                if (m > self.flist[f]['lm']) or (s != self.flist[f]['size']):
                    self.flist[f] = {'lm': m, 'size': s}
                    changed = True
            except OSError:
                if not os.path.exists(f):
                    self.flist.pop(f)
                    changed = True
            except KeyError:
                self.flist[f] = {'lm': m, 'size': s}
                changed = True
        return(changed) #WoOoOoOO side effects OoOooO
























