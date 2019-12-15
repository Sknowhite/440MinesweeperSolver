from tkinter import *


class BoardButton(Button):
    def __init__(self, x, y, frame, images, value=0):

        self.img_blank = images['blank']
        self.img_mine = images['mine']
        self.img_hit_mine = images['hit_mine']
        self.img_flag = images['flag']
        self.img_wrong = images['wrong']
        self.img_no = images['no']

        super(BoardButton, self).__init__(frame, image=self.img_blank,
                                          background='#181a19', foreground='#d10232', highlightbackground='#000000')
        self._x = x
        self._y = y
        self._value = value
        self.is_a_mine = False
        self.is_visible = False
        self.is_flagged = False
        if value == -1:
            self.is_a_mine = True

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._value == -1:
            self.is_a_mine = True

    def flag(self):
        if not self.is_visible:
            if self.is_flagged:
                self.config(image=self.img_blank)
            else:
                self.config(image=self.img_flag)
            self.is_flagged = not self.is_flagged

    def is_flag(self):
        return self.is_flagged

    def place_mine(self):
        if not self.is_a_mine:
            self._value = -1
            self.is_a_mine = True
            return True
        return False

    def is_mine(self):
        return self.is_a_mine

    def show(self):
        if not self.is_visible and not self.is_flagged:
            self.is_visible = True
            if self.is_mine():
                self.config(image=self.img_mine)
            else:
                self.config(image=self.img_no[self._value])

    def is_show(self):
        return self.is_visible

    def reset(self):
        self._value = 0
        self.is_a_mine = False
        self.is_visible = False
        self.is_flagged = False
        self.show_blank()

    def show_wrong_flag(self):
        self.config(image=self.img_wrong)

    def show_hit_mine(self):
        self.config(image=self.img_hit_mine)

    def show_blank(self):
        self.config(image=self.img_blank)
