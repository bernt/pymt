from pymt.ui.widgets.widget import MTWidget

class MTAbstractLayout(MTWidget):
    '''Abstract layout. Base class used to implement layout.

    :Events:
        `on_layout`
            Fired when layout function have been called
        `on_content_resize`
            Fired when content_width or content_height have changed
    '''

    def __init__(self, **kwargs):
        if self.__class__ == MTAbstractLayout:
            raise NotImplementedError, 'class MTAbstractLayout is abstract'
        super(MTAbstractLayout, self).__init__(**kwargs)
        self.register_event_type('on_layout')
        self.register_event_type('on_content_resize')
        self._content_height = 0
        self._content_width  = 0

    def _set_content_width(self, w):
        if self._content_width == w:
            return
        self._content_width = w
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_width(self):
        return self._content_width
    content_width = property(_get_content_width, _set_content_width)

    def _set_content_height(self, w):
        if self._content_height == w:
            return
        self._content_height = w
        self.dispatch_event('on_content_resize', self._content_height, self._content_height)
    def _get_content_height(self):
        return self._content_height
    content_height = property(_get_content_height, _set_content_height)

    def _set_content_size(self, size):
        w, h = size
        if self._content_width == w and self._content_height == h:
            return
        self._content_width = w
        self._content_height = h
        self.dispatch_event('on_content_resize', self._content_width, self._content_height)
    def _get_content_size(self):
        return (self.content_width, self.content_height)
    content_size = property(_get_content_size, _set_content_size)

    def add_widget(self, widget, do_layout=True):
        super(MTAbstractLayout, self).add_widget(widget)
        if do_layout:
            self.do_layout()

    def do_layout(self):
        pass

    def get_parent_layout(self):
        return self

    def on_layout(self):
        pass

    def on_content_resize(self, w, h):
        if self.parent:
            layout = self.parent.get_parent_layout()
            if layout:
                layout.do_layout()


class MTBoxLayout(MTAbstractLayout):
    '''Box layout can arrange item in horizontal or vertical orientation.

    :Parameters:
        `padding` : int, default to 0
            Padding between the border and content
        `spacing` : int, default to 1
            Spacing between widgets
        `orientation` : str, default is 'horizontal'
            Orientation of widget inside layout, can be `horizontal` or `vertical`
        `uniform_width` : bool, default to False
            Try to have same width for all children
        `uniform_height` : bool, default to False
            Try to have same height for all children
        `invert_x` : bool, default to False
            Invert X axis
        `invert_y` : bool, default to False
            Invert Y axis
    '''

    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('spacing', 1)
        kwargs.setdefault('padding', 0)
        kwargs.setdefault('uniform_width', False)
        kwargs.setdefault('uniform_height', False)
        kwargs.setdefault('invert_x', False)
        kwargs.setdefault('invert_y', False)

        if kwargs.get('orientation') not in ['horizontal', 'vertical']:
            raise Exception('Invalid orientation, only horizontal/vertical are supported')

        super(MTBoxLayout, self).__init__(**kwargs)

        self.spacing        = kwargs.get('spacing')
        self.padding        = kwargs.get('padding')
        self.orientation    = kwargs.get('orientation')
        self.uniform_width  = kwargs.get('uniform_width')
        self.uniform_height = kwargs.get('uniform_height')
        self.invert_x       = kwargs.get('invert_x')
        self.invert_y       = kwargs.get('invert_y')

    def add_widget(self, w):
        super(MTBoxLayout, self).add_widget(w)
        self.do_layout()

    def on_move(self, x, y):
        self.do_layout()
        super(MTBoxLayout, self).on_move(x, y)

    def do_layout(self):
        '''Recalculate position for every subwidget, fire
        on_layout when finished. If content size have changed,
        fire on_content_resize too. Uniform width/height are handled
        after on_content_resize.
        '''
        max_width = max_height = 0
        current_width = current_height = 0
        for w in self.children:
            try:
                if w.height > max_height:
                    max_height = w.height
                if w.width > max_width:
                    max_width = w.width
                if self.orientation == 'horizontal':
                    if current_width > 0:
                        current_width += self.spacing
                    current_width += w.width
                elif self.orientation == 'vertical':
                    if current_height > 0:
                        current_height += self.spacing
                    current_height += w.height
            except:
                pass

        # uniform
        if self.uniform_width:
            for w in self.children:
                w.width = max_width
            if self.orientation == 'horizontal':
                current_width = (len(self.children) - 1) * (max_width + self.spacing)
        if self.uniform_height:
            for w in self.children:
                w.height = max_height
            if self.orientation == 'vertical':
                current_height = (len(self.children) - 1) * (max_height + self.spacing)

        # adjust current width/height
        if self.orientation == 'horizontal':
            current_height = max_height
        elif self.orientation == 'vertical':
            current_width = max_width

        # apply double padding
        current_width += self.padding * 2
        current_height += self.padding * 2

        # reposition
        cur_x = self.x + self.padding
        cur_y = self.y + self.padding
        for w in self.children:
            try:
                if self.invert_x:
                    w.y = self.x + current_width - w.width - (cur_x - self.x)
                else:
                    w.x = cur_x
                if self.invert_y:
                    w.y = self.y + current_height - w.height - (cur_y - self.y)
                else:
                    w.y = cur_y
                if self.orientation == 'horizontal':
                    cur_x += w.width + self.spacing
                elif self.orientation == 'vertical':
                    cur_y += w.height + self.spacing
            except:
                pass

        self.content_size = (current_width, current_height)

        # XXX make it optionnal, in 0.2
        self.size = (self.content_width, self.content_height)

        # we just do a layout, dispatch event
        self.dispatch_event('on_layout')

