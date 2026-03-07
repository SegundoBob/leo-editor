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

    g.es("Body Style Plugin loaded (Zoom Compatibility Fixed).")
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
        self._initial_size_set = False  # Track if initial config size was applied

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
        """Freeze UI updates to prevent flashing during formatting"""
        editor = self.get_editor()
        if editor:
            editor.setUpdatesEnabled(False)
            if editor.viewport():
                editor.viewport().setUpdatesEnabled(False)

    def _force_unfreeze(self):
        """Restore UI updates and reset undo flag"""
        self._is_undoing = False
        editor = self.get_editor()
        if editor:
            editor.setUpdatesEnabled(True)
            if editor.viewport():
                editor.viewport().setUpdatesEnabled(True)

    # @+node:swot.20260222193522.8: *3* def get_config
    def get_config(self):
        """Load settings from @data body-style-settings"""
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
        """Refresh full document style when switching nodes"""
        if keywords.get("c") != self.c:
            return
        QTimer.singleShot(0, lambda: self.apply_style(None, 0))

    # @+node:swot.20260222193522.10: *3* def on_command1
    def on_command1(self, tag, keywords):
        """Snapshot scrollbar and freeze UI before native Undo/Redo occurs"""
        if keywords.get("c") == self.c:
            cmd = (keywords.get("label") or keywords.get("commandName") or "").lower()
            if "undo" in cmd or "redo" in cmd:
                self._is_undoing = True
                editor = self.get_editor()
                if editor and editor.verticalScrollBar():
                    v_bar = editor.verticalScrollBar()
                    self._pre_undo_scroll_val = v_bar.value()
                    # Check if scrollbar is at the bottom with 2px tolerance
                    self._pre_undo_was_at_bottom = v_bar.maximum() - v_bar.value() <= 2

                self._freeze_ui()
                # Safety timeout to prevent permanent UI freeze
                self._unfreeze_timer.start(200)

    # @+node:swot.20260222193522.11: *3* def on_command2
    def on_command2(self, tag, keywords):
        """Re-apply style and unfreeze UI after command completes"""
        if keywords.get("c") == self.c:
            cmd = (keywords.get("label") or keywords.get("commandName") or "").lower()
            if "undo" in cmd or "redo" in cmd:
                self.apply_style(None, 0)
                self._force_unfreeze()
                self._unfreeze_timer.stop()

    # @+node:swot.20260222193522.12: *3* def setup_qt_signals
    def setup_qt_signals(self):
        """Establish connection to Qt document signals"""
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
        """Apply incremental style updates on text change"""
        # Block updates during Undo/Redo to prevent cursor reset issues
        if self._is_formatting or self._is_undoing:
            return

        if charsAdded > 0:
            QTimer.singleShot(
                0, lambda p=position, l=charsAdded: self.apply_style(p, l)
            )
        elif charsRemoved > 0:
            QTimer.singleShot(0, lambda p=position: self.apply_style(p, 0))

    # @+node:swot.20260222193522.14: *3* def get_editor
    def get_editor(self):
        """Safely retrieve the Qt editor widget"""
        try:
            return self.c.frame.body.wrapper.widget
        except AttributeError:
            return None

    # @+node:swot.20260222193522.15: *3* def apply_style
    def apply_style(self, position=None, length=0):
        """Prepare font and delegate formatting to _apply_formats"""
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
            font_needs_update = False

            # 1. Apply configured size ONLY ONCE on initialization
            if not self._initial_size_set:
                if current_font.pointSize() != config["size"]:
                    current_font.setPointSize(config["size"])
                    font_needs_update = True
                self._initial_size_set = True

            # 2. Enforce Font Family
            if current_font.family() != config["family"]:
                current_font.setFamily(config["family"])
                font_needs_update = True

            # 3. Enforce Letter Spacing
            if current_font.letterSpacing() != config["letter_spacing"]:
                current_font.setLetterSpacing(
                    QFont.SpacingType.PercentageSpacing, config["letter_spacing"]
                )
                font_needs_update = True

            if font_needs_update:
                editor.setFont(current_font)
                doc.setDefaultFont(current_font)

            self._apply_formats(editor, doc, config, position, length)
        finally:
            self._is_formatting = False

    # @+node:swot.20260222193522.16: *3* def _apply_formats
    def _apply_formats(self, editor, doc, config, position=None, length=0):
        """Execute paragraph and character formatting while preserving UI state"""
        v_scrollbar = editor.verticalScrollBar()

        # Determine scrollbar state using snapshot if undoing
        if self._is_undoing:
            saved_scroll_val = self._pre_undo_scroll_val
            was_at_bottom = self._pre_undo_was_at_bottom
        else:
            saved_scroll_val = v_scrollbar.value() if v_scrollbar else 0
            was_at_bottom = False
            if v_scrollbar:
                was_at_bottom = v_scrollbar.maximum() - saved_scroll_val <= 2

        # Save cursor position as integers to prevent reset during formatting
        main_cursor = editor.textCursor()
        saved_anchor = main_cursor.anchor()
        saved_pos = main_cursor.position()

        # Block signals to prevent infinite formatting loops
        editor.blockSignals(True)
        doc.blockSignals(True)

        cursor = QTextCursor(doc)

        try:
            if position is not None:
                # Incremental formatting for performance
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
                # Full document formatting
                cursor.select(QTextCursor.SelectionType.Document)

            # Apply Line Height
            block_fmt = QTextBlockFormat()
            block_fmt.setLineHeight(config["line_height"], config["line_height_type"])
            cursor.mergeBlockFormat(block_fmt)

            # Apply Letter Spacing and Font Family (DO NOT apply point size here to preserve zoom)
            char_fmt = QTextCharFormat()
            char_fmt.setFontFamily(config["family"])
            char_fmt.setFontLetterSpacingType(QFont.SpacingType.PercentageSpacing)
            char_fmt.setFontLetterSpacing(config["letter_spacing"])
            cursor.mergeCharFormat(char_fmt)
        finally:
            doc.blockSignals(False)
            editor.blockSignals(False)

            # Restore cursor position from saved integers
            max_pos = max(0, doc.characterCount() - 1)
            safe_anchor = min(saved_anchor, max_pos)
            safe_pos = min(saved_pos, max_pos)

            main_cursor.setPosition(safe_anchor)
            main_cursor.setPosition(safe_pos, QTextCursor.MoveMode.KeepAnchor)
            editor.setTextCursor(main_cursor)

            # Restore scrollbar position after cursor restoration
            if v_scrollbar:
                if was_at_bottom:
                    v_scrollbar.setValue(v_scrollbar.maximum())
                else:
                    v_scrollbar.setValue(min(saved_scroll_val, v_scrollbar.maximum()))

                # Secondary restoration with a short delay for precise layout alignment
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
