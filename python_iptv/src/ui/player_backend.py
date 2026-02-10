"""
Player Backend Abstraction Layer.
Provides a unified interface for VLC and mpv media players.
Auto-detects available backend: tries mpv first, then VLC.
"""
import sys
import os
import logging
from abc import abstractmethod
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class PlayerState(Enum):
    IDLE = "idle"
    OPENING = "opening"
    BUFFERING = "buffering"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    ENDED = "ended"


class PlayerBackend(QObject):
    """Abstract base class for media player backends with Signals."""
    
    # Signals for thread-safe UI updates
    state_changed = pyqtSignal(PlayerState)
    time_changed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()

    @abstractmethod
    def play(self, url: str, options: dict = None):
        """Start playing a media URL."""
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    @abstractmethod
    def pause(self):
        pass
    
    @abstractmethod
    def resume(self):
        pass
    
    @abstractmethod
    def toggle_pause(self):
        pass
    
    @abstractmethod
    def set_volume(self, value: int):
        """Set volume (0-100)."""
        pass
    
    @abstractmethod
    def set_window(self, window_id: int):
        """Embed video in a Qt widget window."""
        pass
    
    @abstractmethod
    def is_playing(self) -> bool:
        pass
    
    @abstractmethod
    def get_state(self) -> PlayerState:
        pass
    
    @abstractmethod
    def get_time(self) -> int:
        """Returns current playback time in ms, or -1."""
        pass
    
    @abstractmethod
    def set_time(self, ms: int):
        """Seek to position in ms."""
        pass
    
    @abstractmethod
    def video_set_aspect_ratio(self, ratio: str):
        pass
    
    @abstractmethod
    def video_take_snapshot(self, num: int, path: str, width: int, height: int):
        pass
    
    @abstractmethod
    def cleanup(self):
        """Release resources."""
        pass


# ==================== VLC Backend ====================

