import remi.gui as gui
from remi import start, App
from util import camera
from util import public_tools as tool
from service import hr_service as hr
import pyodbc
import datetime

ADMIN_LOGIN = True
current_admin = None


class ClockInSystem(App):
    def __init__(self, *args):
        super(ClockInSystem, self).__init__(*args)
        hr.load_emp_data()  # 数据初始化

    def main(self):
        self.title = "智能视频打卡系统"

        # 主容器
        container = gui.VBox(width=300, height='100%')
        container.style['align-items'] = 'center'
        self.main_container = container

        # 标题
        title = gui.Label("智能视频打卡系统", width='100%', height=15)
        title.style['font-size'] = '20px'
        title.style['font-weight'] = 'bold'
        title.style['text-align'] = 'center'
        title.style['margin'] = '10px 0'
        container.append(title)

        self.login_status = gui.Label("", width='100%', height=10)
        self.login_status.style.update({
            'font-size': '12px',
            'text-align': 'center',
            'margin': '5px 0'
        })
        container.append(self.login_status)
        self.update_login_status()

        # 按钮容器
        self.btn_container = gui.VBox(width='80%', height='auto')
        self.btn_container.style['align-items'] = 'center'
        self.btn_container.style['margin'] = '10px 0'
        container.append(self.btn_container)

        # 初始化按钮（稍后根据权限更新）
        self.update_buttons()

        # 结果显示区域
        self.result_label = gui.Label("", width='80%', height=100)
        self.result_label.style['margin'] = '10px'
        self.result_label.style['padding'] = '5px'
        self.result_label.style['border'] = '1px solid #ccc'
        self.result_label.style['overflow'] = 'auto'
        self.result_label.style['white-space'] = 'pre-line'
        container.append(self.result_label)

        # 存储当前对话框
        self.current_dialog = None

        return container

    def update_login_status(self):
        """更新登录状态标签"""
        if ADMIN_LOGIN:
            self.login_status.set_text("已登录")
            self.login_status.style['color'] = 'green'
        else:
            self.login_status.set_text("未登录")
            self.login_status.style['color'] = 'red'

    def update_buttons(self):
        """根据登录状态更新按钮显示"""
        # 清空当前按钮
        self.btn_container.empty()

        # 总是显示的按钮
        self.btn_clock = gui.Button("打卡", width='100%', height=30)
        self.btn_clock.style['margin'] = '5px 0'
        self.btn_clock.onclick.do(self.on_clock_in)
        self.btn_container.append(self.btn_clock)

        self.btn_records = gui.Button("查看记录", width='100%', height=30)
        self.btn_records.style['margin'] = '5px 0'
        self.btn_records.onclick.do(self.on_check_records)
        self.btn_container.append(self.btn_records)

        self.btn_employee = gui.Button("员工管理", width='100%', height=30)
        self.btn_employee.style['margin'] = '5px 0'
        self.btn_employee.onclick.do(self.on_employee_management)
        self.btn_container.append(self.btn_employee)

        self.btn_report = gui.Button("考勤报表", width='100%', height=30)
        self.btn_report.style['margin'] = '5px 0'
        self.btn_report.onclick.do(self.on_check_report)
        self.btn_container.append(self.btn_report)

        self.btn_add_admin = gui.Button("添加管理员", width='100%', height=30)
        self.btn_add_admin.style['margin'] = '5px 0'
        self.btn_add_admin.onclick.do(self.on_add_admin)
        self.btn_container.append(self.btn_add_admin)

        # 登录/退出按钮
        if ADMIN_LOGIN:
            self.btn_login = gui.Button("退出登录", width='100%', height=30)
            self.btn_login.style['margin'] = '5px 0'
            self.btn_login.style['background-color'] = 'red'
            self.btn_login.onclick.do(self.on_admin_logout)
        else:
            self.btn_login = gui.Button("管理员登录", width='100%', height=30)
            self.btn_login.style['margin'] = '5px 0'
            self.btn_login.onclick.do(self.on_admin_login)
        self.btn_container.append(self.btn_login)

        self.btn_exit = gui.Button("退出系统", width='100%', height=30)
        self.btn_exit.style['margin'] = '5px 0'
        self.btn_exit.onclick.do(self.on_exit)
        self.btn_container.append(self.btn_exit)

    def show_message(self, message):
        self.result_label.set_text(message)

    def close_current_dialog(self):
        if self.current_dialog and self.current_dialog in self.children:
            self.remove_child(self.current_dialog)
        self.current_dialog = None

    def on_admin_login(self, widget):
        """
        管理员登录对话框
        :param widget:
        :return:
        """
        global ADMIN_LOGIN
        if ADMIN_LOGIN:
            self.show_message("您已经以管理员身份登录")
            return

        self.dialog = gui.GenericDialog(title='管理员登录', message='请输入管理员账号和密码',width=300, height=180)

        # 创建表单
        form = gui.VBox(width='100%', height='100%')

        # 用户名输入
        username_container = gui.HBox(width='100%', height='30%')
        username_label = gui.Label('用户名:', width='30%', height='100%')
        self.username_input = gui.Input(width='70%', height='80%')
        username_container.append(username_label)
        username_container.append(self.username_input)

        # 密码输入
        password_container = gui.HBox(width='100%', height='30%')
        password_label = gui.Label('密码:', width='30%', height='100%')
        self.password_input = gui.Input(width='70%', height='80%', input_type='password')
        password_container.append(password_label)
        password_container.append(self.password_input)

        # 按钮容器
        buttons_container = gui.HBox(width='100%', height='30%')
        buttons_container.style['justify-content'] = 'center'
        buttons_container.style['align-items'] = 'center'

        # 确认按钮
        confirm_btn = gui.Button('登录', width=80, height=30)
        confirm_btn.onclick.do(self.on_login_confirm)

        # 取消按钮
        cancel_btn = gui.Button('取消', width=80, height=30)
        cancel_btn.onclick.do(self.dialog.hide)

        buttons_container.append(confirm_btn)
        buttons_container.append(cancel_btn)

        # 组装表单
        form.append(username_container)
        form.append(password_container)
        form.append(buttons_container)

        # 将表单添加到对话框
        self.dialog.add_field_with_label('form', '登录表单', form)

        # 显示对话框
        self.dialog.show(self)

    def on_login_confirm(self, widget):#验证管理员登陆
        # 获取输入的用户名和密码
        username = self.username_input.get_value()
        password = self.password_input.get_value()

        if hr.valid_user(username, password):
            global ADMIN_LOGIN
            ADMIN_LOGIN = True
            self.dialog.hide()
            self.update_buttons()
            self.update_login_status()
            self.show_message(f"{username} 登录成功!")

        else:
            # 显示错误信息
            error_label = gui.Label('用户名或密码错误!', style={'color': 'red'})
            self.dialog.add_field_with_label('error', '错误', error_label)

    def on_admin_logout(self, widget):
        """
        退出管理员登陆
        :param widget:
        :return:
        """
        global ADMIN_LOGIN, current_admin
        ADMIN_LOGIN = False
        current_admin = None
        self.login_status.set_text("未登录")
        self.login_status.style['color'] = 'red'
        self.show_message("已退出管理员登录")
        self.update_buttons()  # 更新按钮显示


    def on_clock_in(self, widget):
        """
        打卡功能
        :param widget:
        :return:
        """
        self.show_message("请正面对准摄像头进行打卡...")
        name = camera.clock_in()
        if name:
            hr.add_lock_record(name)
            self.show_message(f"{name} 打卡成功!")
        else:
            self.show_message("未识别到员工，打卡失败")

    def on_check_records(self, widget):
        """
        查看记录
        :param widget:
        :return:
        """
        dialog = gui.VBox(width=400, height=300)
        dialog.style.update({
            'background-color': '#f0f0f0',
            'border': '1px solid #333',
            'border-radius': '5px',
            'padding': '20px',
            'box-shadow': '0 4px 8px rgba(0,0,0,0.2)',
        })

        # 添加标题
        title = gui.Label('自定义窗口', width='100%', height='15%')
        title.style.update({'font-size': '18px', 'text-align': 'center'})
        dialog.append(title)

        # 添加自定义按钮
        btn1 = gui.Button('按钮1', width='80%', height=30)
        btn1.style['margin'] = '10px auto'
        btn1.onclick.do(lambda w: self.show_message("你点击了按钮1"))
        dialog.append(btn1)

        close_btn = gui.Button('关闭窗口', width='80%', height=30)
        close_btn.style['margin'] = '20px auto'
        close_btn.style['background-color'] = '#ff6666'
        close_btn.onclick.do(lambda w: dialog.set_style({'display': 'none'}))
        dialog.append(close_btn)
        self.show_message(hr.get_record_all())
        # 添加到主容器
        self.main_container.append(dialog)
        dialog.show(self)




    def close_current_dialog(self):
            """
            关闭当前对话框
            :return:
            """
            if hasattr(self, 'current_dialog') and self.current_dialog:
                self.remove_child(self.current_dialog)  # 使用 remove_child 明确移除
                self.current_dialog = None

    def on_employee_management(self, widget):
        """

        :param widget:
        :return:
        """
        self.close_current_dialog()

        # 创建员工管理对话框
        self.current_dialog = gui.VBox(width=280, height='auto')
        self.current_dialog.style['padding'] = '15px'
        self.current_dialog.style['border'] = '1px solid #ccc'
        self.current_dialog.style['background-color'] = '#f9f9f9'
        self.current_dialog.style['border-radius'] = '5px'

        title = gui.Label("员工管理", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        option = gui.DropDown(width='100%')
        option.add_item("录入新员工", "add")
        option.add_item("删除员工", "delete")
        option.style['margin-bottom'] = '15px'

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        self.current_dialog.append(title)
        self.current_dialog.append(option)
        self.current_dialog.append(buttons_container)

        def on_confirm(widget):
            selected = option.get_value()
            if selected == "add":
                self.close_current_dialog()
                self.show_add_employee_dialog()
            elif selected == "delete":
                self.close_current_dialog()
                self.show_delete_employee_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.append(self.current_dialog)

    def show_add_employee_dialog(self):
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("录入新员工", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        name_container = gui.VBox(width='100%', height='auto')
        name_label = gui.Label("员工姓名:", width='100%', height=20)
        name_input = gui.TextInput(width='100%', height=30)
        name_container.append(name_label)
        name_container.append(name_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(name_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            name = name_input.get_value().strip()
            if name:
                code = hr.add_new_employee(name)
                # 在实际应用中，这里应该调用摄像头模块注册员工
                self.show_message(f"员工 {name} 录入成功! 特征码: {code}")
                self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def show_delete_employee_dialog(self):
        employees = hr.get_employee_report()
        dialog = gui.VBox(width=350, height=300)
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("删除员工", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        # 创建员工列表
        emp_list = gui.ListView(width='100%', height=200)
        emp_list.style['overflow'] = 'auto'
        emp_list.style['border'] = '1px solid #ccc'
        emp_list.style['margin-bottom'] = '10px'

        # 解析员工数据
        emp_dict = {}
        for line in employees.split('\n'):
            if line.strip():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    emp_id = parts[0].strip()
                    emp_name = parts[1].strip()
                    emp_dict[emp_id] = emp_name
                    emp_list.append([emp_id, emp_name])

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'

        btn_confirm = gui.Button("删除", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(emp_list)
        dialog.append(buttons_container)

        def on_confirm(widget):
            selected_items = emp_list.get_selected_items()
            if selected_items:
                emp_id = selected_items[0][0]  # 获取选中的ID
                self.close_current_dialog()
                self.show_delete_verification_dialog(emp_id)
            else:
                self.show_message("请选择要删除的员工")

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def on_check_report(self, widget):
        self.close_current_dialog()

        # 创建报表对话框
        self.current_dialog = gui.VBox(width=280, height='auto')
        self.current_dialog.style['padding'] = '15px'
        self.current_dialog.style['border'] = '1px solid #ccc'
        self.current_dialog.style['background-color'] = '#f9f9f9'
        self.current_dialog.style['border-radius'] = '5px'

        title = gui.Label("考勤报表", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        option = gui.DropDown(width='100%')
        option.add_item("日报", "daily")
        option.add_item("周报", "weekly")
        option.add_item("月报", "monthly")
        option.add_item("报表设置", "config")
        option.style['margin-bottom'] = '15px'

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        self.current_dialog.append(title)
        self.current_dialog.append(option)
        self.current_dialog.append(buttons_container)

        def on_confirm(widget):
            selected = option.get_value()
            self.close_current_dialog()
            if selected == "daily":
                self.show_daily_report_dialog()
            elif selected == "weekly":
                self.show_weekly_report_dialog()
            elif selected == "monthly":
                self.show_monthly_report_dialog()
            elif selected == "config":
                self.show_report_config_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.append(self.current_dialog)

    def show_daily_report_dialog(self):
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("日报", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        date_container = gui.VBox(width='100%', height='auto')
        date_label = gui.Label("日期(YYYY-MM-DD)或0表示今天:", width='100%', height=20)
        date_input = gui.TextInput(width='100%', height=30)
        date_input.set_value("0")
        date_container.append(date_label)
        date_container.append(date_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(date_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            date_str = date_input.get_value().strip()
            if date_str == "0":
                today = datetime.date.today()
                date_str = today.strftime("%Y-%m-%d")
            elif not tool.valid_date(date_str):
                self.show_message("日期格式错误")
                return

            report = hr.get_day_report(date_str)
            self.show_message(report)
            self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def show_weekly_report_dialog(self):
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("周报", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        week_container = gui.VBox(width='100%', height='auto')
        week_label = gui.Label("周数(1-53)或0表示本周:", width='100%', height=20)
        week_input = gui.TextInput(width='100%', height=30)
        week_input.set_value("0")
        week_container.append(week_label)
        week_container.append(week_input)

        year_container = gui.VBox(width='100%', height='auto')
        year_label = gui.Label("年份(YYYY)或0表示今年:", width='100%', height=20)
        year_input = gui.TextInput(width='100%', height=30)
        year_input.set_value("0")
        year_container.append(year_label)
        year_container.append(year_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(week_container)
        dialog.append(year_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            week_str = week_input.get_value().strip()
            year_str = year_input.get_value().strip()

            if week_str == "0":
                today = datetime.date.today()
                year = today.year
                week, _ = today.isocalendar()[1:]
            else:
                try:
                    week = int(week_str)
                    if week < 1 or week > 53:
                        raise ValueError
                except ValueError:
                    self.show_message("周数必须在1-53之间")
                    return

                if year_str == "0":
                    year = datetime.date.today().year
                else:
                    try:
                        year = int(year_str)
                    except ValueError:
                        self.show_message("年份格式错误")
                        return

            report = hr.get_week_report(year, week)
            self.show_message(report)
            self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def show_monthly_report_dialog(self):
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("月报", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        month_container = gui.VBox(width='100%', height='auto')
        month_label = gui.Label("月份(YYYY-MM)或0表示上个月:", width='100%', height=20)
        month_input = gui.TextInput(width='100%', height=30)
        month_input.set_value("0")
        month_container.append(month_label)
        month_container.append(month_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(month_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            month_str = month_input.get_value().strip()
            if month_str == "0":
                # 获取上个月
                today = datetime.date.today()
                first = datetime.date(day=1, month=today.month, year=today.year)
                last_month = first - datetime.timedelta(days=1)
                month_str = last_month.strftime("%Y-%m")
            elif not tool.valid_year_month(month_str):
                self.show_message("月份格式错误")
                return

            report = hr.get_month_report(month_str)
            self.show_message(report)
            self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def show_report_config_dialog(self):
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("报表设置", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        work_container = gui.VBox(width='100%', height='auto')
        work_label = gui.Label("上班时间(HH:MM:SS):", width='100%', height=20)
        work_input = gui.TextInput(width='100%', height=30)
        work_input.set_value("08:00:00")
        work_container.append(work_label)
        work_container.append(work_input)

        close_container = gui.VBox(width='100%', height='auto')
        close_label = gui.Label("下班时间(HH:MM:SS):", width='100%', height=20)
        close_input = gui.TextInput(width='100%', height=30)
        close_input.set_value("23:59:59")
        close_container.append(close_label)
        close_container.append(close_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(work_container)
        dialog.append(close_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            work_time = work_input.get_value().strip()
            close_time = close_input.get_value().strip()

            if not tool.valid_time(work_time):
                self.show_message("上班时间格式错误")
                return
            if not tool.valid_time(close_time):
                self.show_message("下班时间格式错误")
                return

            hr.save_work_time(work_time, close_time)
            self.show_message(f"设置完成\n上班时间: {work_time}\n下班时间: {close_time}")
            self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def on_add_admin(self, widget):
        self.close_current_dialog()

        # 创建添加管理员对话框
        dialog = gui.VBox(width=280, height='auto')
        dialog.style['padding'] = '15px'
        dialog.style['border'] = '1px solid #ccc'
        dialog.style['background-color'] = '#f9f9f9'
        dialog.style['border-radius'] = '5px'

        title = gui.Label("添加管理员", width='100%', height=20)
        title.style['font-weight'] = 'bold'
        title.style['margin-bottom'] = '15px'
        title.style['text-align'] = 'center'

        username_container = gui.VBox(width='100%', height='auto')
        username_label = gui.Label("用户名:", width='100%', height=20)
        username_input = gui.TextInput(width='100%', height=30)
        username_container.append(username_label)
        username_container.append(username_input)

        buttons_container = gui.HBox(width='100%', height=40)
        buttons_container.style['justify-content'] = 'space-between'
        buttons_container.style['margin-top'] = '15px'

        btn_confirm = gui.Button("确定", width='48%', height=30)
        btn_cancel = gui.Button("取消", width='48%', height=30)
        buttons_container.append(btn_confirm)
        buttons_container.append(btn_cancel)

        dialog.append(title)
        dialog.append(username_container)
        dialog.append(buttons_container)

        def on_confirm(widget):
            username = username_input.get_value().strip()
            if username:
                hr.add_user(username)
                self.show_message(f"管理员 {username} 添加成功!")
                self.close_current_dialog()

        def on_cancel(widget):
            self.close_current_dialog()

        btn_confirm.onclick.do(on_confirm)
        btn_cancel.onclick.do(on_cancel)

        self.current_dialog = dialog
        self.append(dialog)

    def on_exit(self, widget):
        self.close()


# 启动应用
if __name__ == "__main__":
    start(ClockInSystem, address='0.0.0.0', port=8081, start_browser=True)