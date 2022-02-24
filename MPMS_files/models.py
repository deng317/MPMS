from datetime import datetime

from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from MPMS_files import db, login_manager, app


@login_manager.user_loader
def lode_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    account_image = db.Column(db.String(50), nullable=False, default="default.jpg")
    group = db.Column(db.String(50), nullable=False, default='CH')
    password = db.Column(db.String(100), nullable=False)

    # 与Post类建立Relathonship，通过 backref 指向 Post类中的一个 Column 的名称"author"
    posts = db.relationship('Post', backref="author", lazy=True)
    # 与Case类建立Relationship,通过 backref 指向 Case类中的一个 Column 的名称 "group"
    cases = db.relationship('Case', backref="author", lazy=True)

    # vendors = db.relationship('Vendor',backref='author',lazy=True)
    vendor = db.relationship('VendorAuthor', backref='author', lazy=True)

    def get_set_token(self, expire_time=600):
        s = Serializer(app.config['SECRET_KEY'], expire_time)
        token = s.dumps({'user_id': self.id}).decode('utf-8')
        return token

    @staticmethod
    def verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            return User.query.get(user_id)
        except:
            return None

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.account_image}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=False, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    content = db.Column(db.Text, nullable=False)

    # 与 user 建立关联，使用FortignKey, user.id使用小写字母
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.time}','{self.content}')"


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(30), nullable=False, unique=True)
    guest_code = db.Column(db.String(30), nullable=False, unique=True)
    address = db.Column(db.String(50), nullable=False)

    contacts = db.relationship("GuestContact", backref="company_title", lazy=True)
    cases = db.relationship("Case", backref="company_title", lazy=True)

    def __repr__(self):
        return f"Guset('{self.guest_name}')"


class GuestContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    mobile_phone = db.Column(db.String(20))
    wechart = db.Column(db.String(20))

    guest_id = db.Column(db.Integer, db.ForeignKey("guest.id"), nullable=False)


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    want_end_date = db.Column(db.DateTime)
    contract_code = db.Column(db.String(20))

    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_details = db.relationship("CaseDetail", backref='case_title', lazy=True)

    def __repr__(self):
        return f"Case('{self.case_name}','{self.guest_name}','{self.vendor}')"


class CaseDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_section = db.Column(db.String(10), nullable=False, default="All")
    EQ_name = db.Column(db.String(20), nullable=False)
    EQ_type = db.Column(db.String(20), nullable=False)
    contract_code = db.Column(db.String(20))
    price = db.Column(db.String(20))
    currency_unit = db.Column(db.String(5))
    quantity = db.Column(db.Integer, nullable=False)
    pay_after_contact = db.Column(db.String(5), nullable=False)
    pay_before_deliver = db.Column(db.String(5), nullable=False)
    pay_after_setup = db.Column(db.String(5), nullable=False)
    pay_after_recieve = db.Column(db.String(5), nullable=False)
    pay_time_after_recieve = db.Column(db.String(10), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

    def __repr__(self):
        return f"Case('{self.process_section}','{self.EQ_name}','{self.vendor}')"


class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    vendor_code = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(60), nullable=False)

    cases = db.relationship('CaseDetail', backref='vendor', lazy=True)
    vendorauthor = db.relationship('VendorAuthor', backref='vendor', lazy=True)


class VendorAuthor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
