from flask import Flask, request, render_template, session, abort, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import yaml
import datetime, time
import string, json
import bcrypt
import sys
import os
import random
from captcha.image import ImageCaptcha

icgen = ImageCaptcha(fonts=[os.path.join('fonts', fn) for fn in os.listdir('fonts') if fn.endswith('.ttf')])

cfg = yaml.load(open('cfg.yaml', 'r'))

r_fields = [
	dict(dispname="Full Name:", intname="name", type="text", required=True),
	dict(dispname="Email Address:", intname="email", type="email", required=True),
	dict(dispname="Mobile Phone Number:", intname="mobile", type="text", length=16),
	dict(dispname="Any allergies or specific dietary requirements?", intname="allergies", type="text", length=256),
	dict(dispname="Any medication it would be useful for us to know about?", intname="medication", type="text", length=256),
	dict(dispname="Any illnesses, injuries or conditions that it would be useful for us to know about?", intname="conditions", type="text", length=256),
	dict(dispname="A website, blog, etc?", intname="website", type="text"),
	dict(dispname="Partial date of birth (Month/Year):", intname="dob", type="text", pad=True, length=16),
	dict(dispname="Any disabilities?", intname="disabilities", type="text"),
	dict(dispname="Place of Residence Postcode:", intname="postcode", type="text", length=16),
	dict(dispname="Gender:", intname="gender", type="text"),
	dict(dispname="Ethnicity:", intname="ethnicity", type="text"),
	dict(dispname="Religion:", intname="religion", type="text"),
	dict(dispname="Emergency Contact 1:", intname="ignore_ec1", type="hidden", pad=True),
	dict(dispname="Name:", intname="emergency_contact_1_name", type="text", required=True, indent=True),
	dict(dispname="Relation to Member:", intname="emergency_contact_1_relation", type="text", required=True, indent=True),
	dict(dispname="Phone Number:", intname="emergency_contact_1_phone", type="text", required=True, indent=True, length=16),
	dict(dispname="Email:", intname="emergency_contact_1_email", type="email", required=True, indent=True),
	dict(dispname="Emergency Contact 2:", intname="ignore_ec2", type="hidden", pad=True),
	dict(dispname="Name:", intname="emergency_contact_2_name", type="text", required=True, indent=True),
	dict(dispname="Relation to Member:", intname="emergency_contact_2_relation", type="text", required=True, indent=True),
	dict(dispname="Phone Number:", intname="emergency_contact_2_phone", type="text", required=True, indent=True, length=16),
	dict(dispname="Email:", intname="emergency_contact_2_email", type="email", required=True, indent=True)
]

def next_weekday(d, weekday):
	days_ahead = weekday - d.weekday()
	if days_ahead < 0:
		days_ahead += 7
	return d + datetime.timedelta(days_ahead)

def get_next_pw_dt():
	return next_weekday(datetime.date.today(), 2)

def get_next_pw():
	return '{0.day}/{0.month}/{0.year}'.format(get_next_pw_dt())

def NameCase(name):
	name = u' ' + name.lower()
	for i in xrange(26):
		name = name.replace(u' ' + string.ascii_lowercase[i], u' ' + string.ascii_uppercase[i])
	name = name.replace(u'<', unichr(9001)).replace(u'>', unichr(9002)).replace(u'&', unichr(65286))
	return u' '.join(name.split())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = cfg['database_URI']
app.config['SECRET_KEY'] = cfg['secret_key']
db = SQLAlchemy(app)


