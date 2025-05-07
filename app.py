from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3, datetime

app = Flask(__name__)
DB_PATH = 'data.db'

# --- Database helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        alpha REAL, beta REAL, gamma REAL,
        N REAL, S REAL,
        t_star TEXT, t TEXT,
        vessel_type TEXT, dwt REAL,
        t_q TEXT, t_on TEXT, t_qp TEXT,
        TC_e REAL, tau_core REAL, billed REAL
    )''')
    db.commit()

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, '_database', None)
    if db:
        db.close()

# --- Time helpers ---
def parse_time(s):
    h, m = map(int, s.split(':'))
    return h + m/60.0

def format_time(x):
    h = int(x)
    m = int(round((x-h)*60))
    return f"{h:02d}:{m:02d}"

# Vessel multipliers
TYPE_MULT = {
    'Container': 1.00,
    'Bulk':      1.05,
    'Tanker':    1.10,
    'LNG':       1.20,
}

@app.route('/', methods=['GET','POST'])
def index():
    result = {}
    if request.method=='POST':
        # read inputs
        alpha = float(request.form['alpha'])
        beta  = float(request.form['beta'])
        gamma = float(request.form['gamma'])
        N     = float(request.form['N'])
        S     = float(request.form['S'])
        t_star_str = request.form['t_star']
        t_str      = request.form['t']
        vessel_type = request.form['vessel_type']
        dwt         = float(request.form['dwt'])

        # parse times
        t_star = parse_time(t_star_str)
        t      = parse_time(t_str)

        # precompute
        t_q  = t_star - (gamma/(beta+gamma))*(N/S)
        t_on = t_star - (beta*gamma/(alpha*(beta+gamma)))*(N/S)
        t_qp = t_star + (beta/(beta+gamma))*(N/S)
        TC_e = (beta*gamma/(beta+gamma))*(N/S)

        # core toll
        if t < t_q or t > t_qp:
            tau_core = None
        elif t < t_star:
            tau_core = TC_e - beta*(t_star - t)
        elif t == t_star:
            tau_core = TC_e
        else:
            tau_core = TC_e - gamma*(t - t_star)

        # billed toll
        if tau_core is not None:
            type_mult   = TYPE_MULT.get(vessel_type,1.0)
            billed_toll = tau_core * type_mult * (dwt/1000.0)
        else:
            billed_toll = None

        # format results
        result = {
            't_q':       format_time(t_q),
            't_on':      format_time(t_on),
            't_qp':      format_time(t_qp),
            'TC_e':      round(TC_e,4),
            'tau_core':  None if tau_core is None else round(tau_core,4),
            'billed':    None if billed_toll is None else round(billed_toll,4),
            'vessel_type': vessel_type,
            'dwt':         dwt
        }

        # save to history
        db = get_db()
        db.execute('''INSERT INTO history (
            timestamp, alpha,beta,gamma,N,S,t_star,t,
            vessel_type,dwt,t_q,t_on,t_qp,TC_e,tau_core,billed
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            datetime.datetime.utcnow().isoformat(),
            alpha,beta,gamma,N,S,t_star_str,t_str,
            vessel_type,dwt,
            result['t_q'], result['t_on'], result['t_qp'],
            result['TC_e'], result['tau_core'], result['billed']
        ))
        db.commit()

    return render_template('index.html', result=result, types=TYPE_MULT.keys())

@app.route('/history')
def history():
    db = get_db()
    rows = db.execute('SELECT * FROM history ORDER BY id DESC').fetchall()
    return render_template('history.html', rows=rows)

if __name__=='__main__':
    # Initialize the database before first request handling
    with app.app_context():
        init_db()
    app.run(debug=True)