class VLCBackend(PlayerBackend):
    """VLC-based player backend using python-vlc."""
    
    def __init__(self):
        super().__init__()
        import vlc
        self._vlc = vlc
        
        vlc_args = [
            '--http-user-agent=VAVOO/2.6',
            '--no-video-title-show',
            '--quiet',
            '--no-xlib',
            '--network-caching=5000'
        ]
        self._instance = vlc.Instance(*vlc_args)
        self._player = self._instance.media_player_new()
        self._player.video_set_mouse_input(False)
        self._player.video_set_key_input(False)
        
        # Determine initial state
        self._last_state = PlayerState.IDLE
        
        # Setup event manager
        self._event_manager = self._player.event_manager()
        events = [
            vlc.EventType.MediaPlayerOpening,
            vlc.EventType.MediaPlayerBuffering,
            vlc.EventType.MediaPlayerPlaying,
            vlc.EventType.MediaPlayerPaused,
            vlc.EventType.MediaPlayerStopped,
            vlc.EventType.MediaPlayerEndReached,
            vlc.EventType.MediaPlayerEncounteredError,
            vlc.EventType.MediaPlayerTimeChanged
        ]
        for e in events:
            self._event_manager.event_attach(e, self._on_vlc_event)
            
        logging.info("Player Backend: VLC initialized.")
    
    def _on_vlc_event(self, event):
        """Translate VLC events to Signals."""
        new_state = None
        if event.type == self._vlc.EventType.MediaPlayerOpening:
            new_state = PlayerState.OPENING
        elif event.type == self._vlc.EventType.MediaPlayerBuffering:
            # VLC sends buffering as a percentage in event.u.new_buffering
            new_state = PlayerState.BUFFERING
        elif event.type == self._vlc.EventType.MediaPlayerPlaying:
            new_state = PlayerState.PLAYING
        elif event.type == self._vlc.EventType.MediaPlayerPaused:
            new_state = PlayerState.PAUSED
        elif event.type == self._vlc.EventType.MediaPlayerStopped:
            new_state = PlayerState.STOPPED
        elif event.type == self._vlc.EventType.MediaPlayerEndReached:
            new_state = PlayerState.ENDED
        elif event.type == self._vlc.EventType.MediaPlayerEncounteredError:
            new_state = PlayerState.ERROR
            self.error_occurred.emit("VLC Error occurred")
        elif event.type == self._vlc.EventType.MediaPlayerTimeChanged:
            self.time_changed.emit(event.u.new_time)
            
        if new_state is not None and new_state != self._last_state:
            self._last_state = new_state
            self.state_changed.emit(new_state)

    def play(self, url: str, options: dict = None):
        self._player.stop()
        media = self._instance.media_new(url)
        
        ua = (options or {}).get('user_agent', 'VAVOO/2.6')
        referrer = (options or {}).get('referrer', 'https://vavoo.to/')
        caching = (options or {}).get('caching', '5000')
        
        media.add_option(f":http-user-agent={ua}")
        media.add_option(f":http-referrer={referrer}")
        media.add_option(f":network-caching={caching}")
        media.add_option(":http-reconnect=true")
        
        self._player.set_media(media)
        self._player.play()
    
    def stop(self):
        self._player.stop()
    
    def pause(self):
        self._player.set_pause(1)
        
    def resume(self):
        self._player.set_pause(0)
    
    def toggle_pause(self):
        self._player.pause()
    
    def set_volume(self, value: int):
        self._player.audio_set_volume(value)
    
    def set_window(self, window_id: int):
        if sys.platform == "win32":
            self._player.set_hwnd(window_id)
        elif sys.platform.startswith("linux"):
            self._player.set_xwindow(window_id)
    
    def is_playing(self) -> bool:
        return self._player.is_playing()
    
    def get_state(self) -> PlayerState:
        return self._last_state
    
    def get_time(self) -> int:
        return self._player.get_time()
    
    def set_time(self, ms: int):
        self._player.set_time(ms)
    
    def video_set_aspect_ratio(self, ratio: str):
        self._player.video_set_aspect_ratio(ratio)
    
    def video_take_snapshot(self, num: int, path: str, width: int, height: int):
        self._player.video_take_snapshot(num, path, width, height)
    
    def cleanup(self):
        self._player.stop()
        self._player.release()
        self._instance.release()
        logging.info("VLC Backend cleaned up.")


# ==================== mpv Backend ====================

