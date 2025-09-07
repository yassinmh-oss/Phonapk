from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.graphics.texture import Texture
import threading
import time
import os
import socket
import json
from datetime import datetime

# استيراد انتقائي للوحدات المتاحة
try:
    from plyer import accelerometer, gyroscope, orientation, proximity, light
    from plyer import compass, gps, battery, vibrator, notification, camera
    from plyer import tts, uniqueid, bluetooth, wifi, sms, email, call, filechooser
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("⚠️ مكتبة plyer غير متاحة بالكامل")

class CameraTab(BoxLayout):
    def __init__(self, **kwargs):
        super(CameraTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        
        # عرض الصورة
        self.image_widget = Image(size_hint=(1, 0.7))
        self.add_widget(self.image_widget)
        
        # أزرار التحكم
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.capture_btn = Button(text='التقاط صورة')
        self.capture_btn.bind(on_press=self.capture_image)
        btn_layout.add_widget(self.capture_btn)
        
        self.record_btn = Button(text='تسجيل فيديو')
        self.record_btn.bind(on_press=self.record_video)
        btn_layout.add_widget(self.record_btn)
        
        self.gallery_btn = Button(text='معرض الصور')
        self.gallery_btn.bind(on_press=self.open_gallery)
        btn_layout.add_widget(self.gallery_btn)
        
        self.add_widget(btn_layout)
        
        # معلومات الصورة
        self.info_label = Label(text='جاهز للتصوير', size_hint=(1, 0.1))
        self.add_widget(self.info_label)
        
        self.capturing = False

    def capture_image(self, instance):
        try:
            def on_success(filename):
                self.info_label.text = f'تم حفظ الصورة: {filename}'
                self.update_image_preview(filename)
                
            def on_error(error):
                self.info_label.text = f'خطأ: {error}'
                
            camera.take_picture(
                filename=f'/sdcard/DCIM/photo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                on_complete=on_success
            )
        except Exception as e:
            self.info_label.text = f'خطأ في الكاميرا: {str(e)}'

    def update_image_preview(self, filename):
        try:
            if os.path.exists(filename):
                self.image_widget.source = filename
                self.image_widget.reload()
        except Exception as e:
            print(f"خطأ في عرض الصورة: {e}")

    def record_video(self, instance):
        self.info_label.text = 'ميزة الفيديو قيد التطوير'

    def open_gallery(self, instance):
        try:
            filechooser.open_file(
                filters=['*.jpg', '*.png', '*.jpeg'],
                on_selection=self.gallery_selected
            )
        except Exception as e:
            self.info_label.text = f'خطأ في المعرض: {str(e)}'

    def gallery_selected(self, selection):
        if selection:
            self.update_image_preview(selection[0])

class BluetoothTab(BoxLayout):
    def __init__(self, **kwargs):
        super(BluetoothTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        
        # حالة البلوتوث
        self.status_label = Label(text='حالة البلوتوث: غير معروف', size_hint=(1, 0.1))
        self.add_widget(self.status_label)
        
        # أزرار التحكم
        control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.toggle_btn = Button(text='تفعيل البلوتوث')
        self.toggle_btn.bind(on_press=self.toggle_bluetooth)
        control_layout.add_widget(self.toggle_btn)
        
        self.scan_btn = Button(text='بحث عن أجهزة')
        self.scan_btn.bind(on_press=self.scan_devices)
        control_layout.add_widget(self.scan_btn)
        
        self.add_widget(control_layout)
        
        # قائمة الأجهزة
        self.devices_label = Label(text='الأجهزة:', size_hint=(1, 0.1))
        self.add_widget(self.devices_label)
        
        self.devices_list = GridLayout(cols=1, size_hint_y=None)
        self.devices_list.bind(minimum_height=self.devices_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 0.6))
        scroll.add_widget(self.devices_list)
        self.add_widget(scroll)
        
        # نقل الملفات
        self.transfer_btn = Button(text='إرسال ملف', size_hint=(1, 0.1))
        self.transfer_btn.bind(on_press=self.send_file)
        self.add_widget(self.transfer_btn)
        
        self.update_bluetooth_status()

    def toggle_bluetooth(self, instance):
        try:
            if bluetooth.is_enabled():
                bluetooth.disable()
                self.status_label.text = 'حالة البلوتوث: معطل'
                instance.text = 'تفعيل البلوتوث'
            else:
                bluetooth.enable()
                self.status_label.text = 'حالة البلوتوث: مفعل'
                instance.text = 'تعطيل البلوتوث'
        except Exception as e:
            self.status_label.text = f'خطأ: {str(e)}'

    def update_bluetooth_status(self):
        try:
            if bluetooth.is_enabled():
                self.status_label.text = 'حالة البلوتوث: مفعل'
                self.toggle_btn.text = 'تعطيل البلوتوث'
            else:
                self.status_label.text = 'حالة البلوتوث: معطل'
                self.toggle_btn.text = 'تفعيل البلوتوث'
        except:
            self.status_label.text = 'البلوتوث غير مدعوم'

    def scan_devices(self, instance):
        self.devices_list.clear_widgets()
        self.devices_label.text = 'جاري البحث عن الأجهزة...'
        
        def scan_thread():
            try:
                devices = bluetooth.discover_devices()
                Clock.schedule_once(lambda dt: self.update_devices_list(devices))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(str(e)))
        
        threading.Thread(target=scan_thread, daemon=True).start()

    def update_devices_list(self, devices):
        self.devices_list.clear_widgets()
        if devices:
            for device in devices:
                btn = Button(text=device, size_hint_y=None, height=50)
                btn.bind(on_press=lambda x, d=device: self.connect_device(d))
                self.devices_list.add_widget(btn)
            self.devices_label.text = f'تم العثور على {len(devices)} أجهزة'
        else:
            self.devices_label.text = 'لم يتم العثور على أجهزة'

    def connect_device(self, device):
        self.show_popup(f'جاري الاتصال ب {device}')

    def send_file(self, instance):
        try:
            filechooser.open_file(on_selection=self.file_selected)
        except Exception as e:
            self.show_error(f'خطأ: {str(e)}')

    def file_selected(self, selection):
        if selection:
            self.show_popup(f'تم اختيار الملف: {selection[0]}')

    def show_popup(self, message):
        popup = Popup(title='إشعار', content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def show_error(self, message):
        self.status_label.text = f'خطأ: {message}'

class FileTransferTab(BoxLayout):
    def __init__(self, **kwargs):
        super(FileTransferTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        
        # خادم/عميل
        mode_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.server_btn = Button(text='تشغيل الخادم')
        self.server_btn.bind(on_press=self.start_server)
        mode_layout.add_widget(self.server_btn)
        
        self.client_btn = Button(text='الاتصال كعميل')
        self.client_btn.bind(on_press=self.connect_client)
        mode_layout.add_widget(self.client_btn)
        
        self.add_widget(mode_layout)
        
        # معلومات الاتصال
        self.status_label = Label(text='حالة: غير متصل', size_hint=(1, 0.1))
        self.add_widget(self.status_label)
        
        # إدخال IP
        ip_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        ip_layout.add_widget(Label(text='IP:'))
        
        self.ip_input = TextInput(text='192.168.1.1', multiline=False)
        ip_layout.add_widget(self.ip_input)
        
        self.add_widget(ip_layout)
        
        # نقل الملفات
        transfer_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.send_btn = Button(text='إرسال ملف')
        self.send_btn.bind(on_press=self.send_file)
        transfer_layout.add_widget(self.send_btn)
        
        self.receive_btn = Button(text='استقبال ملفات')
        self.receive_btn.bind(on_press=self.receive_files)
        transfer_layout.add_widget(self.receive_btn)
        
        self.add_widget(transfer_layout)
        
        # تقدم النقل
        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.1))
        self.add_widget(self.progress_bar)
        
        self.progress_label = Label(text='0%', size_hint=(1, 0.1))
        self.add_widget(self.progress_label)
        
        # سجل النقل
        self.log_label = Label(text='سجل النقل:', size_hint=(1, 0.3))
        self.add_widget(self.log_label)
        
        self.server_socket = None
        self.client_socket = None
        self.is_server = False

    def start_server(self, instance):
        self.is_server = True
        self.status_label.text = 'جاري تشغيل الخادم...'
        
        def server_thread():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind(('0.0.0.0', 12345))
                self.server_socket.listen(1)
                
                Clock.schedule_once(lambda dt: self.update_status('خادم يعمل على port 12345'))
                
                while self.is_server:
                    client, addr = self.server_socket.accept()
                    Clock.schedule_once(lambda dt: self.update_status(f'عميل متصل: {addr}'))
                    
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f'خطأ: {str(e)}'))
        
        threading.Thread(target=server_thread, daemon=True).start()

    def connect_client(self, instance):
        self.is_server = False
        self.status_label.text = 'جاري الاتصال...'
        
        def client_thread():
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.ip_input.text, 12345))
                Clock.schedule_once(lambda dt: self.update_status('متصل بالخادم'))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f'خطأ اتصال: {str(e)}'))
        
        threading.Thread(target=client_thread, daemon=True).start()

    def send_file(self, instance):
        try:
            filechooser.open_file(on_selection=self.file_to_send)
        except Exception as e:
            self.update_status(f'خطأ: {str(e)}')

    def file_to_send(self, selection):
        if selection and self.client_socket:
            filename = selection[0]
            self.transfer_file(filename)

    def transfer_file(self, filename):
        def transfer_thread():
            try:
                filesize = os.path.getsize(filename)
                with open(filename, 'rb') as f:
                    self.client_socket.sendall(f"{os.path.basename(filename)}|{filesize}".encode())
                    
                    total_sent = 0
                    while True:
                        data = f.read(4096)
                        if not data:
                            break
                        self.client_socket.sendall(data)
                        total_sent += len(data)
                        
                        progress = (total_sent / filesize) * 100
                        Clock.schedule_once(lambda dt: self.update_progress(progress))
                
                Clock.schedule_once(lambda dt: self.update_status('تم الإرسال بنجاح'))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_status(f'خطإ في الإرسال: {str(e)}'))
        
        threading.Thread(target=transfer_thread, daemon=True).start()

    def receive_files(self, instance):
        self.update_status('جاهز لاستقبال الملفات')

    def update_status(self, message):
        self.status_label.text = message
        self.log_label.text += f'\n{datetime.now().strftime("%H:%M:%S")} - {message}'

    def update_progress(self, value):
        self.progress_bar.value = value
        self.progress_label.text = f'{value:.1f}%'

