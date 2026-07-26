"""Production Automated Backup Manager for GrapheinAI.

Backs up:
- Extracted charts & raw data (data/raw)
- Generated PDF reports (data/reports)
- System application logs (logs/)
- Session state & exports
"""

import argparse
from datetime import datetime
import logging
import os
import tarfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BackupManager")

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = ROOT_DIR / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TARGET_DIRS = [
    ROOT_DIR / "data",
    ROOT_DIR / "logs",
]


def create_backup(dest_dir: Path = BACKUP_DIR) -> Path:
    """Creates a timestamped tar.gz archive of target production directories."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"graphein_backup_{timestamp}.tar.gz"
    archive_path = dest_dir / archive_name

    logger.info(f"Starting production backup process -> {archive_path.name}...")

    with tarfile.open(archive_path, "w:gz") as tar:
        for target_path in TARGET_DIRS:
            if target_path.exists():
                logger.info(f"Adding '{target_path.relative_to(ROOT_DIR)}' to backup archive...")
                tar.add(target_path, arcname=target_path.name)
            else:
                logger.warning(f"Target directory '{target_path}' does not exist. Skipping.")

    archive_size_mb = archive_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ Production backup successfully created: {archive_path.resolve()} ({archive_size_mb:.2f} MB)")
    return archive_path


def cleanup_old_backups(max_keep: int = 10, dest_dir: Path = BACKUP_DIR) -> None:
    """Cleans up older backups keeping only the most recent N archives."""
    archives = sorted(dest_dir.glob("graphein_backup_*.tar.gz"), key=os.path.getmtime, reverse=True)
    if len(archives) > max_keep:
        to_delete = archives[max_keep:]
        for arch in to_delete:
            logger.info(f"Purging old backup archive: {arch.name}")
            arch.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GrapheinAI Production Backup Manager")
    parser.add_argument("--keep", type=int, default=10, help="Number of recent backups to keep")
    args = parser.parse_args()

    created_file = create_backup()
    cleanup_old_backups(max_keep=args.keep)
