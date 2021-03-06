# Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_MK3\TrackControlComponent.py
# Compiled at: 2017-09-17 14:37:13
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from MidiMap import *
from TrackButtonHandler import TrackButtonHandler
from PadColorButton import IndexedButton
from _Framework.InputControlElement import MIDI_CC_TYPE
from MaschineButtonMatrix import IndexButtonMatrix
from Constants import *
COLORLIST = [colorOnOff(CI_WARM_YELLOW),
 colorOnOff(CI_BLUE),
 colorOnOff(CI_RED),
 colorOnOff(CI_CYAN),
 colorOnOff(CI_PURPLE),
 colorOnOff(CI_LIGHT_ORANGE),
 colorOnOff(CI_OFF),
 colorOnOff(CI_OFF)]

class TrackControlComponent(CompoundComponent):

    def __init__(self, session, track_editor, *a, **k):
        super(TrackControlComponent, self).__init__(*a, **k)
        self._bmatrix = IndexButtonMatrix(100, name='Track_Select_Button_Matrix')
        self._buttons = [ self.create_buttons(index, track_editor) for index in range(8) ]
        self._bmatrix.add_row(tuple([ trackButtonHandler._button for trackButtonHandler in self._buttons ]))
        self.__session = session
        self.assign_buttons = self._assign_track_buttons
        self._run_index = -1
        self._mode = SEL_MODE_SELECT
        self._handle_selection.subject = self.song().view
        self._tracks_change.subject = self.song()
        self._visible_changed.subject = self.song()
        self._prev_mode_button = None
        self._prev_mode = None
        return

    @subject_slot('tracks')
    def _tracks_change(self):
        self._assign_track_buttons()

    @subject_slot('visible_tracks')
    def _visible_changed(self):
        self._assign_track_buttons()

    def refresh_state(self):
        for button in self._buttons:
            button.reset()

    def create_buttons(self, index, track_editor):
        button = IndexedButton(True, MIDI_CC_TYPE, index + 100, 0, COLORLIST[0])
        button.index = index
        return TrackButtonHandler(index, button, track_editor)

    def mode_changed(self, newmode):
        self.assign_buttons()

    def gettrack(self, index, off):
        tracks = self.song().visible_tracks
        if index + off < len(tracks):
            return tracks[index + off]
        return

    @subject_slot('selected_track')
    def _handle_selection(self):
        if self._mode == SEL_MODE_SELECT:
            for i in range(8):
                self._buttons[i].update_value()

    def notify(self, blinking_state):
        if self._bmatrix.grabbed:
            return
        if self._mode == SEL_MODE_STOP:
            for button in self._buttons:
                button.update_value(blinking_state)

    @property
    def mode(self):
        return self._mode

    def trigger_solo(self, button, value=None):
        if value == None:
            if self._mode == SEL_MODE_SOLO:
                button.set_display_value(0, True)
                self._mode = SEL_MODE_SELECT
                self._assign_track_buttons()
                self._prev_mode_button = None
            else:
                self._mode = SEL_MODE_SOLO
                if self._prev_mode_button:
                    self._prev_mode_button.set_display_value(0, True)
                button.set_display_value(127, True)
                self._assign_track_buttons()
                self._prev_mode_button = button
                self._prev_mode = SEL_MODE_SOLO
        else:
            button.set_display_value(value, True)
            if value == 0:
                self._mode = SEL_MODE_SELECT
                self._assign_track_buttons()
                self._prev_mode_button = None
            else:
                if self._mode != SEL_MODE_SOLO:
                    self._mode = SEL_MODE_SOLO
                    if self._prev_mode_button:
                        self._prev_mode_button.set_display_value(0, True)
                    button.set_display_value(127, True)
                    self._assign_track_buttons()
                    self._prev_mode_button = button
                    self._prev_mode = SEL_MODE_SOLO
        return

    def trigger_mute(self, button, value=None):
        if value == None:
            if self._mode == SEL_MODE_MUTE:
                button.set_display_value(0, True)
                self._mode = SEL_MODE_SELECT
                self._assign_track_buttons()
                self._prev_mode_button = None
            else:
                self._mode = SEL_MODE_MUTE
                if self._prev_mode_button:
                    self._prev_mode_button.set_display_value(0, True)
                button.set_display_value(127, True)
                self._assign_track_buttons()
                self._prev_mode_button = button
                self._prev_mode = SEL_MODE_MUTE
        else:
            button.set_display_value(value, True)
            if value == 0:
                self._mode = SEL_MODE_SELECT
                self._assign_track_buttons()
                self._prev_mode_button = None
            else:
                if self._mode != SEL_MODE_MUTE:
                    self._mode = SEL_MODE_MUTE
                    if self._prev_mode_button:
                        self._prev_mode_button.set_display_value(0, True)
                    self._assign_track_buttons()
                    self._prev_mode_button = button
                    self._prev_mode = SEL_MODE_MUTE
        return

    def trigger_stop(self):
        self._mode = SEL_MODE_STOP
        self._assign_track_buttons()

    def trigger_to_prev(self):
        if self._prev_mode_button and self._prev_mode:
            self._mode = self._prev_mode
            self._prev_mode_button.set_display_value(127, True)
            self._assign_track_buttons()
        else:
            self._mode = SEL_MODE_SELECT
            self._assign_track_buttons()
            self._prev_mode_button = None
        return

    def trigger_arm(self, button):
        if self._mode == SEL_MODE_ARM:
            button.set_display_value(0, True)
            self._mode = SEL_MODE_SELECT
            self._assign_track_buttons()
            self._prev_mode_button = None
        else:
            self._mode = SEL_MODE_ARM
            if self._prev_mode_button:
                self._prev_mode_button.set_display_value(0, True)
            button.set_display_value(127, True)
            self._assign_track_buttons()
            self._prev_mode_button = button
        return

    def _assign_track_buttons(self):
        trackoff = self.__session.track_offset()
        for i in range(8):
            track = self.gettrack(i, trackoff)
            button = self._buttons[i]
            if track is None:
                button.disable(self.empty_action)
            else:
                if self._mode == SEL_MODE_MUTE:
                    button.assign_mute(track)
                if self._mode == SEL_MODE_SOLO:
                    button.assign_solo(track)
                if self._mode == SEL_MODE_ARM:
                    button.assign_arm(track)
                if self._mode == SEL_MODE_SELECT:
                    button.assign_select(track)
                if self._mode == SEL_MODE_STOP:
                    button.assign_stop(track)
                if self._mode == SEL_MODE_XFADE:
                    button.assign_xfade(track)
                button.update_value(0)

        return

    def empty_action(self):
        if self._mode == SEL_MODE_SELECT:
            if self.canonical_parent.is_shift_down():
                self.song().create_audio_track(-1)
            elif self.canonical_parent.is_select_down():
                self.song().create_audio_track(-1)
            else:
                self.song().create_midi_track(-1)

    def disconnect(self):
        super(TrackControlComponent, self).disconnect()
        for button in self._buttons:
            button.disable()
