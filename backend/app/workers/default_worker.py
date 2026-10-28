import asyncio
import logging
import signal
import sys
from app.core.config import settings

# Günlükleme yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [DefaultWorker] %(message)s"
)
logger = logging.getLogger("yonned.workers.default")


class DefaultWorker:
    """Medya işleme, arşivleme ve genel arkaplan görevlerini işleyen standart worker."""

    def __init__(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        """Worker'ı güvenli bir şekilde durdurur."""
        logger.info("Standart worker durdurma sinyali alındı. Kapanıyor...")
        self.is_running = False

    async def run(self) -> None:
        """Standart görev kuyruğunu asenkron olarak dinler ve işletir."""
        logger.info(
            f"Standart Worker başlatıldı. Ortam: {settings.ENVIRONMENT}, "
            f"Redis: {settings.REDIS_URL}"
        )

        while self.is_running:
            try:
                # Standart arka plan görevleri tüketilir
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Standart worker döngüsünde hata: {e}", exc_info=True)
                await asyncio.sleep(3)

        logger.info("Standart worker başarıyla kapatıldı.")


async def main() -> None:
    worker = DefaultWorker()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.stop)

    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
