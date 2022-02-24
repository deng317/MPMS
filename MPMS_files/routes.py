import os
import secrets

from PIL import Image
from flask import render_template, redirect, flash, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from MPMS_files import app, bcrypt, db, mail
from MPMS_files.forms import RegistrationForm, LoginForm, UpdateAccountForm, ChangePasswordForm, FoundGuestForm, \
    QueryCompanyForm, CreateGuestContactForm, CreateCaseForm, UpdateGuestForm, VendorForm, FoundCaseDetailForm, \
    RequestResetForm, ResetPasswordForm
from MPMS_files.models import User, Guest, GuestContact, Case, Vendor, CaseDetail


def random_prefix():
    random_hex = secrets.token_hex(8)
    return random_hex


def random_suffix():
    random_hex = secrets.token_hex(6)
    return random_hex


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    cases = Case.query.order_by(Case.start_date.asc()).paginate(per_page=10)
    return render_template("main.html", cases=cases)


@app.route('/casedetail<case_id>')
@login_required
def casedetail(case_id):
    case = Case.query.get_or_404(case_id)
    page = request.args.get('page', 1, type=int)
    case_details = CaseDetail.query.filter_by(case_id=case_id).paginate(per_page=10)
    return render_template("casedetail.html", title=f"专案{case.case_name}明细", **locals())


@app.route('/case/add_casedetail<int:case_id><vendor_id>', methods=['GET', 'POST'])
@login_required
def add_casedetail(case_id, vendor_id):
    form = FoundCaseDetailForm()
    case = Case.query.get_or_404(case_id)
    vendor = Vendor.query.get_or_404(vendor_id)
    if form.validate_on_submit():
        process_section = form.process_section.data
        EQ_name = form.EQ_name.data
        EQ_type = form.EQ_type.data
        contract_code = form.contract_code.data
        price = form.price.data
        currency_unit = form.currency_unit.data
        quantity = form.quantity.data
        pay_after_contact = form.pay_after_contact.data
        pay_before_deliver = form.pay_before_deliver.data
        pay_after_setup = form.pay_after_setup.data
        pay_after_recieve = form.pay_after_recieve.data
        pay_time_after_recieve = form.pay_time_after_recieve.data

        user_id = current_user.id
        case_id = case.id
        vendor_id = vendor.id

        casedetail = CaseDetail(process_section=process_section, EQ_name=EQ_name, EQ_type=EQ_type,
                                contract_code=contract_code, price=price, currency_unit=currency_unit,
                                quantity=int(quantity), pay_after_contact=pay_after_contact,
                                pay_before_deliver=pay_before_deliver, pay_after_setup=pay_after_setup,
                                pay_after_recieve=pay_after_recieve, pay_time_after_recieve=pay_time_after_recieve,
                                user_id=user_id, case_id=case_id, vendor_id=vendor_id)

        db.session.add(casedetail)
        db.session.commit()
        flash("明细添加成功", "success")
        return redirect(url_for("casedetail", case_id=case_id))
    return render_template("add_casedetail.html", vendor=vendor, form=form, case=case, title="添加专案明细")


@app.route("/casedetail/delete<case_id><case_detail_id>")
@login_required
def delete_case_detail(case_id, case_detail_id):
    detail = CaseDetail.query.get_or_404(case_detail_id)
    if detail.author != current_user:
        abort(403)
    db.session.delete(detail)
    db.session.commit()
    flash(f"专案项目{detail.EQ_name}删除成功", "success")
    return redirect(url_for("casedetail", case_id=case_id))


@app.route("/case/add_casedetail<int:case_id>_queryvendor", methods=["post", "get"])
@login_required
def query_vendor(case_id):
    form_query_vendor = QueryCompanyForm()
    case = Case.query.get_or_404(case_id)
    if form_query_vendor.validate_on_submit():
        vendors = Vendor.query.filter(Vendor.name.like(f"%{form_query_vendor.guest_name.data}%"))
        if vendors:
            flash("查询到供应商信息", "success")
            return render_template("add_casedetail_query_vendor.html", case=case, vendors=vendors,
                                   form_query_vendor=form_query_vendor)
        else:
            vendors = ""
    return render_template("add_casedetail_query_vendor.html", case=case,
                           form_query_vendor=form_query_vendor)


@app.route('/vendor')
@login_required
def vendor():
    page = request.args.get('page', 1, type=int)
    vendors = Vendor.query.paginate(per_page=10)
    return render_template('vendor.html', title='供应商列表', vendors=vendors)


def create_vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(name=form.name.data, vendor_code=form.vendor_code.data, address=form.address.data)
        db.session.add(vendor)
        db.session.commit()
        flash("供应商信息创建成功", "success")
        return redirect(url_for("vendor"))
    return render_template("create_vendor.html", legend_tag="创建供应商档案", title="创建供应商档案", form=form)


