import subprocess
import shutil
import time
import zipfile
from pathlib import Path


class Recorder:
    def __init__(self, output_dir="camascii_recording"):
        self.output_dir = Path(output_dir)
        self.frames = []
        self.recording = False
        self.start_time = None

    def start(self):
        self.frames = []
        self.recording = True
        self.start_time = time.time()
        self.output_dir.mkdir(exist_ok=True)

    def stop(self):
        self.recording = False
        return self._export_txt_zip()

    def add_frame(self, rows):
        if self.recording:
            self.frames.append(list(rows))

    def _export_txt_zip(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        zip_path = f"camascii_rec_{ts}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, frame in enumerate(self.frames):
                zf.writestr(f"frame_{i:06d}.txt", "\n".join(frame))
        return zip_path

    def export_video(self, fps=24):
        if not shutil.which("ffmpeg"):
            return self._export_txt_zip()

        ts = time.strftime("%Y%m%d_%H%M%S")
        tmp_dir = Path(f"/tmp/camascii_{ts}")
        tmp_dir.mkdir()
        out_path = f"camascii_vid_{ts}.mp4"

        for i, frame in enumerate(self.frames):
            frame_path = tmp_dir / f"frame_{i:06d}.txt"
            frame_path.write_text("\n".join(frame))

        if shutil.which("convert"):
            for i, frame in enumerate(self.frames):
                txt_path = tmp_dir / f"frame_{i:06d}.txt"
                png_path = tmp_dir / f"frame_{i:06d}.png"
                subprocess.run([
                    "convert",
                    "-background", "black",
                    "-fill", "#00ff41",
                    "-font", "Courier-New",
                    "-pointsize", "12",
                    f"label:@{txt_path}",
                    str(png_path),
                ], check=False, capture_output=True)

            subprocess.run([
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", str(tmp_dir / "frame_%06d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                out_path,
            ], check=False, capture_output=True)
            shutil.rmtree(tmp_dir)
            return out_path

        shutil.rmtree(tmp_dir)
        return self._export_txt_zip()