## code based on http://tkinter.unpythonic.net/wiki/FontChooser


import tkinter.tix
import tkinter.simpledialog
import tkinter.font


class FontChooser(tkinter.simpledialog.Dialog):
    BASIC = 1
    ALL = 2

    def __init__(self, parent, defaultfont=None, showstyles=None):
        self._family = tkinter.tix.StringVar(value='Ariel')
        self._sizeString = tkinter.tix.StringVar(value='12')
        self._weight = tkinter.tix.StringVar(value=tkinter.font.NORMAL)
        self._slant = tkinter.tix.StringVar(value=tkinter.font.ROMAN)
        self._isUnderline = tkinter.tix.BooleanVar(value=False)
        self._isOverstrike = tkinter.tix.BooleanVar(value=False)

        if defaultfont:
            self._initialize(defaultfont)

        self._currentFont = tkinter.font.Font(font=self.getFontTuple())

        self._showStyles = showstyles

        self.sampleText = None

        tkinter.simpledialog.Dialog.__init__(self, parent, 'Font Chooser')

    def _initialize(self, aFont):
        if not isinstance(aFont, tkinter.font.Font):
            aFont = tkinter.font.Font(font=aFont)

        fontOpts = aFont.actual()

        self._family.set(fontOpts['family'])
        self._sizeString.set(fontOpts['size'])
        self._weight.set(fontOpts['weight'])
        self._slant.set(fontOpts['slant'])
        self._isUnderline.set(fontOpts['underline'])
        self._isOverstrike.set(fontOpts['overstrike'])

    def body(self, master):
        theRow = 0

        tkinter.tix.Label(master, text="Font Family").grid(row=theRow, column=0)
        tkinter.tix.Label(master, text="Font Size").grid(row=theRow, column=2)

        theRow += 1

        # Font Families
        fontList = tkinter.tix.ComboBox(master, command=self.selectionChanged, dropdown=False, editable=False,
                                        selectmode=tkinter.tix.IMMEDIATE, variable=self._family)
        fontList.grid(row=theRow, column=0, columnspan=2,
                      sticky=tkinter.tix.N + tkinter.tix.S + tkinter.tix.E + tkinter.tix.W, padx=10)
        first = None
        familyList = list(tkinter.font.families())
        familyList.sort()
        last = -1
        select = -1
        for family in familyList:
            if family[0] == '@':
                continue
            if first is None:
                first = family

            fontList.insert(tkinter.tix.END, family)

            last += 1
            if self._family.get() == family:
                select = last

        # fontList.configure(value=first)
        if select != -1:
            fontList.pick(select)
        else:
            fontList.pick(last)

        # Font Sizes
        sizeList = tkinter.tix.ComboBox(master, command=self.selectionChanged, dropdown=False, editable=False,
                                        selectmode=tkinter.tix.IMMEDIATE, variable=self._sizeString)
        sizeList.grid(row=theRow, column=2, columnspan=2,
                      sticky=tkinter.tix.N + tkinter.tix.S + tkinter.tix.E + tkinter.tix.W, padx=10)

        last = -1
        select = -1
        for size in range(6, 200):
            sizeList.insert(tkinter.tix.END, '%d' % size)
            last += 1
            if self._sizeString.get() == str(size):
                select = last

        # sizeList.configure(value='9')
        if select != -1:
            sizeList.pick(select)
        else:
            sizeList.pick(last)

        # Styles
        if self._showStyles is not None:
            theRow += 1

            if self._showStyles in (FontChooser.ALL, FontChooser.BASIC):
                tkinter.tix.Label(master, text='Styles', anchor=tkinter.tix.W).grid(row=theRow, column=0, pady=10,
                                                                                    sticky=tkinter.tix.W)

                theRow += 1

                tkinter.tix.Checkbutton(master, text="bold", command=self.selectionChanged, offvalue='normal',
                                        onvalue='bold', variable=self._weight).grid(row=theRow, column=0)
                tkinter.tix.Checkbutton(master, text="italic", command=self.selectionChanged, offvalue='roman',
                                        onvalue='italic', variable=self._slant).grid(row=theRow, column=1)

            if self._showStyles == FontChooser.ALL:
                tkinter.tix.Checkbutton(master, text="underline", command=self.selectionChanged, offvalue=False,
                                        onvalue=True, variable=self._isUnderline).grid(row=theRow, column=2)
                tkinter.tix.Checkbutton(master, text="overstrike", command=self.selectionChanged, offvalue=False,
                                        onvalue=True, variable=self._isOverstrike).grid(row=theRow, column=3)

        # Sample Text
        theRow += 1

        tkinter.tix.Label(master, text='Sample Text', anchor=tkinter.tix.W).grid(row=theRow, column=0, pady=10,
                                                                                 sticky=tkinter.tix.W)

        theRow += 1

        self.sampleText = tkinter.tix.Text(master, height=11, width=70)
        self.sampleText.insert(tkinter.tix.INSERT,
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz', 'fontStyle')
        self.sampleText.config(state=tkinter.tix.DISABLED)
        self.sampleText.tag_config('fontStyle', font=self._currentFont)
        self.sampleText.grid(row=theRow, column=0, columnspan=4, padx=10)

    def apply(self):
        self.result = self.getFontTuple()

    def selectionChanged(self, something=None):
        self._currentFont.configure(family=self._family.get(), size=self._sizeString.get(),
                                    weight=self._weight.get(), slant=self._slant.get(),
                                    underline=self._isUnderline.get(),
                                    overstrike=self._isOverstrike.get())

        if self.sampleText:
            self.sampleText.tag_config('fontStyle', font=self._currentFont)

    def getFontTuple(self):
        family = self._family.get()
        size = int(self._sizeString.get())

        styleList = []
        if self._weight.get() == tkinter.font.BOLD:
            styleList.append('bold')
        if self._slant.get() == tkinter.font.ITALIC:
            styleList.append('italic')
        if self._isUnderline.get():
            styleList.append('underline')
        if self._isOverstrike.get():
            styleList.append('overstrike')

        if len(styleList) == 0:
            return family, size
        else:
            return family, size, ' '.join(styleList)


def askChooseFont(parent, defaultfont=None, showstyles=FontChooser.ALL):
    return FontChooser(parent, defaultfont=defaultfont, showstyles=showstyles).result


if __name__ == '__main__':
    root = tkinter.tix.Tk()
    font = askChooseFont(root)

    if font:
        print(font)