def delete_vendor(vendor_id):
    vendor = Vendor.query.get_or_404(vendor_id)
    if not vendor.cases:
        db.session.delete(vendor)
        db.session.commit()
        flash(f"供应商{vendor.name}删除成功", "success")
    else:
        flash(f"供应商{vendor.name}有关联信息", "danger")
    return redirect(url_for("vendor"))


app.add_url_rule(rule="/vendor/create_vendor", endpoint="create_vendor", view_func=create_vendor,
                 methods=["get", "post"])
app.add_url_rule(rule="/delete_vendor<vendor_id>", endpoint="delete_vendor", view_func=delete_vendor,
                 methods=['get', 'post'])


@app.route('/vendor/updatevendor<vendor_id>', methods=['GET', 'POST'])
@login_required
def update_vendor(vendor_id):
    form = VendorForm()
    vendor = Vendor.query.get_or_404(vendor_id)
    if form.validate_on_submit():
        vendor.name = form.name.data
        vendor.vendor_code = form.vendor_code.data
        vendor.address = form.address.data
        db.session.commit()
        flash("供应商信息更新成功", "success")
        return redirect(url_for("vendor"))
    elif request.method == "GET":
        form.name.data = vendor.name
        form.vendor_code.data = vendor.vendor_code
        form.address.data = vendor.address
    return render_template("create_vendor.html", legend_tag="更新供应商档案", title="更新供应商档案", form=form)


@app.route('/query_guest/', methods=['post', 'get'])
@login_required
def query_guest():
    form1 = QueryCompanyForm()
    if form1.validate_on_submit():
        guest = Guest.query.filter(Guest.guest_name.like(f"%{form1.guest_name.data}%")).first()
        if guest:
            return render_template('query_guest.html', guest=guest, form1=form1)
    else:
        guest = ''
        return render_template('query_guest.html', guest=guest, form1=form1)


@app.route('/create_case<guest_id>', methods=['POST', 'GET'])
@login_required
def create_case(guest_id):
    form = CreateCaseForm()
    guest = Guest.query.get(guest_id)
    if form.validate_on_submit():
        case = Case(case_name=form.case_name.data, address=form.address.data, start_date=form.start_date.data,
                    want_end_date=form.want_end_date.data, contract_code=form.contract_code.data,
                    user_id=current_user.id, guest_id=guest_id)
        db.session.add(case)
        db.session.commit()
        flash('专案创建成功', 'success')
        return redirect(url_for('index'))
    return render_template('create_case.html', form=form, title='创建新专案', guest=guest)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(group=form.group.data, username=form.username.data, email=form.email.data, password=hashed_passwd,
                    account_image="default.jpg")
        db.create_all()
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="注册页面", form=form)