class SystemInfoTab(BoxLayout):
    def __init__(self, **kwargs):
        super(SystemInfoTab, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        
        self.info_labels = {}
        
        # معلومات النظام
        info_categories = [
            ('البطارية', self.get_battery_info),
            ('الذاكرة', self.get_memory_info),
            ('التخزين', self.get_storage_info),
            ('الشبكة', self.get_network_info),
            ('الجهاز', self.get_device_info)
        ]
        
        for category, callback in info_categories:
            category_label = Label(text=category, size_hint_y=None, height=40, bold=True)
            self.add_widget(category_label)
            
            info_label = Label(text='جاري التحميل...', size_hint_y=None, height=60)
            self.add_widget(info_label)
            self.info_labels[category] = info_label
        
        # زر التحديث
        self.refresh_btn = Button(text='تحديث المعلومات', size_hint=(1, 0.1))
        self.refresh_btn.bind(on_press=self.refresh_info)
        self.add_widget(self.refresh_btn)
        
        self.refresh_info()

    def get_battery_info(self):
        try:
            status = battery.status
            return f'المستوى: {battery.percentage}% - الشحن: {"نعم" if status.get("isCharging", False) else "لا"}'
        except:
            return 'غير متاح'

    def get_memory_info(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.readlines()
            return f'ذاكرة: {meminfo[0].split()[1]} KB'
        except:
            return 'غير متاح'

    def get_storage_info(self):
        try:
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bfree * stat.f_frsize
            return f'الإجمالي: {total//1024//1024}MB - المتاح: {free//1024//1024}MB'
        except:
            return 'غير متاح'

    def get_network_info(self):
        try:
            import netifaces
            interfaces = netifaces.interfaces()
            return f'واجهات: {len(interfaces)}'
        except:
            return 'غير متاح'

    def get_device_info(self):
        try:
            device_id = uniqueid.id if hasattr(uniqueid, 'id') else 'غير معروف'
            return f'المعرف: {device_id}'
        except:
            return 'غير متاح'

    def refresh_info(self, instance=None):
        for category, callback in [
            ('البطارية', self.get_battery_info),
            ('الذاكرة', self.get_memory_info),
            ('التخزين', self.get_storage_info),
            ('الشبكة', self.get_network_info),
            ('الجهاز', self.get_device_info)
        ]:
            self.info_labels[category].text = callback()

class PhoneControllerApp(App):
    def build(self):
        if not PLYER_AVAILABLE:
            return Label(text="❌ مكتبة plyer غير مثبتة\n\nيرجى تثبيتها عبر:\npip install plyer", font_size=20)
        
        # إنشاء واجهة التبويبات
        tabs = TabbedPanel(do_default_tab=False)
        
        # تبويب الكاميرا
        camera_tab = TabbedPanelItem(text='📷 الكاميرا')
        camera_tab.add_widget(CameraTab())
        tabs.add_widget(camera_tab)
        
        # تبويب البلوتوث
        bluetooth_tab = TabbedPanelItem(text='📡 البلوتوث')
        bluetooth_tab.add_widget(BluetoothTab())
        tabs.add_widget(bluetooth_tab)
        
        # تبويب نقل الملفات
        transfer_tab = TabbedPanelItem(text='📂 نقل الملفات')
        transfer_tab.add_widget(FileTransferTab())
        tabs.add_widget(transfer_tab)
        
        # تبويب معلومات النظام
        info_tab = TabbedPanelItem(text='ℹ️ معلومات النظام')
        info_tab.add_widget(SystemInfoTab())
        tabs.add_widget(info_tab)
        
        return tabs

    def on_stop(self):
        # تنظيف الموارد عند إغلاق التطبيق
        try:
            if hasattr(accelerometer, 'disable'):
                accelerometer.disable()
            if hasattr(gps, 'stop'):
                gps.stop()
        except:
            pass

if __name__ == '__main__':
    PhoneControllerApp().run()
