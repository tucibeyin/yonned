import asyncio
import logging
import signal
import sys
from app.core.config import settings

# Günlükleme yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [CriticalWorker] %(message)s"
)
logger = logging.getLogger("yonned.workers.critical")


class CriticalWorker:
    """Acil durumlar, SMS/OTP bildirimleri ve kritik olayları işleyen öncelikli worker."""

    def __init__(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        """Worker'ı güvenli bir şekilde durdurur."""
        logger.info("Kritik worker durdurma sinyali alındı. Kapanıyor...")
        self.is_running = False

    async def run(self) -> None:
        """Kritik görev kuyruğunu asenkron olarak dinler ve işletir."""
        logger.info(
            f"Kritik Worker başlatıldı. Ortam: {settings.ENVIRONMENT}, "
            f"Redis: {settings.REDIS_URL}"
        )

        while self.is_running:
            try:
                # Burada Redis LIST veya PubSub üzerinden acil görevler tüketilir
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Kritik worker döngüsünde hata: {e}", exc_info=True)
                await asyncio.sleep(2)

        logger.info("Kritik worker başarıyla kapatıldı.")


async def main() -> None:
    worker = CriticalWorker()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
