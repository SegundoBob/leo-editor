# @+leo-ver=5-thin
# @+node:swot.20260222193522.1: * @file /Users/swot/app/leo-editor/leo/plugins/body_style.py
# @@language python
# @+others
# @+node:swot.20260222193522.2: ** import
from leo.core import leoGlobals as g
from PyQt6.QtGui import QTextBlockFormat, QTextCursor, QFont, QTextCharFormat
from PyQt6.QtCore import QTimer

# @+node:swot.20260222193522.3: ** var
try:
    c
except NameError:
    c = None


# @+node:swot.20260222193522.4: ** def init
def init():
    g.registerHandler("open2", on_window_init)
    g.registerHandler("start2", on_window_init)

    if g.app.commanders():
        for existing_c in g.app.commanders():
            on_window_init("reload", {"c": existing_c})

    g.es("Body Style Plugin loaded (Snapshot Timing Fixed).")
    return True


# @+node:swot.20260222193522.5: ** def on_window_init
def on_window_init(tag, keywords):
    c = keywords.get("c")
    if not c:
        return
    if hasattr(c, "_body_styler"):
        c._body_styler.apply_style()
        return
    c._body_styler = BodyStyleController(c)


# @+node:swot.20260222193522.6: ** class BodyStyleController
class BodyStyleController:
    # @+others
    # @+node:swot.20260222193522.7: *3* def __init__
    def __init__(self, c):
        self.c = c
        self._is_formatting = False

        # State tracking for Undo/Redo operations
        self._is_undoing = False
        self._pre_undo_scroll_val = 0
        self._pre_undo_was_at_bottom = False

        g.registerHandler("select1", self.on_select)
        g.registerHandler("command1", self.on_command1)
        g.registerHandler("command2", self.on_command2)

        self._unfreeze_timer = QTimer()
        self._unfreeze_timer.setSingleShot(True)
        self._unfreeze_timer.timeout.connect(self._force_unfreeze)

        QTimer.singleShot(100, self.setup_qt_signals)

    def _freeze_ui(self):
        """Freeze UI updates to prevent flashing"""
        editor = self.get_editor()
        if editor:
            editor.setUpdatesEnabled(False)
            if editor.viewport():
                editor.viewport().setUpdatesEnabled(False)

    def _force_unfreeze(self):
        """Unfreeze UI and reset states"""
        self._is_undoing = False
        editor = self.get_editor()
        if editor:
            editor.setUpdatesEnabled(True)
            if editor.viewport():
                editor.viewport().setUpdatesEnabled(True)

    # @+node:swot.20260222193522.8: *3* def get_config
    def get_config(self):
        conf = {
            "family": "JetBrains Mono",
            "size": 16,
            "line_height": 125,
            "line_height_type": 1,
            "letter_spacing": 105,
        }
        data = self.c.config.getData("body-style-settings")
        if data:
            for line in data:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = [x.strip() for x in line.split("=", 1)]
                    if key in conf:
                        if key == "family":
                            conf[key] = val
                        else:
                            try:
                                conf[key] = int(val)
                            except ValueError:
                                pass
        return conf

    # @+node:swot.20260222193522.9: *3* def on_select
    def on_select(self, tag, keywords):
        if keywords.get("c") != self.c:
            return
        QTimer.singleShot(0, lambda: self.apply_style(None, 0))

    # @+node:swot.20260222193522.10: *3* def on_command1
    def on_command1(self, tag, keywords):
        """Before command: Snapshot scrollbar BEFORE the document shrinks"""
        if keywords.get("c") == self.c:
            cmd = (keywords.get("label") or keywords.get("commandName") or "").lower()
            if "undo" in cmd or "redo" in cmd:
                self._is_undoing = True
                editor = self.get_editor()
                if editor and editor.verticalScrollBar():
                    v_bar = editor.verticalScrollBar()
                    self._pre_undo_scroll_val = v_bar.value()
                    self._pre_undo_was_at_bottom = v_bar.maximum() - v_bar.value() <= 2

                self._freeze_ui()
                self._unfreeze_timer.start(200)

    # @+node:swot.20260222193522.11: *3* def on_command2
    def on_command2(self, tag, keywords):
        """After command: Re-apply style and unfreeze"""
        if keywords.get("c") == self.c:
            cmd = (keywords.get("label") or keywords.get("commandName") or "").lower()
            if "undo" in cmd or "redo" in cmd:
                self.apply_style(None, 0)
                self._force_unfreeze()
                self._unfreeze_timer.stop()

    # @+node:swot.20260222193522.12: *3* def setup_qt_signals
    def setup_qt_signals(self):
        editor = self.get_editor()
        if not editor or not editor.document():
            return
        doc = editor.document()
        try:
            doc.contentsChange.disconnect(self.on_contents_change)
        except Exception:
            pass
        doc.contentsChange.connect(self.on_contents_change)
        self.apply_style(None, 0)

    # @+node:swot.20260222193522.13: *3* def on_contents_change
    def on_contents_change(self, position, charsRemoved, charsAdded):
        if self._is_formatting:
            return

        if charsAdded > 0:
            QTimer.singleShot(
                0, lambda p=position, l=charsAdded: self.apply_style(p, l)
            )
        elif charsRemoved > 0:
            QTimer.singleShot(0, lambda p=position: self.apply_style(p, 0))

    # @+node:swot.20260222193522.14: *3* def get_editor
    def get_editor(self):
        try:
            return self.c.frame.body.wrapper.widget
        except AttributeError:
            return None

    # @+node:swot.20260222193522.15: *3* def apply_style
    def apply_style(self, position=None, length=0):
        if self._is_formatting:
            return
        self._is_formatting = True

        try:
            editor = self.get_editor()
            if not editor or not editor.document():
                return
            doc = editor.document()
            config = self.get_config()

            current_font = editor.font()
            if (
                current_font.family() != config["family"]
                or current_font.pointSize() != config["size"]
            ):
                font = QFont(config["family"])
                font.setPointSize(config["size"])
                font.setLetterSpacing(
                    QFont.SpacingType.PercentageSpacing, config["letter_spacing"]
                )
                editor.setFont(font)
                doc.setDefaultFont(font)

            self._apply_formats(editor, doc, config, position, length)
        finally:
            self._is_formatting = False

    # @+node:swot.20260222193522.16: *3* def _apply_formats
    def _apply_formats(self, editor, doc, config, position=None, length=0):
        v_scrollbar = editor.verticalScrollBar()

        # Use the pre-undo snapshot if we are undoing, otherwise read current state
        if self._is_undoing:
            saved_scroll_val = self._pre_undo_scroll_val
            was_at_bottom = self._pre_undo_was_at_bottom
        else:
            saved_scroll_val = v_scrollbar.value() if v_scrollbar else 0
            was_at_bottom = False
            if v_scrollbar:
                was_at_bottom = v_scrollbar.maximum() - saved_scroll_val <= 2

        editor.blockSignals(True)
        doc.blockSignals(True)

        cursor = QTextCursor(doc)

        try:
            if position is not None:
                max_pos = max(0, doc.characterCount() - 1)
                safe_pos = min(position, max_pos)
                cursor.setPosition(safe_pos)

                if length > 0:
                    safe_length = min(length, max_pos - safe_pos)
                    cursor.setPosition(
                        safe_pos + safe_length, QTextCursor.MoveMode.KeepAnchor
                    )
                else:
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            else:
                cursor.select(QTextCursor.SelectionType.Document)

            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(config["line_height"], config["line_height_type"])
            cursor.mergeBlockFormat(block_fmt)

            char_fmt = QTextCharFormat()
            char_fmt.setFontFamily(config["family"])
            char_fmt.setFontPointSize(config["size"])
            char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
            char_fmt.setFontLetterSpacing(config["letter_spacing"])
            cursor.mergeCharFormat(char_fmt)
        finally:
            doc.blockSignals(False)
            editor.blockSignals(False)

            if v_scrollbar:
                if was_at_bottom:
                    v_scrollbar.setValue(v_scrollbar.maximum())
                else:
                    v_scrollbar.setValue(min(saved_scroll_val, v_scrollbar.maximum()))

                # Retain the 20ms delay here just in case Qt needs a tick to finish rendering
                if was_at_bottom:
                    QTimer.singleShot(
                        20, lambda: v_scrollbar.setValue(v_scrollbar.maximum())
                    )
                else:
                    QTimer.singleShot(
                        20,
                        lambda: v_scrollbar.setValue(
                            min(saved_scroll_val, v_scrollbar.maximum())
                        ),
                    )

    # @-others


# @-others
# @-leo
