from flask import  Blueprint,views,render_template,request,session,redirect,url_for,g,jsonify
from  .forms import LoginForm,ResetpwdForm
from .models import CMSUser
from .decorators import login_required
import config
from exts import db
from utils import restful

bp = Blueprint("cms",__name__,url_prefix='/cms')

@bp.route('/logout/')
@login_required
def logout():
    del session[config.CMS_USER_ID]
    return redirect(url_for('cms.login'))


@bp.route('/profile/')
@login_required
def profile():
    return render_template('cms/cms_profile.html')


@bp.route('/')
@login_required
def index():
    return render_template('cms/cms_index.html')
# render_template('cms/cms_index.html')




"""
登录界面
"""


class LoginView(views.MethodView):
    def get(self,message=None):
        return render_template('cms/cms_login.html',message=message )

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = CMSUser.query.filter_by(email = email).first()
            if user and user.check_password(password):
                session[config.CMS_USER_ID]=user.id
                """
            #session是存储了user_id,同时这个session又保存在cookies当中,当用户再次请求的时候会把cookies提交给服务器
                这时候falsk就会把cookies中的session拿到,而后把相应的数据解码出来
                
                """
                if remember:#如果用户有提交这个remember,那么就让这个cookies信息保存的长一点
                    #如果session.permanent = True
                    #则过期时间31天
                    session.permanent = True
                return redirect(url_for('cms.index'))
            else:
                return self.get(message="邮箱或者密码错误")

        else:
            # print(form.errors)
            # message = form.errors.popitem()[1][0]
            message = form.get_error()
            # print(message)
            # 请输入正确格式的密码

            """
            form.errors.popitem()[1]是一个列表:
         {'password': ['请输入正确格式的密码']}
         里面的第0项为:请输入正确格式的密码

            """

            return self.get(message=message)


class ResetPwdView(views.MethodView):
    decorators=[login_required]
    def get(self):
        return render_template('cms/cms_resetpwd.html')

    def post(self):
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()
                # return jsonify({"code": 200, "message": ""})
                return restful.success()
            else:
                # print("post里层循环400")
                return restful.params_error("旧密码错误")
        else:
            message = form.get_error()
            # print("post外层循环400")
            return restful.params_error(form.get_error())


class ResetEmailView(views.MethodView):
    decorators = [login_required]
    def get(self):
        return render_template('cms/cms_resetemail.html')
    def post(self):
        pass

bp.add_url_rule('/login/',view_func=LoginView.as_view('login'))
##一定要和base.js里面的重置密码url保持一致;这里是和第31行一样
bp.add_url_rule('/resetpwd/',view_func=ResetPwdView.as_view('resetpwd'))
##一定要和base.js里面的重置邮箱url保持一致;这里是和第35行一样
bp.add_url_rule('/resetemail/',view_func=ResetEmailView.as_view('resetemail'))



