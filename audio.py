import threading
import numpy as np

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

SAMPLE_RATE = 44100
BLOCK_SIZE = 1024


class AudioAnalyzer:
    def __init__(self):
        self.amplitude = 0.0
        self.is_transient = False
        self.spectral_centroid = 0.0
        self._prev_rms = 0.0
        self._lock = threading.Lock()
        self._stream = None
        self._running = False

    def start(self):
        if not HAS_SOUNDDEVICE:
            return False
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                blocksize=BLOCK_SIZE,
                callback=self._callback,
                dtype='float32',
            )
            self._stream.start()
            self._running = True
            return True
        except Exception:
            return False

    def stop(self):
        self._running = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if status:
            return
        mono = indata[:, 0]
        rms = float(np.sqrt(np.mean(mono ** 2)))
        rms = min(1.0, rms * 8.0)

        transient = (rms - self._prev_rms) > 0.15

        fft_mag = np.abs(np.fft.rfft(mono))
        freqs = np.fft.rfftfreq(len(mono), 1 / SAMPLE_RATE)
        sc = float(np.sum(freqs * fft_mag) / (np.sum(fft_mag) + 1e-9))
        sc_norm = min(1.0, sc / 4000.0)

        with self._lock:
            self.amplitude = rms
            self.is_transient = transient
            self.spectral_centroid = sc_norm
            self._prev_rms = rms

    def get(self):
        with self._lock:
            return self.amplitude, self.is_transient, self.spectral_centroid