class MpvBackend(PlayerBackend):
    """mpv-based player backend using python-mpv."""
    
    def __init__(self):
        super().__init__()
        import mpv
        self._mpv_module = mpv
        
        # Initialize MPV with default options
        # Note: input_default_bindings=True might be needed if we want MPV to handle some keys, 
        # but usually False is better for embedding so PyQt handles it.
        self._player = mpv.MPV(
            wid=0,
            vo='gpu',
            hwdec='auto',
            input_default_bindings=False,
            input_vo_keyboard=False,
            osc=False,
            user_agent='VAVOO/2.6',
            cache='yes',
            demuxer_max_bytes='50MiB',
            demuxer_max_back_bytes='25MiB',
            log_handler=logging.debug
        )
        
        self._window_id = None
        self._current_state = PlayerState.IDLE
        
        # --- Property Observers (Thread-safe emission using pyqtSignal) ---
        
        @self._player.property_observer('idle-active')
        def on_idle_change(_name, value):
            if value:
                self._current_state = PlayerState.IDLE
                self.state_changed.emit(PlayerState.IDLE)

        @self._player.property_observer('core-idle')
        def on_core_idle(_name, value):
             # Useful for detecting loading states sometimes, 
             # but idle-active is usually enough.
             pass

        @self._player.property_observer('pause')
        def on_pause_change(_name, value):
            if value:
                self._current_state = PlayerState.PAUSED
                self.state_changed.emit(PlayerState.PAUSED)
            elif self._player.idle_active:
                 pass # Still idle
            else:
                self._current_state = PlayerState.PLAYING
                self.state_changed.emit(PlayerState.PLAYING)
        
        # 'eof-reached' behaves differently in some mpv versions.
        @self._player.property_observer('eof-reached')
        def on_eof(_name, value):
            if value:
                self._current_state = PlayerState.ENDED
                self.state_changed.emit(PlayerState.ENDED)

        # Buffering handling
        # 'paused-for-cache' is true when buffering
        @self._player.property_observer('paused-for-cache')
        def on_buffering(_name, value):
            if value:
                self._current_state = PlayerState.BUFFERING
                self.state_changed.emit(PlayerState.BUFFERING)
            elif not self._player.pause:
                 # If we were buffering and now we are not, and not paused, we are playing
                 self._current_state = PlayerState.PLAYING
                 self.state_changed.emit(PlayerState.PLAYING)

        @self._player.property_observer('time-pos')
        def on_time(_name, value):
            if value is not None:
                self.time_changed.emit(int(value * 1000))

        logging.info("Player Backend: mpv initialized.")
    
    def play(self, url: str, options: dict = None):
        ua = (options or {}).get('user_agent', 'VAVOO/2.6')
        referrer = (options or {}).get('referrer', 'https://vavoo.to/')
        
        # mpv properties
        self._player.user_agent = ua
        self._player.referrer = referrer
        
        self._current_state = PlayerState.OPENING
        self.state_changed.emit(PlayerState.OPENING)
        
        try:
            self._player.play(url)
        except Exception as e:
            self._current_state = PlayerState.ERROR
            self.state_changed.emit(PlayerState.ERROR)
            self.error_occurred.emit(str(e))
    
    def stop(self):
        self._player.command('stop')
        self._current_state = PlayerState.STOPPED
        self.state_changed.emit(PlayerState.STOPPED)
    
    def pause(self):
        self._player.pause = True
    
    def resume(self):
        self._player.pause = False
    
    def toggle_pause(self):
        self._player.pause = not self._player.pause
    
    def set_volume(self, value: int):
        self._player.volume = value
    
    def set_window(self, window_id: int):
        self._window_id = window_id
        # Setting wid after init might require property access
        self._player.wid = window_id
    
    def is_playing(self) -> bool:
        try:
            return not self._player.pause and not self._player.idle_active
        except Exception:
            return False
    
    def get_state(self) -> PlayerState:
        return self._current_state
    
    def get_time(self) -> int:
        # Uses observer usually, but direct access:
        try:
             t = self._player.time_pos
             return int(t * 1000) if t else 0
        except: return 0
    
    def set_time(self, ms: int):
        try:
            self._player.time_pos = ms / 1000.0
        except Exception:
            pass
    
    def video_set_aspect_ratio(self, ratio: str):
        try:
            self._player.video_aspect_override = ratio if ratio else '-1'
        except Exception:
            pass
    
    def video_take_snapshot(self, num: int, path: str, width: int, height: int):
        try:
            # mpv screenshot_to_file usually synchronous?
            self._player.screenshot_to_file(path, 'video')
            logging.info(f"mpv: Snapshot saved to {path}")
        except Exception as e:
            logging.error(f"mpv: Snapshot failed: {e}")
            self.error_occurred.emit(f"Snapshot failed: {e}")
    
    def cleanup(self):
        try:
            self._player.terminate()
        except Exception:
            pass
        logging.info("mpv Backend cleaned up.")


# ==================== Factory ====================

def create_player() -> PlayerBackend:
    """Creates the best available player backend.
    Tries mpv first, then VLC. Raises RuntimeError if neither is available."""
    
    # Try mpv
    try:
        backend = MpvBackend()
        return backend
    except Exception as e:
        logging.warning(f"mpv not available: {e}")

    # Try VLC
    try:
        backend = VLCBackend()
        return backend
    except Exception as e:
        logging.warning(f"VLC not available: {e}")
    
    raise RuntimeError(
        "No media player backend found!\n"
        "Please install mpv (https://mpv.io/) or VLC (https://www.videolan.org/)."
    )


def get_backend_name(backend: PlayerBackend) -> str:
    """Returns a human-readable name for the backend."""
    if isinstance(backend, VLCBackend):
        return "VLC"
    elif isinstance(backend, MpvBackend):
        return "mpv"
    return "Unknown"