@app.route('/login', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'【{form.email.data}】登录成功！', 'success')
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
        else:
            flash("账号或密码错误", "danger")
    return render_template('login.html', title='登录页面', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/account")
@login_required
def account():
    image_file = url_for('static', filename=os.path.join('account_pics', current_user.account_image))
    return render_template("account.html", title="我的个人页面", image_file=image_file)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extention = os.path.splitext(form_picture.filename)
    picture_name = random_hex + file_extention
    picture_path = os.path.join(app.root_path, 'static', 'account_pics', picture_name)
    thumbnail_image_size = (100, 100)
    thumbnail_picture = Image.open(form_picture)
    thumbnail_picture.thumbnail(thumbnail_image_size)
    thumbnail_picture.save(picture_path)

    picture_path1 = os.path.join(app.root_path, 'static', 'upload_pic', picture_name)
    out_image_size = (500, 500)
    upload_picture = Image.open(form_picture)
    upload_picture.thumbnail(out_image_size)
    upload_picture.save(picture_path1)
    return picture_name


@app.route("/account/update_account", methods=["POST", "GET"])
@login_required
def update_account():
    form = UpdateAccountForm()
    image_file = url_for("static", filename=os.path.join("account_pics", current_user.account_image))
    if request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.group.data = current_user.group
        # form.account_image.data = current_user.account_image
    elif form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.group = form.group.data
        if form.account_image.data:
            current_user.account_image = save_picture(form.account_image.data)
        db.session.commit()
        flash("账户信息更新成功", "success")
        return redirect(url_for("account"))
    return render_template("update_account.html", title="更新用户信息", form=form, image_file=image_file)


@app.route("/account/change_password", methods=["POST", "GET"])
@login_required
def change_password():
    form = ChangePasswordForm()
    image_file = url_for("static", filename=os.path.join("account_pics", current_user.account_image))
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode("utf-8")
            db.session.commit()
            flash("密码更改成功", "success")
            return redirect(url_for("account"))
    return render_template("change_password.html", title="更改密码", form=form, image_file=image_file)


@app.route("/guest/create_guest", methods=["POST", "GET"])
@login_required
def create_guest():
    form = FoundGuestForm()
    if form.validate_on_submit():
        guest_name = form.guest_name.data
        guest_code = form.guest_code.data
        address = form.address.data
        guest = Guest(guest_name=guest_name, guest_code=guest_code, address=address)
        db.session.add(guest)
        db.session.commit()
        flash("客户信息创建成功", "success")
        return redirect(url_for('guest'))
    return render_template("create_guest.html", form=form, title="创建客户信息")


@app.route("/guest/unpdate_guest<guest_id>", methods=["POST", "GET"])
@login_required
def update_guest(guest_id):
    form = UpdateGuestForm()
    guest = Guest.query.get(guest_id)
    if form.validate_on_submit():
        guest.guest_name = form.guest_name.data
        guest.guest_code = form.guest_code.data
        guest.address = form.address.data
        db.session.commit()
        flash("客户信息更新成功", "success")
        return redirect(url_for('guest'))
    elif request.method == "GET":
        form.guest_name.data = guest.guest_name
        form.guest_code.data = guest.guest_code
        form.address.data = guest.address
    return render_template("update_guest.html", form=form, title="更新客户信息")


@app.route("/guest/add_contact<guest_id>", methods=['GET', 'POST'])
@login_required
def add_guest_contact(guest_id):
    form = CreateGuestContactForm()
    guest = Guest.query.get(guest_id)
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        mobile_phone = form.mobile_phone.data
        wechart = form.wechart.data
        guest_id = guest_id
        guest = GuestContact(name=name, email=email, mobile_phone=mobile_phone, wechart=wechart, guest_id=guest_id)
        db.session.add(guest)
        db.session.commit()
        return redirect(url_for('guest'))
    return render_template('add_contact.html', form=form, title="添加客户联系人", guest_id=guest_id, guest=guest)


@app.route(f"/guest/update_contact-{random_prefix()}<contact_id>{random_suffix()}", methods=['GET', 'POST'])
@login_required
def update_guest_contact(contact_id):
    form = CreateGuestContactForm()
    contact = GuestContact.query.get(contact_id)
    if form.validate_on_submit():
        contact.name = form.name.data
        contact.email = form.email.data
        contact.mobile_phone = form.mobile_phone.data
        contact.wechart = form.wechart.data
        db.session.commit()
        return redirect(url_for('guest'))
    elif request.method == "GET":
        form.name.data = contact.name
        form.email.data = contact.email
        form.mobile_phone.data = contact.mobile_phone
        form.wechart.data = contact.wechart
    return render_template('update_guest_contact.html', form=form, title="更新客户联系人信息", contact=contact)


@app.route("/guest/detail<guest_id>", methods=['post', 'get'])
@login_required
def guest_detail(guest_id):
    guest = Guest.query.get(guest_id)
    return render_template('guest_detail.html', title='客户档案', guest=guest)


@app.route("/guest", methods=["POST", "GET"])
@login_required
def guest():
    form = QueryCompanyForm()
    per_page = 10
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        guests = Guest.query.filter(Guest.guest_name.like(f"%{form.guest_name.data}%")).paginate(per_page=per_page)
        if guests.items:
            flash(f'查询到客户{form.guest_name.data}', 'success')
        else:
            flash(f'未查询到客户{form.guest_name.data}', 'danger')
        return render_template("guest.html", guests=guests, title="客户列表", form=form, page=1)
    else:
        page = request.args.get('page', 1, type=int)
        guests = Guest.query.paginate(per_page=per_page)
        return render_template("guest.html", guests=guests, title="客户列表", form=form)




@app.route('/requestreset', methods=['post', 'get'])
def request_reset():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = User.get_set_token(user)
        msg = Message(subject='重置信息的邮件', recipients=[user.email],
                      sender='happylearn2021@163.com',
                      body=f'''点击如下链接进行信息重置
                        {url_for('reset_password', token=token,_external=True)}
                        ''')
        mail.send(msg)
        return redirect(url_for('index'))
    return render_template('requestreset.html', form=form)


@app.route('/reset_password_token=<token>', methods=['post', 'get'])
def reset_password(token):
    user = User.verify_token(token)
    form = ResetPasswordForm()
    if user is None:
        return render_template("expire_page.html")
    if form.validate_on_submit():
        user = User.verify_token(token)
        if user is None:
            return render_template("expire_page.html")
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('index'))
    return render_template('reset_password.html', form=form, title='重置密码')