class Member(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
	name = db.Column(db.String(80))
	email = db.Column(db.String(80))
	mobile = db.Column(db.String(16))
	allergies = db.Column(db.String(256))
	medication = db.Column(db.String(256))
	conditions = db.Column(db.String(256))
	website = db.Column(db.String(80))
	dob = db.Column(db.String(16))
	disabilities = db.Column(db.String(80))
	postcode = db.Column(db.String(16))
	gender = db.Column(db.String(80))
	ethnicity = db.Column(db.String(80))
	religion = db.Column(db.String(80))
	emergency_contact_1_name = db.Column(db.String(80))
	emergency_contact_1_relation = db.Column(db.String(80))
	emergency_contact_1_phone = db.Column(db.String(16))
	emergency_contact_1_email = db.Column(db.String(80))
	emergency_contact_2_name = db.Column(db.String(80))
	emergency_contact_2_relation = db.Column(db.String(80))
	emergency_contact_2_phone = db.Column(db.String(16))
	emergency_contact_2_email = db.Column(db.String(80))

	photo = db.Column(db.Boolean)
	by_parent = db.Column(db.Boolean)
	registered = db.Column(db.Integer)
	__tablename__ = 'Member'
	
	def __init__(self, form):
		self.registered = int(time.time())
		self.photo = form.get('photo') == 'yes'
		self.by_parent = form.get('registered_by') == 'parent'
		for f in r_fields:
			if 'name' in f['intname']:
				self.__dict__[f['intname']] = NameCase(form.get(f['intname']))
			elif not f['intname'].startswith('ignore'):
				self.__dict__[f['intname']] = form.get(f['intname'])
	
	def htmltable(self):
		it = ''
		for f in self.__dict__:
			if not f[0] == '_':
				it += '<tr><td>%s</td><td>%s</td></tr>' % (f.replace('_', ' '), self.__dict__[f])
		return '<table><tbody>%s</tbody></table>' % it



class PWSession(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
	date = db.Column(db.String(10))
	__tablename__ = 'PWSession'
	
	def __init__(self, date):
		self.date = date

NOT_YET_ARRIVED = 0
HERE = 1
LEFT = 2

class GoingTo(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
	usr_id = db.Column(db.Integer)
	pws_id = db.Column(db.Integer)
	state = db.Column(db.Integer)
	__tablename__ = 'GoingTo'
	
	def __init__(self, usr, pws):
		self.usr_id = usr
		self.pws_id = pws
		self.state = NOT_YET_ARRIVED

class LoggedEvent(db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
	timestamp = db.Column(db.Integer)
	html = db.Column(db.String(1024))
	__tablename__ = 'LoggedEvent'
	
	def __init__(self, msg):
		self.timestamp = int(time.time())
		self.html = msg
	
	def json(self):
		return json.dumps({"timestamp":self.timestamp, "html":self.html})

class Captcha(db.Model):
	id = db.Column(db.String(16), unique=True, primary_key=True)
	nbr = db.Column(db.Integer)
	timestamp = db.Column(db.Integer)
	__tablename__ = 'Captcha'

	def __init__(self, cid, nbr):
		self.id = cid
		self.nbr = nbr
		self.timestamp = int(time.time())


def log(msg):
	evt = LoggedEvent(msg)
	db.session.add(evt)
	db.session.commit()
	return evt

def register_captcha(cid, nbr):
	cobj = Captcha(cid, nbr)
	db.session.add(cobj)
	db.session.commit()

def check_captcha(cid, nbr):
	cobj = Captcha.query.filter_by(id=cid).first()
	if not cobj:
		return False
	
	correct = str(nbr) == str(cobj.nbr)

	db.session.delete(cobj)
	db.session.commit()

	return correct

def wipe_old_captchas():
	earliest_allowed = time.time() - 700000

	flag = False
	for cobj in Captcha.query.all():
		if cobj.timestamp < earliest_allowed:
			db.session.delete(cobj)
			flag = True
	
	if flag:
		db.session.commit()

def newMember(f):
	m = Member(f)
	db.session.add(m)
	db.session.commit()
	return m

def get_pws(date):
	s = PWSession.query.filter_by(date=date).first()
	if not s:
		s = PWSession(date)
		db.session.add(s)
		db.session.commit()
	return s

def getMembers(*a, **k):
	if a:
		d = a[0]
	else:
		d = k
	return Member.query.filter_by(**d).all() if d else Member.query.all()

@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = datetime.timedelta(days=1337)

@app.route('/')
def index(error=''):
	
	if (get_next_pw_dt() == datetime.date.today()
	  and datetime.datetime.now().time() > datetime.time(cfg['sign_up_end']['hour'], cfg['sign_up_end']['minute'], 0, 0)):
		return render_template('late.html')
	
	
	number = random.randint(1000, 9999)
	captcha = icgen.generate(str(number))
	binary = captcha.read()
	b64 = binary.encode('base64').replace('\n', '')

	rstr = str(random.randint(0,2000000000))
	register_captcha(rstr, number)

	return render_template('index.html', date=get_next_pw(), error=error, captcha=b64, rstr=rstr)

def yeeeeeha_int():
	if 'name' not in request.args or not request.args['name']:
		return 'Please enter your name.'
	name = NameCase(request.args['name'])
	m = getMembers(name=name)
	if not m:
		return 'Sorry, but you don\'t appear to be a registered member. Check for\
			typos in your name, or <a href="register">register</a> if you haven\'t already.'
	
	if not check_captcha(request.args['captcha'], request.args.get(request.args['captcha']).strip()):
		return 'Please check you have filled out the CAPTCHA below correctly.'

	pws_id = get_pws(get_next_pw()).id
	
	if GoingTo.query.filter_by(usr_id=m[0].id, pws_id=pws_id).first():
		log('<member>%s</member> attempted to register for Prewired on <session>%s</session>, but was already going.' % (m[0].name, get_next_pw()))
	else:
		
		if len(GoingTo.query.filter_by(pws_id=pws_id).all()) == cfg['capacity']:
			log('<member>%s</member> attempted to register for Prewired on <session>%s</session>, but it was full' % (m[0].name,get_next_pw()))
			return 'Sorry, but Prewired has already been fully booked for this week.'

		gt = GoingTo(m[0].id, pws_id)
		db.session.add(gt)
		
		db.session.commit()
		
		log('<member>%s</member> is going to Prewired on <session>%s</session>.' % (m[0].name, get_next_pw()))
	return m[0]

@app.route('/yeeeeeha')
def yeeeeeha():
	e = yeeeeeha_int()
	if isinstance(e, basestring):
		if e == 'Sorry, but Prewired has already been fully booked for this week.':
			return render_template('full.html')

		return index(e)

	session['name'] = e.name
	return render_template('yeeeeeha.html')

@app.route('/yeeeeeha.json')
def yeeeeeha_json():
	e = yeeeeeha_int()
	if isinstance(e, basestring): return json.dumps({"status":"fail","err":e})
	return '{"status":"success"}'

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html', fields=r_fields)
	else:
		for f in r_fields:
			if f.get('required') and not request.form.get(f['intname']):
				return render_template('register.html', fields=r_fields, err=True)
				
		if getMembers(name=NameCase(request.form.get('name'))):
			return render_template('eviltwin.html')
		else:
			m = newMember(request.form)
			log('Member <member>%s</member> registered.' % m.name)
		return render_template('registered.html', name=m.name)

@app.route('/favicon.ico')
def favicon():
	return redirect(url_for('static', filename='favicon.ico'))

def req_admin():
	if session.get('admin') != 'y':
		abort(403)

@app.errorhandler(403)
def login(e):
	return render_template('login.html'), 403

@app.route('/gimme', methods=['POST'])
def gimme():
	if bcrypt.hashpw(request.get_data(), cfg['admin_password_bcrypt']) == cfg['admin_password_bcrypt']:
		session['admin'] = 'y'
		return 'y'
	return 'n'

@app.route('/admin/')
def admin():
	req_admin()
	return render_template('admin.html')

@app.route('/admin/out')
def admin_out():
	session['admin'] = 'n'
	return '<h2>You are no longer an admin</h2>'

@app.route('/admin/log/feed')
def log_feed():
	req_admin()
	return u'[%s]' % u','.join([e.json() for e in LoggedEvent.query.all()])

@app.route('/admin/log/clear')
def log_clear():
	req_admin()
	for e in LoggedEvent.query.all():
		db.session.delete(e)
	db.session.commit()
	return '1'
		
@app.route('/admin/session/list')
def list_sessions():
	req_admin()
	return json.dumps([{"date": s.date, "id": s.id} for s in PWSession.query.all()])

@app.route('/admin/session/went')
def went_to():
	req_admin()
	gtos = GoingTo.query.filter_by(pws_id=get_pws(request.args['s']).id).all()
	ppl = [getMembers({'id': i.usr_id})[0] for i in gtos]
	return json.dumps([p.name for p in ppl])

@app.route('/admin/member/list')
def list_members():
	req_admin()
	return json.dumps([m.name for m in getMembers()])

@app.route('/admin/member/about')
def who_is():
	req_admin()
	m = getMembers(name=request.args['m'])[0]
	return json.dumps(
		[
			[
				(unichr(160)*4 if f.get('indent') else '') + f['dispname'],
				'' if f['intname'].startswith('ignore') else m.__dict__[f['intname']]
			] for f in r_fields
		] + [
			['Consents to photos', str(m.photo)],
			['Registered by a parent or guardian', str(m.by_parent)]
		]
	)

@app.route('/entrance/')
def entrance():
	req_admin()
	wipe_old_captchas() 
	return render_template('entrance.html')

@app.route('/entrance/stream', methods=['POST'])
def stream():
	req_admin()
	
	sid = get_pws(get_next_pw()).id
	
	dirty = False

	for evt in request.get_json(force=True):
		dirty = True

		if evt['type'] == 'tap':
			mid = getMembers(name=evt['target'])[0].id
			gto = GoingTo.query.filter_by(usr_id=mid, pws_id=sid).first()
			gto.state = (1 + gto.state) % 3
	
	if dirty:
		db.session.commit()
	
	data = []
	for m in GoingTo.query.filter_by(pws_id=sid).all():
		data.append({
			'name': getMembers({'id':m.usr_id})[0].name,
			'state': m.state
		})
	
	return Response(json.dumps(data), mimetype='application/json')

@app.route('/errah')
def errah():
	return 0/0

if 'create-all' in sys.argv:
	db.create_all()
elif 'dev-server' in sys.argv:
	app.run('0.0.0.0', debug=True)
