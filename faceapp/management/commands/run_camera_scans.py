import logging
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from faceapp.models import Camera
from faceapp.camera_scanner import scan_camera

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Polling berkala: scan frame CCTV aktif tiap interval detik sesuai konfigurasi kamera."

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=0,
                             help='Override interval global (detik). Jika 0, pakai interval per kamera.')
        parser.add_argument('--once', action='store_true',
                             help='Jalankan sekali untuk semua kamera aktif, lalu keluar.')
        parser.add_argument('--camera', type=int, default=0,
                             help='Scan hanya kamera dengan ID tertentu.')

    def handle(self, *args, **options):
        global_interval = options.get('interval') or 0
        once = options.get('once', False)
        only_pk = options.get('camera') or None

        if once:
            self._run_once(only_pk)
            return

        self.stdout.write(self.style.NOTICE("Scheduler kamera aktif memulai polling..."))
        last_run = {}
        try:
            while True:
                self._tick(global_interval, last_run, only_pk)
        except KeyboardInterrupt:
            self.stdout.write(self.style.NOTICE("Scheduler dihentikan."))

    def _run_once(self, only_pk):
        cameras = Camera.objects.filter(auto_scan=True)
        if only_pk:
            cameras = cameras.filter(pk=only_pk)
        if not cameras.exists():
            self.stdout.write(self.style.WARNING("Tidak ada kamera dengan auto_scan aktif."))
            return
        for camera in cameras:
            self._scan(camera)

    def _tick(self, global_interval, last_run, only_pk):
        cameras = Camera.objects.filter(auto_scan=True).exclude(stream_url='')
        if only_pk:
            cameras = cameras.filter(pk=only_pk)
        now = timezone.now()
        for camera in cameras:
            interval = global_interval or camera.scan_interval_seconds or 30
            last = last_run.get(camera.id)
            if last and (timezone.now() - last).total_seconds() < interval:
                continue
            last_run[camera.id] = timezone.now()
            self._scan(camera)
        time.sleep(1)

    def _scan(self, camera):
        self.stdout.write(f"Scanning kamera {camera.name} (stream {camera.stream_url})...")
        started = time.time()
        try:
            log = scan_camera(camera, identify=True)
            elapsed = round(time.time() - started, 2)
            if log and log.error_message:
                self.stdout.write(self.style.WARNING(f"  gagal: {log.error_message} ({elapsed}s)"))
            elif log:
                self.stdout.write(self.style.SUCCESS(
                    f"  selesai: {log.face_count} wajah "
                    f"(cocok {log.matched_person_id}) {elapsed}s"
                ))
        except Exception as exc:
            logger.exception("scan error")
            raise CommandError(f"Gagal memindai {camera.name}: {exc}")
