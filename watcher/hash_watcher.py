  """with open(path, 'rb') as f:
                    a = hashlib.new('blake2s')
                    done = False
                    while not done:
                        chunk = f.read(1024)
                        if len(chunk) == 0:
                            ptr.execute('''INSERT INTO files (fname, data, size, lm) VALUES (?, ?, ?);''', [path, a.hexdigest(), os.getsize(path), os.path.getmtime(path)])
                            db.commit()
                            done = True
                        a.update(f.read(1))"""
