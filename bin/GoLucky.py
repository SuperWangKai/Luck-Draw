# -*- coding: utf-8 -*-

# Simple lucky draw program
# kai1.wang@intel.com
# 2015-11-27


import json
import copy
import time
import random
import os.path
import traceback
import fontpicker
import tkinter.tix
import tkinter.ttk
import tkinter.colorchooser
import tkinter.filedialog
from tkinter import *
from PIL import ImageTk, Image
from functools import partial

ROLLING_INTERVAL = 0.005  # sec
USER_SETTING_FILE = '../config/user.cfg'
DEFAULT_SETTING_FILE = '../config/default.cfg'
SETTING_ICON = '../res/settings.png'
DEF_BG_IMAGE = '../res/bg.png'


class SettingWindow:
    def __init__(self, parent):

        self.dirty = False

        self.mute_notify = False

        self.current_row = 0

        self.settings = copy.deepcopy(parent.settings)

        self.controls = {}

        self.parent = parent

        self.root = tkinter.tix.Toplevel()
        self.root.transient(parent.root)

        self.root.resizable(0, 0)

        self.root.protocol('WM_DELETE_WINDOW', self.on_cancel)

        self.frame = Frame(self.root)

        for s in self.parent.settings:
            self.create_option(s)

        self.separator = tkinter.ttk.Separator(self.frame)
        self.separator.grid(row=self.current_row, column=0, columnspan=2, sticky='ew', pady=20)
        self.current_row += 1

        self.button_frame = Frame(self.frame)

        self.default_button = Button(self.button_frame, text='Default', command=self.on_default).grid(row=0, column=0,
                                                                                                      padx=4, pady=10,
                                                                                                      sticky=S)
        self.cancel_button = Button(self.button_frame, text='Cancel', command=self.on_cancel).grid(row=0, column=1,
                                                                                                   padx=4, pady=10,
                                                                                                   sticky=S)
        self.save_button = Button(self.button_frame, text='Save', command=self.on_save).grid(row=0, column=2, padx=4,
                                                                                             pady=10, sticky=S)

        self.button_frame.grid(row=self.current_row, column=1)

        self.frame.pack(padx=8, pady=8)

        self.update_title()

        # self.set_to_center()

    def set_to_center(self):
        self.root.update_idletasks()
        width = self.root["width"] != 0 and self.root["width"] or self.root.winfo_width()
        height = self.root["height"] != 0 and self.root["height"] or self.root.winfo_height()
        win_width, win_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(
            '%dx%d+%d+%d' % (width, height, (win_width / 2) - (width / 2), (win_height / 2) - (height / 2)))

    def create_option(self, opt):
        t = opt[1]
        if t == 'int':
            c, v = self.create_int_option(opt[0], opt[2])
        elif t == 'text':
            c, v = self.create_text_option(opt[0], opt[2])
        elif t == 'font':
            c, v = self.create_font_option(opt[0], opt[2])
        elif t == 'color':
            c, v = self.create_color_option(opt[0], opt[2])
        elif t == 'path':
            c, v = self.create_path_option(opt[0], opt[2])
        else:
            raise Exception('Unknown option type', opt)

        self.controls[opt[0]] = (c, v)

    def create_int_option(self, name, v):
        value = IntVar()
        value.set(v[2])
        value.trace("w", partial(self.on_int_variable, name))

        left = Label(self.frame, text=name, anchor=W)
        right = Scale(self.frame, orient=HORIZONTAL, variable=value, from_=v[0], to=v[1])
        left.grid(row=self.current_row, column=0, sticky=E + W, pady=0)
        right.grid(row=self.current_row, column=1, sticky=E + W, pady=0)

        self.current_row += 1

        return right, value

    def create_text_option(self, name, v):
        value = StringVar()
        value.set(v)
        value.trace("w", partial(self.on_text_variable, name))

        left = Label(self.frame, text=name, anchor=W)
        right = Entry(self.frame, textvariable=value)
        left.grid(row=self.current_row, column=0, sticky=E + W, pady=0)
        right.grid(row=self.current_row, column=1, sticky=E + W, pady=0)

        self.current_row += 1

        return right, value

    def create_font_option(self, name, v):
        value = StringVar()
        value.set(v)
        value.trace("w", partial(self.on_font_variable, name))

        left = Label(self.frame, text=name, anchor=W)
        right = Button(self.frame, text=v, command=partial(self.on_font_button, name))
        left.grid(row=self.current_row, column=0, sticky=E + W, pady=0)
        right.grid(row=self.current_row, column=1, sticky=E + W, pady=0)

        self.current_row += 1

        return right, value

    def create_color_option(self, name, v):
        value = StringVar()
        value.set(v)
        value.trace("w", partial(self.on_color_variable, name))

        left = Label(self.frame, text=name, anchor=W)
        right = Button(self.frame, bg=value.get(), width=4, command=partial(self.on_color_button, name))
        left.grid(row=self.current_row, column=0, sticky=E + W, pady=0)
        right.grid(row=self.current_row, column=1, sticky=E + W, pady=0)

        self.current_row += 1

        return right, value

    def create_path_option(self, name, v):
        value = StringVar()

        value.set(v)
        value.trace("w", partial(self.on_path_variable, name))

        left = Label(self.frame, text=name, anchor=W)
        right = Button(self.frame, textvariable=value, command=partial(self.on_path_button, name))
        left.grid(row=self.current_row, column=0, sticky=E + W, pady=0)
        right.grid(row=self.current_row, column=1, sticky=E + W, pady=0)

        self.current_row += 1

        return right, value

    def on_int_variable(self, name, *args):
        c, v = self.controls[name]
        self.set_opt_int(name, v.get())

        self.apply_prop_changed()

    def on_text_variable(self, name, *args):
        c, v = self.controls[name]
        self.set_opt(name, v.get())

        self.apply_prop_changed()

    def on_font_variable(self, name, *args):
        c, v = self.controls[name]
        self.set_opt_font(name, v.get())
        c.configure(text=v.get())

        self.apply_prop_changed()

    def on_color_variable(self, name, *args):
        c, v = self.controls[name]
        self.set_opt(name, v.get())
        c.configure(bg=v.get())

        self.apply_prop_changed()

    def on_path_variable(self, name, *args):
        c, v = self.controls[name]
        self.set_opt(name, v.get())
        c.configure(text=v.get())

        self.apply_prop_changed()

    def update_control_value(self, t, name, value):
        print('update_control_value', t, name, value)
        c, v = self.controls[name]
        if t == 'int':
            v.set(value[2])
        elif t in ['text', 'font', 'color', 'path']:
            v.set(value)
        else:
            raise Exception('Unknown option type')

    def set_opt(self, n, v):
        for i, values in enumerate(self.settings):
            if values[0] == n:
                self.settings[i][2] = v
                return

    def set_opt_int(self, n, v):
        for i, values in enumerate(self.settings):
            if values[0] == n:
                self.settings[i][2][2] = v
                return

    def set_opt_font(self, n, v):
        for i, values in enumerate(self.settings):
            if values[0] == n:
                self.settings[i][2] = eval(v)
                return

    def get_opt(self, n):
        for i, values in enumerate(self.settings):
            if values[0] == n:
                return values[2]

    def on_font_button(self, name):
        s = self.get_opt(name)
        f = fontpicker.askChooseFont(self.root, defaultfont=font.Font(font=tuple(s)))
        if f:
            c, v = self.controls[name]
            v.set(f)

    def on_color_button(self, name):
        color = tkinter.colorchooser.askcolor(initialcolor=self.get_opt(name))[1]
        if color:
            c, v = self.controls[name]
            v.set(color)

    def on_path_button(self, name):
        file_path = tkinter.filedialog.askopenfilename(filetypes=(("Image files", "*.*"),))
        print(file_path)
        if not len(file_path):
            return
        try:
            image = Image.open(file_path)
            ImageTk.PhotoImage(image)
        except:
            tkinter.messagebox.showerror(title='Image load error',
                                         message='Invalid image, please choose a valid image file')
            return

        c, v = self.controls[name]
        v.set(os.path.abspath(file_path))

    def on_cancel(self):
        if self.dirty:
            if not tkinter.messagebox.askokcancel("Quit", "Do you want to quit without saving?"):
                return

            self.settings = copy.deepcopy(self.parent.settings)
            self.apply_prop_changed()

        self.parent.set_setting_button_enabled(True)
        self.root.destroy()

    def on_default(self):
        self.settings = copy.deepcopy(self.parent.def_settings)

        self.mute_notify = True
        for s in self.settings:
            n = s[0]
            t = s[1]
            v = s[2]
            self.update_control_value(t, n, v)
        self.mute_notify = False

        self.apply_prop_changed()

    def on_save(self):
        self.parent.settings = self.settings
        self.parent.write_config_file(USER_SETTING_FILE, self.parent.settings)
        self.parent.set_setting_button_enabled(True)
        self.root.destroy()

    def apply_prop_changed(self):
        if self.mute_notify:
            return

        self.dirty = True
        self.update_title()
        #print('on_prop_changed')
        self.parent.on_setting_changed(self.settings)

    def update_title(self):
        if self.dirty:
            self.root.title('Settings *')
        else:
            self.root.title('Settings')


