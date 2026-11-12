import os
import json
import hashlib
import hmac
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

Window.clearcolor = (0.05, 0.07, 0.09, 1)

VAULT_SIZE = 131072  # 128 KB
OFFSET_MASTER = 4096
OFFSET_DECOY = 69632
BLOCK_SIZE = 32768

class CryptoEngine:
    @staticmethod
    def get_vault_path():
        app = App.get_running_app()
        folder = app.user_data_dir if app else "."
        return os.path.join(folder, "vbn_fortress.dat")

    @staticmethod
    def derive_key(pin, salt):
        return hashlib.pbkdf2_hmac('sha256', pin.encode(), salt, 100000, dklen=32)

    @staticmethod
    def xor_stream(data, key):
        out = bytearray(len(data))
        counter = 0
        for i in range(0, len(data), 32):
            block_key = hmac.new(key, counter.to_bytes(8, 'big'), hashlib.sha256).digest()
            chunk = data[i:i+32]
            for j in range(len(chunk)):
                out[i+j] = chunk[j] ^ block_key[j]
            counter += 1
        return bytes(out)

    @classmethod
    def vault_exists(cls):
        return os.path.exists(cls.get_vault_path())

    @classmethod
    def init_vault(cls, master_pin, decoy_pin):
        container = bytearray(os.urandom(VAULT_SIZE))
        m_salt = os.urandom(16)
        d_salt = os.urandom(16)
        container[0:16] = m_salt
        container[16:32] = d_salt

        m_data = {"type": "MASTER", "balance": 0.0, "txs": []}
        d_data = {"type": "DECOY", "balance": 0.0, "txs": []}

        cls._write_slot(container, OFFSET_MASTER, cls.derive_key(master_pin, m_salt), m_data)
        cls._write_slot(container, OFFSET_DECOY, cls.derive_key(decoy_pin, d_salt), d_data)

        with open(cls.get_vault_path(), "wb") as f:
            f.write(container)

    @classmethod
    def _write_slot(cls, container, offset, key, data_dict):
        raw = json.dumps(data_dict).encode('utf-8')
        checksum = hashlib.sha256(raw).digest()[:8]
        payload = b"VBN1" + len(raw).to_bytes(4, 'big') + checksum + raw
        padded = payload + os.urandom(BLOCK_SIZE - len(payload))
        encrypted = cls.xor_stream(padded, key)
        container[offset:offset+BLOCK_SIZE] = encrypted

    @classmethod
    def unlock(cls, pin):
        path = cls.get_vault_path()
        if not os.path.exists(path):
            return None, None
        with open(path, "rb") as f:
            container = bytearray(f.read())
        if len(container) != VAULT_SIZE:
            return None, None

        m_salt = bytes(container[0:16])
        d_salt = bytes(container[16:32])

        for offset, salt in [(OFFSET_MASTER, m_salt), (OFFSET_DECOY, d_salt)]:
            key = cls.derive_key(pin, salt)
            dec = cls.xor_stream(bytes(container[offset:offset+BLOCK_SIZE]), key)
            if dec[:4] == b"VBN1":
                length = int.from_bytes(dec[4:8], 'big')
                if 0 < length < BLOCK_SIZE - 16:
                    checksum = dec[8:16]
                    raw = dec[16:16+length]
                    if hashlib.sha256(raw).digest()[:8] == checksum:
                        return json.loads(raw.decode('utf-8')), (offset, key)
        return None, None

    @classmethod
    def save_data(cls, slot_info, data_dict):
        offset, key = slot_info
        with open(cls.get_vault_path(), "rb") as f:
            container = bytearray(f.read())
        cls._write_slot(container, offset, key, data_dict)
        with open(cls.get_vault_path(), "wb") as f:
            f.write(container)

    @classmethod
    def destroy_vault(cls):
        path = cls.get_vault_path()
        if os.path.exists(path):
            with open(path, "wb") as f:
                f.write(os.urandom(VAULT_SIZE))
            os.remove(path)

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="VBN FORTRESS SETUP", font_size='24sp', bold=True, color=(0.35, 0.65, 1, 1)))
        layout.add_widget(Label(text="Create 128KB Dual-Vault Container", font_size='14sp', color=(0.6, 0.6, 0.6, 1)))

        self.m_pin = TextInput(hint_text="Master PIN (6-12 digits)", password=True, input_filter='int', multiline=False, font_size='18sp', size_hint_y=None, height=50)
        self.d_pin = TextInput(hint_text="Decoy PIN (6-12 digits)", password=True, input_filter='int', multiline=False, font_size='18sp', size_hint_y=None, height=50)
        self.status = Label(text="", color=(1, 0.3, 0.3, 1), font_size='14sp')

        btn = Button(text="INITIALIZE VAULTS", background_color=(0.14, 0.53, 0.21, 1), font_size='16sp', bold=True, size_hint_y=None, height=55)
        btn.bind(on_press=self.create_vaults)

        layout.add_widget(self.m_pin)
        layout.add_widget(self.d_pin)
        layout.add_widget(self.status)
        layout.add_widget(btn)
        self.add_widget(layout)

    def
