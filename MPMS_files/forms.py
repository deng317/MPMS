from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from MPMS_files import bcrypt
from MPMS_files.models import User, Guest


class RegistrationForm(FlaskForm):
    username = StringField("用户名",
                           validators=[DataRequired(message='请输入字符'), Length(min=6, max=20, message='字符长度请控制在6～20位')])
    email = StringField("邮箱", validators=[DataRequired(message='请输入邮箱'), Email(message='请确认邮箱格式')])
    password = PasswordField("密码", validators=[DataRequired(message='要输入密码才能注册哟～'),
                                               Length(min=6, max=20, message='密码长度请控制在6～20位。')])
    confirm_password = PasswordField("确认密码", validators=[DataRequired(message='要输入密码才能注册哟～'),
                                                         EqualTo('password', message='两次密码输入不一致哟～')])
    group = StringField("公司", validators=[DataRequired(message='选择公司')])
    submit = SubmitField("注册")

    # # 自定义Validater
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("该用户名已经被使用")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("该邮箱已经被注册了")


class UpdateAccountForm(FlaskForm):
    username = StringField("用户名",
                           validators=[DataRequired(message='请输入字符'), Length(min=6, max=20, message='字符长度请控制在6～20位')])
    email = StringField("邮箱", validators=[DataRequired(message='请输入邮箱'), Email(message='请确认邮箱格式')])
    group = StringField("公司", validators=[DataRequired(message='选择公司')])
    submit = SubmitField("更新")
    account_image = FileField("选择头像", validators=[FileAllowed(['jpg', 'jpeg', 'png'], message="确认图片格式")])

    # # 自定义Validater
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("该用户名已经被使用")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("该邮箱已经被注册了")


class LoginForm(FlaskForm):
    email = StringField("用户名", validators=[DataRequired(message="请输入邮箱"), Email(message="邮箱格式不正确")])
    password = PasswordField("密码", validators=[DataRequired(message="请输入密码")])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('无此用户')


class CreateCaseForm(FlaskForm):
    case_name = StringField('专案名称', validators=[DataRequired()])
    address = StringField('交货地点', validators=[DataRequired()])
    start_date = DateField('开案时间', validators=[])
    want_end_date = DateField('预计交期', format='%Y-%m-%d')
    contract_code = StringField('合同编号')
    submit = SubmitField("提交")


class FoundCaseDetailForm(FlaskForm):
    process_section = SelectField("制程段别", validators=[DataRequired()],
                                  choices=["SBK", "CT1", "PA", "CT2", "Bonding", "LCM", "OCA", "其他"])
    EQ_name = StringField("设备名称", validators=[DataRequired(message="输入设备名称")])
    EQ_type = StringField("设备型号", validators=[DataRequired(message="输入设备型号")])
    contract_code = StringField("合同编号", validators=[DataRequired(message="输入合同编号")])
    price = StringField("价格", validators=[DataRequired(message="价格")])
    currency_unit = StringField("币别", validators=[DataRequired(message="币别")])
    quantity = IntegerField("数量(台)", validators=[DataRequired(message="数量")])
    pay_after_contact = StringField("首付款比例", validators=[DataRequired(message="首付款")])
    pay_before_deliver = StringField("发货款比例", validators=[DataRequired(message="发货款")])
    pay_after_setup = StringField("装机完成款比例", validators=[DataRequired(message="装机完成款")])
    pay_after_recieve = StringField("验收款比例", validators=[DataRequired(message="验收款")])
    pay_time_after_recieve = StringField("验收后付款天数(天)", validators=[DataRequired(message="天数")])
    submit = SubmitField("提交")


class FoundGuestForm(FlaskForm):
    guest_name = StringField("客户公司全称", validators=[DataRequired(message="输入客户公司名称")])
    guest_code = StringField("客户代码", validators=[DataRequired(), Length(max=10, min=10, message="请输入10位客户代码")])
    address = StringField("客户地址", validators=[DataRequired()])
    submit = SubmitField("提交")

    def validate_guest_name(self, guest_name):
        user = Guest.query.filter_by(guest_name=guest_name.data).first()
        if user:
            raise ValidationError('客户信息已存在')


class UpdateGuestForm(FlaskForm):
    guest_name = StringField("客户公司全称", validators=[DataRequired(message="输入客户公司名称")])
    guest_code = StringField("客户代码", validators=[DataRequired(), Length(max=10, min=10, message="请输入10位客户代码")])
    address = StringField("客户地址", validators=[DataRequired()])
    submit = SubmitField("更新客户资料")


class CreateGuestContactForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message='联系人姓名')])
    email = StringField('邮箱', validators=[])
    mobile_phone = StringField('手机')
    wechart = StringField('微信号')
    submit = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("密码", validators=[DataRequired(message='请输入原密码')])

    new_password = PasswordField("密码", validators=[DataRequired(message='请输入新密码～'),
                                                   Length(min=6, max=20, message='密码长度请控制在6～20位。')])
    confirm_new_password = PasswordField("确认密码", validators=[DataRequired(message='请再次输入新密码～'),
                                                             EqualTo('new_password', message='两次密码输入不一致哟～')])
    submit = SubmitField("更改密码")

    # # 自定义Validater
    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError("密码错误")

    def validate_new_password(self, new_password):
        if bcrypt.check_password_hash(current_user.password, new_password.data):
            raise ValidationError("与原密码一致")


class QueryCompanyForm(FlaskForm):
    guest_name = StringField("公司名称", validators=[DataRequired(message="输入公司名称")])
    submit_query = SubmitField("查询")


class SubmitForm(FlaskForm):
    submit_vendor = SubmitField("确定")


class VendorForm(FlaskForm):
    name = StringField("公司名称", validators=[DataRequired(message="输入公司名称")])
    vendor_code = StringField("厂商代码", validators=[DataRequired(message="输入厂商代码")])
    address = StringField("厂商地址", validators=[DataRequired(message='厂商地址')])
    submit = SubmitField('提交')

class RequestResetForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('无此用户！！')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("输入密码", validators=[DataRequired(message='请输入密码～'),
                                               Length(min=6, max=20, message='密码长度请控制在6～20位。')])
    confirm_password = PasswordField("确认密码", validators=[DataRequired(message='请输入密码～'),
                                                         EqualTo('password', message='两次密码输入不一致哟～')])
    submit = SubmitField('提交')