# app.py (updated)
from flask import Flask, render_template, request, redirect
import json
import os
import glob
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_config():
    with open('config.json') as f:
        return json.load(f)

def init_db():
    config = get_config()
    conn = sqlite3.connect(config['database'])
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS codex_entries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  region TEXT NOT NULL,
                  system TEXT NOT NULL,
                  body_id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  count INTEGER DEFAULT 1,
                  UNIQUE(region, system, body_id, name))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS processed_files
                 (path TEXT PRIMARY KEY, 
                  last_modified REAL NOT NULL)''')
    
    conn.commit()
    conn.close()

def scan_logs(full_rescan=False):
    config = get_config()
    conn = sqlite3.connect(config['database'])
    c = conn.cursor()
    
    if full_rescan:
        c.execute('DELETE FROM codex_entries')
        c.execute('DELETE FROM processed_files')
        conn.commit()

    processed_files = {row[0]: row[1] for row in c.execute('SELECT path, last_modified FROM processed_files')}
    
    log_files = sorted(glob.glob(os.path.join(config['log_path'], 'Journal*.log')),
                       key=os.path.getmtime)
    
    for path in log_files:
        try:
            mtime = os.path.getmtime(path)
            if not full_rescan and path in processed_files and processed_files[path] >= mtime:
                continue
            
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get('event') != 'CodexEntry':
                            continue
                        if entry.get('Category') != '$Codex_Category_Biology;':
                            continue
                            
                        # Validate required fields
                        required_fields = [
                            'Region_Localised', 'System', 
                            'BodyID', 'Name_Localised'
                        ]
                        if not all(entry.get(field) for field in required_fields):
                            continue
                            
                        # Insert/update entry
                        c.execute('''INSERT INTO codex_entries 
                                    (region, system, body_id, name)
                                    VALUES (?, ?, ?, ?)
                                    ON CONFLICT(region, system, body_id, name) 
                                    DO UPDATE SET count = count + 1''',
                                (entry['Region_Localised'], 
                                 entry['System'],
                                 entry['BodyID'],
                                 entry['Name_Localised']))
                                 
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Error processing line in {path}: {e}")
                        continue
                        
            c.execute('''INSERT OR REPLACE INTO processed_files 
                       VALUES (?, ?)''', (path, mtime))
            conn.commit()
            
        except Exception as e:
            print(f"Error processing file {path}: {e}")
            conn.rollback()
    
    conn.close()

# ... rest of the Flask routes remain the same ...

@app.route('/')
def index():
    conn = sqlite3.connect(get_config()['database'])
    c = conn.cursor()
    
    # Group by region > system > body
    hierarchy = {}
    c.execute('''SELECT region, system, body_id, name, SUM(count)
                 FROM codex_entries 
                 GROUP BY region, system, body_id, name
                 ORDER BY region, system, body_id''')
    for row in c.fetchall():
        region, system, body_id, name, count = row
        if region not in hierarchy:
            hierarchy[region] = {}
        if system not in hierarchy[region]:
            hierarchy[region][system] = {}
        if body_id not in hierarchy[region][system]:
            hierarchy[region][system][body_id] = []
        hierarchy[region][system][body_id].append((name, count))
    
    # Get totals
    totals = {}
    c.execute('SELECT name, SUM(count) FROM codex_entries GROUP BY name')
    totals = dict(c.fetchall())
    
    conn.close()
    return render_template('index.html', hierarchy=hierarchy, totals=totals)

@app.route('/scan', methods=['POST'])
def scan():
    scan_logs(full_rescan=False)
    return redirect('/')

@app.route('/rescan', methods=['POST'])
def rescan():
    scan_logs(full_rescan=True)
    return redirect('/')

#if __name__ == '__main__':
#    init_db()
#    app.run(debug=True, host='0.0.0.0')

# -----

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
