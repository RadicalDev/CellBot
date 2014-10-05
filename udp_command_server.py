__author__ = 'jfindley'
import socket, time, math
from numpy import interp
from sh import cam_control
PKT_SIZE=87

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 2560))

class CameraController(object):
    def __init__(self):
        self.az = 0
        self.af = 0
        self.ae = 0
        self.auto_focus_enabled = True
        self.auto_exposure_enabled = True

    def get_auto_focus_enabled(self):
        return self.auto_focus_enabled

    def get_auto_exposure_enabled(self):
        return self.auto_exposure_enabled

    def enable_auto_focus(self):
        if self.get_auto_focus_enabled():
            return
        print "Enabling AF"
        self.auto_focus_enabled = True
        cam_control('-d', '1', '-c', 'focus_auto=1')

    def disable_auto_focus(self):
        if not self.get_auto_focus_enabled():
            return
        print 'Disabling AF" '
        self.auto_focus_enabled = False
        cam_control('-d', '1', '-c', 'focus_auto=0')

    def enable_auto_exposure(self):
        if self.get_auto_exposure_enabled():
            return
        self.auto_exposure_enabled = True
        print "Enabling AE"
        cam_control('-d', '1', '-c', 'exposure_auto=3')

    def disable_auto_exposure(self):
        if not self.get_auto_exposure_enabled():
            return
        print "Disabling AE"
        self.auto_exposure_enabled = False
        cam_control('-d', '1', '-c', 'exposure_auto=1')

    def inc_focus(self):
        self.af = self.af + 1 if self.af+1 <= 40 else 40
        self.focus_control(self.af)

    def dec_focus(self):
        self.af = self.af - 1 if self.af-1 >= 0 else 0
        self.focus_control(self.af)

    def inc_zoom(self):
        self.az = self.az + 1 if self.az+1 <= 10 else 10
        self.zoom_control(self.az)

    def dec_zoom(self):
        self.az = self.az - 1 if self.az-1 >= 0 else 0
        self.zoom_control(self.az)

    def inc_exposure(self):
        self.ae = self.ae + 1 if self.ae+1 <= 20000 else 20000
        self.exposure_control(self.ae)

    def dec_exposure(self):
        self.ae = self.ae - 1 if self.ae-1 >= 0 else 0
        self.exposure_control(self.ae)

    def reset_zoom(self):
        self.az = 0
        self.zoom_control(self.az)

    def zoom_max(self):
        self.az = 10
        self.zoom_control(self.az)

    def reset_focus(self):
        self.af = 0
        self.focus_control(self.af)

    def max_focus(self):
        self.af = 40
        self.focus_control(self.af)

    def reset_exposure(self):
        self.ae = 0
        self.exposure_control(self.ae)

    def max_exposure(self):
        self.ae = 20000
        self.exposure_control(self.ae)

    def zoom_control(self, val):
        if not isinstance(val, int):
            val = int(interp(val, [0.0, 1.0], [0, 10]))

        val = 0 if val <= 0 else val
        val = 10 if val >= 10 else val
        if val != self.az:
            print "ZOOMING TO: ", val
            cam_control('-d', '1', '-c', 'zoom_absolute={0}'.format(val))
            self.az = val

    def focus_control(self, val):
        if self.get_auto_focus_enabled():
            return

        if not isinstance(val, int):
            val = int(interp(val, [0.0, 1.0], [0, 40]))

        if val != self.af:
            print "FOCUS TO: ", val
            cam_control('-d', '1', '-c', 'focus_absolute={0}'.format(val))
            self.af = val

    def exposure_control(self, val):
        if self.get_auto_exposure_enabled():
            return
        print "EXPOSE TO: ", val

        cam_control('-d', '1', '-c', 'exposure_absolute={0}'.format(val))



class Engine(object):
    def __init__(self):
        self.last_lt = 0
        self.last_rt = 0
        self.last_ljsx = 0
        self.last_rjsx = 0
        self.last_ljsy = 0
        self.last_rjsy = 0
        self.camera = CameraController()

    def act_on_controller_data(self, controller_data):
        self.process_controller_data(controller_data)

    def process_controller_data(self, controller_data):
        if len(controller_data) >= 81:
            self.process_controller_state(controller_data)
        else:
            self.process_button_code(controller_data)

    def process_button_code(self, button_code):
        print button_code
        if button_code == 'L_DOWN':
            self.camera.zoom_max()
        if button_code == 'L_UP':
            self.camera.reset_zoom()
        if button_code == 'R_DOWN':
            self.camera.enable_auto_exposure()
        if button_code == 'R_UP':
            self.camera.disable_auto_exposure()

    def process_controller_state(self, controller_state):
        d = eval(controller_state)
        for key, value in d.iteritems():
            if key == 'LT':
                self.camera.zoom_control(value)
            if key == 'RT':
                self.camera.focus_control(value)
            if key == 'HY':
                if value < 0:
                    self.camera.enable_auto_exposure()
                elif value > 0:
                    self.camera.disable_auto_exposure()
            if key == 'HX':
                if value < 0:
                    self.camera.enable_auto_focus()
                elif value > 0:
                    self.camera.disable_auto_focus()
            if key == 'LY':
                pass
            if key == 'LX':
                pass
            if key == 'RY':
                pass
            if key == 'RX':
                pass


if __name__ == "__main__":
    engine = Engine()
    start = time.time()
    cmds = 0
    total_data = 0
    while True:
        data = s.recvfrom(PKT_SIZE)[0]
        engine.act_on_controller_data(data)
        #print "Commands per second: ", cmds/(time.time()-start), ' Total data: ', total_data/1000000.0
        total_data += len(data)
        cmds += 1