class RollingApp(object):
    def __init__(self):
        self.setting_names = [('Background image path', 'path', '../image.jpg'),  # 0
                              ('Background color', 'color', '#000000'),  # 1
                              ('Welcome text', 'text', 'Lucky Draw!'),  # 2
                              ('Main text vertical position', 'int', [0, 200, 40]),  # 3
                              ('Main text font', 'font', ['Arial', '20', 'bold']),  # 4
                              ('Main text color', 'color', '#FF0000'),  # 5
                              ('Congratulations text', 'text', 'Congratulations!'),  # 6
                              ('Rolling button font', 'font', ['Arial', '20', 'bold']),  # 7
                              ('Rolling button foreground color', 'color', '#3A4BFF'),  # 8
                              ('Rolling button background color', 'color', '#FFC6BF'),  # 9
                              ('Begin rolling text', 'text', 'Begin!'),  # 10
                              ('End rolling text', 'text', 'Stop'),  # 11
                              ('Left visible letter count', 'int', [0, 50, 3]),  # 12
                              ('Right visible letter count', 'int', [0, 50, 4]), ]  # 13

        self.STATES = ('WELCOME', 'ROLLING', 'RESULT')

        self.state = self.STATES[0]

        self.winner_prefix = 'Winner is:'

        self.visible_left = 5

        self.visible_right = 5

        self._max_index = 0

        self.orig_candidates = []
        self.candidates = []

        self.lucky_index = -1

        # self.write_config_file(DEFAULT_SETTING_FILE, self.setting_names)
        # self.write_config_file(USER_SETTING_FILE, self.setting_names)

        self.settings = {}
        self.settings = self.load_settings()
        self.def_settings = self.load_def_settings()

        self._lucky_result = self.get_setting(2)

        self.stop = False

        self._draw_thread = None

        self.root = tkinter.tix.Tk()
        self.root.title('Lucky Draw Program')

        # position limits
        self.settings[3][2][1] = self.def_settings[3][2][1] = self.root.winfo_screenheight()

        self.use_mask = IntVar()

        self.to_full_screen()

        #self.root.attributes('-topmost', True)

        try:
            self.image = Image.open(self.get_setting(0))
            self.bg_image = ImageTk.PhotoImage(self.image)
        except:
            self.image = Image.open(DEF_BG_IMAGE)
            self.bg_image = ImageTk.PhotoImage(self.image)

        self.bg_label = Label(self.root, image=self.bg_image)

        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.info_label = Label(self.root, font=self.get_setting(4), fg='red')
        # self.info_label.pack(side=TOP, pady=self.get_setting(3)[2])
        self.info_label.place(x=self.root.winfo_screenwidth() / 2, y=self.get_setting(3)[2], anchor=CENTER)

        self.config_frame = Frame(self.root)

        self.check_box = Checkbutton(self.config_frame, text='Mask', variable=self.use_mask)
        self.check_box.pack(side=RIGHT)

        self._reset_button = Button(self.config_frame, relief=GROOVE, text='Reset', command=self.on_reset_button)
        self._reset_button.pack(side=RIGHT)

        self.setting_image = Image.open(SETTING_ICON)
        self.tk_setting_image = ImageTk.PhotoImage(self.setting_image)

        self._setting_button = Button(self.config_frame, relief=GROOVE, image=self.tk_setting_image, text='Settings',
                                      command=self.on_setting_button)

        self._setting_button.pack(side=RIGHT)

        self.config_frame.pack(side=BOTTOM)

        self.draw_button = Button(self.root, width=10, height=0, text=self.get_setting(7),
                                  command=self.on_begin_rolling_button)

        self.draw_button.pack(side=BOTTOM, pady=20)

        self.on_setting_changed(self.settings)

        self.root.bind("<Key>", self.on_key)

        self.root.protocol("WM_DELETE_WINDOW", self.on_delete)

    def rolling_update(self):
        if not self.stop:
            self.lucky_index = self.get_rand_index(self._max_index)
            self._lucky_result = self.candidates[self.lucky_index]

        self.update_info_display()

        self.root.after(10, self.rolling_update)

    def update_info_display(self):
        if self.state == self.STATES[0]:
            info = self.settings[2][2]
        elif self.state == self.STATES[1]:
            if self.use_mask.get():
                info = self.get_masked()
            else:
                info = self._lucky_result
        elif self.state == self.STATES[2]:
            if self.use_mask.get():
                info = self.winner_prefix + '\n' + self.get_masked()
            else:
                info = self.winner_prefix + '\n' + self._lucky_result
        else:
            raise Exception('Invalid state')

        self.info_label.configure(text=info)

    def on_setting_button(self):
        self.set_setting_button_enabled(False)
        SettingWindow(self)

    def on_reset_button(self):
        self.lucky_index = -1
        self.candidates = copy.copy(self.orig_candidates)
        self._max_index = len(self.candidates) - 1

    def get_setting(self, index):
        return self.settings[index][2]

    @staticmethod
    def write_config_file(name, settings):
        with open(name, 'wt+', encoding='utf-8') as out:
            json.dump(settings, out, indent='\t', ensure_ascii=False)

    def settings_valid(self, settings):
        for n in self.setting_names:
            valid = False
            for s in settings:
                if s[0] == n[0]:
                    valid = True
                    break

            if not valid:
                return False

        return True

    def load_config_file(self, name):
        with open(name, 'rt', encoding='utf-8') as config:
            settings = json.load(config)

            # print(settings)

            # check valid
            if self.settings_valid(settings):
                return settings

        raise Exception('invalid user config')

    def load_settings(self):
        try:
            settings = self.load_config_file(USER_SETTING_FILE)
            return settings
        except:
            try:
                settings = self.load_config_file(DEFAULT_SETTING_FILE)
                return settings
            except:
                raise Exception('Config files broken')

    def load_def_settings(self):
        try:
            settings = self.load_config_file(DEFAULT_SETTING_FILE)
            return settings
        except:
            raise Exception('Config files broken')

    def to_full_screen(self):
        # full screen
        self.root.overrideredirect(1)
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.root.geometry("%dx%d+0+0" % (w, h))

    def on_delete(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

    def on_key(self, event):
        if event.keysym == 'space':
            self.draw_button.invoke()
        elif event.keysym == 'Escape':
            self.on_delete()

    @staticmethod
    def is_valid_line(line):
        if not len(line):
            return False
        return True

    def read_candidates_list(self, list_name):
        self.candidates = []
        with open(list_name, 'r', encoding='utf-8') as in_file:
            for line in in_file.readlines():
                line = line.strip(' \n\r')
                line = line.strip('\ufeff') # BOM
                if self.is_valid_line(line):
                    self.candidates.append(line)

            #print(self.candidates)

            self.orig_candidates = copy.copy(self.candidates)
            self.lucky_index = -1
            self._max_index = len(self.candidates) - 1
            print('max index is:', self._max_index)

    def run(self):
        print('Starting the program')
        random.seed()
        print('Random seed set')
        self.read_candidates_list('..\LIST.txt')

        self.rolling_update()

        print('UI main loop')
        self.root.mainloop()

    def update_info(self):
        while True:
            time.sleep(ROLLING_INTERVAL)
            if self.state == self.STATES[0]:
                continue
            if self.state == self.STATES[1]:
                if self.use_mask.get():
                    info = self.get_masked()
                else:
                    info = self._lucky_result
            elif self.state == self.STATES[2]:
                if self.use_mask.get():
                    info = self.winner_prefix + '\n' + self.get_masked()
                else:
                    info = self.winner_prefix + '\n' + self._lucky_result
            else:
                raise Exception('Invalid state')

            self.info_label.configure(text=info)

    def remove_winner_candidate(self):
        self.candidates.pop(self.lucky_index)
        self._max_index = len(self.candidates) - 1

    def on_begin_rolling_button(self):
        self.state = self.STATES[1]

        if not len(self.candidates):
            tkinter.messagebox.showwarning('No more candidates',
                                           "No more candidates! Please use the reset button to reset.")
            return

        self.stop = False

        self.draw_button.configure(text=self.get_setting(11))
        self.draw_button.configure(command=self.on_end_rolling_button)

    def on_end_rolling_button(self):
        self.state = self.STATES[2]

        self.stop = True

        self.remove_winner_candidate()

        self.draw_button.configure(text=self.get_setting(10))
        self.draw_button.configure(command=self.on_begin_rolling_button)

    @staticmethod
    def get_rand_index(max_index):
        r = random.randint(0, max_index)
        return r

    def set_setting_button_enabled(self, enabled):
        if enabled:
            self._setting_button.configure(state=NORMAL)
        else:
            self._setting_button.configure(state=DISABLED)

    def get_masked(self):
        total = len(self._lucky_result)
        if self.visible_left + self.visible_right >= total:
            return self._lucky_result

        left = self._lucky_result[0:self.visible_left]
        if not self.visible_right:
            right = ''
        else:
            right = self._lucky_result[-self.visible_right:]

        mask_count = total - self.visible_left - self.visible_right
        masked = left + mask_count * '*' + right
        return masked

    def on_setting_changed(self, settings):
        try:
            self.image = Image.open(settings[0][2])
            self.bg_image = ImageTk.PhotoImage(self.image)
        except:
            self.image = Image.open(DEF_BG_IMAGE)
            self.bg_image = ImageTk.PhotoImage(self.image)

        self.bg_label.configure(image=self.bg_image, bg=settings[1][2])

        self.info_label.configure(font=settings[4][2], fg=settings[5][2], bg=settings[1][2])
        self.winner_prefix = settings[6][2]

        self.draw_button.configure(font=settings[7][2], fg=settings[8][2], bg=settings[9][2])

        if self.state == self.STATES[0]:
            self.info_label['text'] = settings[2][2]
            self.draw_button.configure(text=settings[10][2])
        elif self.state == self.STATES[1]:
            self.draw_button.configure(text=settings[11][2])
        elif self.state == self.STATES[2]:
            self.draw_button.configure(text=settings[10][2])
        else:
            raise Exception('Invalid state')

        self.visible_left = settings[12][2][2]
        self.visible_right = settings[13][2][2]

        self.info_label.place(x=self.root.winfo_screenwidth() / 2, y=settings[3][2][2], anchor=CENTER)


def main():
    try:
        app = RollingApp()
        app.run()
    except:
        tkinter.messagebox.showerror('Application Error', traceback.format_exc())


if __name__ == "__main__":
    main()
