from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text='[b]VBN Fortress Login[/b]', markup=True, font_size='26sp', size_hint_y=None, height=60))
        
        self.username_input = TextInput(hint_text='Username or Phone', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.password_input)
        
        login_btn = Button(text='Login', size_hint_y=None, height=60, background_color=(0.1, 0.5, 0.8, 1))
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)
        
        self.status_label = Label(text='', font_size='14sp', size_hint_y=None, height=40)
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)

    def do_login(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        if not username or not password:
            self.status_label.text = 'Please fill in all fields.'
            return
        
        self.status_label.text = 'Logging in...'
        try:
            url = "https://your-backend-server.com/api/login"
            payload = {"username": username, "password": password}
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token", "dummy_token")
                app = App.get_running_app()
                app.auth_token = token
                app.username = username
                app.fetch_user_data()
                self.manager.current = 'dashboard'
            else:
                self.status_label.text = 'Invalid credentials!'
        except Exception as e:
            # Fallback for testing/offline mode
            if username == "admin" and password == "1234":
                app = App.get_running_app()
                app.auth_token = "mock_token"
                app.username = username
                app.fetch_user_data()
                self.manager.current = 'dashboard'
            else:
                self.status_label.text = 'Connection error or invalid login.'

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Balance Display
        self.balance_label = Label(text='Balance: $0.00', font_size='22sp', bold=True, size_hint_y=None, height=40)
        self.layout.add_widget(self.balance_label)
        
        # Transfer Section
        transfer_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200)
        transfer_box.add_widget(Label(text='[b]Send Money[/b]', markup=True, font_size='18sp', size_hint_y=None, height=30))
        
        self.recipient_input = TextInput(hint_text='Recipient Account', multiline=False, size_hint_y=None, height=45)
        transfer_box.add_widget(self.recipient_input)
        
        self.amount_input = TextInput(hint_text='Amount', input_filter='float', multiline=False, size_hint_y=None, height=45)
        transfer_box.add_widget(self.amount_input)
        
        send_btn = Button(text='Transfer', size_hint_y=None, height=50, background_color=(0.1, 0.7, 0.3, 1))
        send_btn.bind(on_press=self.send_money)
        transfer_box.add_widget(send_btn)
        
        self.layout.add_widget(transfer_box)
        
        # Transaction History Section
        self.layout.add_widget(Label(text='[b]Transaction History[/b]', markup=True, font_size='18sp', size_hint_y=None, height=30))
        
        self.history_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.history_layout)
        self.layout.add_widget(scroll)
        
        # Bottom Bar (Status & Logout)
        bottom_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.status_label = Label(text='', font_size='14sp')
        bottom_box.add_widget(self.status_label)
        
        logout_btn = Button(text='Logout', size_hint_x=None, width=100, background_color=(0.8, 0.2, 0.2, 1))
        logout_btn.bind(on_press=self.logout)
        bottom_box.add_widget(logout_btn)
        
        self.layout.add_widget(bottom_box)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        app.fetch_user_data()

    def send_money(self, instance):
        recipient = self.recipient_input.text
        amount = self.amount_input.text
        
        if not recipient or not amount:
            self.status_label.text = 'Enter recipient and amount.'
            return
        
        self.status_label.text = 'Processing transfer...'
        app = App.get_running_app()
        
        try:
            url = "https://your-backend-server.com/api/transfer"
            headers = {"Authorization": f"Bearer {app.auth_token}"}
            payload = {"recipient": recipient, "amount": float(amount)}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.status_label.text = 'Transfer successful!'
                self.recipient_input.text = ''
                self.amount_input.text = ''
                app.fetch_user_data()
            else:
                self.status_label.text = 'Transfer failed.'
        except Exception as e:
            # Mock mode update for testing without server
            self.status_label.text = 'Transfer sent (Mock Mode).'
            app.balance -= float(amount)
            app.transactions.insert(0, f"Sent ${amount} to {recipient}")
            app.update_dashboard_ui()
            self.recipient_input.text = ''
            self.amount_input.text = ''

    def logout(self, instance):
        app = App.get_running_app()
        app.auth_token = None
        self.manager.current = 'login'

class VbnFortressApp(App):
    def build(self):
        self.auth_token = None
        self.username = ""
        self.balance = 1500.50
        self.transactions = [
            "Received $500.00 from Ali",
            "Sent $50.00 to Mohammed",
            "Deposited $1000.00"
        ]
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

    def fetch_user_data(self):
        try:
            url = f"https://your-backend-server.com/api/user/{self.username}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.balance = data.get("balance", 0.0)
                self.transactions = data.get("transactions", [])
        except:
            pass
        
        self.update_dashboard_ui()

    def update_dashboard_ui(self):
        dashboard = self.root.get_screen('dashboard')
        dashboard.balance_label.text = f"Balance: ${self.balance:.2f}"
        
        dashboard.history_layout.clear_widgets()
        for tx in self.transactions:
            lbl = Label(text=tx, size_hint_y=None, height=40, font_size='14sp')
            dashboard.history_layout.add_widget(lbl)

if __name__ == '__main__':
    VbnFortressApp().run()
