#!/usr/bin/env python3
"""Tallyturnstone: manual named counters with logged adjustments and undo."""
import argparse,csv,datetime as dt,os,sqlite3,sys
from pathlib import Path
LIMIT=1000000000

def safe(v):return ''.join(c if c.isprintable() else f'\\u{ord(c):04x}' for c in str(v))[:200]
def name(v):
    v=v.strip()
    if not v or len(v)>100 or any(not c.isprintable() for c in v):raise ValueError('Name must be 1-100 printable characters.')
    return v
def connect(path):
    p=Path(path).expanduser();p.parent.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(p);db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
    db.executescript('CREATE TABLE IF NOT EXISTS counters(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL UNIQUE,value INTEGER NOT NULL DEFAULT 0 CHECK(value BETWEEN 0 AND 1000000000));CREATE TABLE IF NOT EXISTS changes(id INTEGER PRIMARY KEY AUTOINCREMENT,counter_id INTEGER NOT NULL REFERENCES counters(id),delta INTEGER NOT NULL,changed_utc TEXT NOT NULL,undone INTEGER NOT NULL DEFAULT 0);');db.commit()
    try:os.chmod(p,0o600)
    except OSError:pass
    return db
def get(db,ident):
    r=db.execute('SELECT * FROM counters WHERE id=?',(ident,)).fetchone()
    if not r:raise ValueError('Unknown counter ID.')
    return r
def create(db,text):
    with db:r=db.execute('INSERT INTO counters(name) VALUES(?)',(name(text),))
    return r.lastrowid
def adjust(db,ident,delta):
    if type(delta) is not int or not -LIMIT<=delta<=LIMIT or delta==0:raise ValueError('Use a nonzero integer adjustment up to 1e9.')
    with db:
        # Conditional SQL enforces bounds even if another process changed the count.
        cur=db.execute('UPDATE counters SET value=value+? WHERE id=? AND value+? BETWEEN 0 AND 1000000000',(delta,ident,delta))
        if cur.rowcount!=1:get(db,ident);raise ValueError('Adjustment would leave range 0..1e9.')
        db.execute('INSERT INTO changes(counter_id,delta,changed_utc) VALUES(?,?,?)',(ident,delta,dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')))
    return get(db,ident)['value']
def undo(db,ident):
    get(db,ident)
    with db:
        last=db.execute('SELECT * FROM changes WHERE counter_id=? AND undone=0 ORDER BY id DESC LIMIT 1',(ident,)).fetchone()
        if not last:return False
        delta=-last['delta'];cur=db.execute('UPDATE counters SET value=value+? WHERE id=? AND value+? BETWEEN 0 AND 1000000000',(delta,ident,delta))
        if cur.rowcount!=1:raise ValueError('Undo would leave allowed range.')
        db.execute('UPDATE changes SET undone=1 WHERE id=?',(last['id'],))
    return True
def show(db):
    rows=db.execute('SELECT * FROM counters ORDER BY id').fetchall();print('\nTALLYTURNSTONE | manual counts')
    if not rows:print('No counters yet.')
    for r in rows:print(r['id'],'|',safe(r['name']),'|',r['value'])
def history(db,ident):get(db,ident);return [dict(r) for r in db.execute('SELECT * FROM changes WHERE counter_id=? ORDER BY id DESC LIMIT 30',(ident,))]
def export(db,path):
    with open(Path(path).expanduser(),'x',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['id','name','value'])
        for r in db.execute('SELECT * FROM counters ORDER BY id'):
            n=r['name'];w.writerow([r['id'],"'"+n if n.lstrip().startswith(('=','+','-','@')) else n,r['value']])
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',default=str(Path.home()/'.local/share/tallyturnstone/counts.sqlite3'));a=p.parse_args(argv);db=None
    try:
        db=connect(a.db)
        while True:
            print('\n1 Counts  2 New counter  3 Adjust  4 Undo latest adjustment  5 History  6 CSV export  0 Exit');c=input('> ').strip()
            if c=='0':return 0
            try:
                if c=='1':show(db)
                elif c=='2':print('Created',create(db,input('Name: ')))
                elif c in ('3','4','5'):
                    ident=int(input('Counter ID: '));r=get(db,ident);print(safe(r['name']),'currently',r['value'])
                    if c=='3':print('New count:',adjust(db,ident,int(input('Signed adjustment: '))))
                    elif c=='4':
                        if input('Undo latest active adjustment? y/N: ').strip().lower()=='y':print('Undone.' if undo(db,ident) else 'No adjustment to undo.')
                    else:
                        for row in history(db,ident):print(row['id'],row['changed_utc'],row['delta'],'undone' if row['undone'] else 'active')
                elif c=='6':export(db,input('New CSV filename: '));print('Exported.')
            except (ValueError,OSError,sqlite3.Error) as exc:print('Error:',safe(exc))
    except (EOFError,KeyboardInterrupt):print('\nBye. Completed changes remain saved.')
    except (ValueError,OSError,sqlite3.Error) as exc:print('Error:',safe(exc),file=sys.stderr);return 2
    finally:
        if db:db.close()
    return 0
if __name__=='__main__':raise SystemExit(main())
