#!/usr/bin/env python3
"""
SecRef Database Backup Script

Performs automated backups of the SQLite database with:
- Rotation policy (keep last N backups)
- Compression
- Integrity verification
- Logging
"""

import argparse
import gzip
import hashlib
import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.config import Config


class DatabaseBackup:
    """Handles database backup operations"""

    def __init__(
        self,
        db_path: str,
        backup_dir: str,
        keep_backups: int = 7,
        compress: bool = True,
    ):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.keep_backups = keep_backups
        self.compress = compress

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def create_backup(self) -> Optional[Path]:
        """Create a backup of the database"""
        if not self.db_path.exists():
            self.logger.error(f"Database not found: {self.db_path}")
            return None

        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"secref_backup_{timestamp}.db"
        if self.compress:
            backup_name += ".gz"
        backup_path = self.backup_dir / backup_name

        try:
            # Create backup using SQLite backup API
            self.logger.info(f"Starting backup to {backup_path}")

            # Open source database
            source_conn = sqlite3.connect(self.db_path)

            if self.compress:
                # Create compressed backup
                with gzip.open(backup_path, "wb") as gz_file:
                    # Create temporary backup
                    temp_path = backup_path.with_suffix("")
                    backup_conn = sqlite3.connect(temp_path)
                    source_conn.backup(backup_conn)
                    backup_conn.close()

                    # Compress the backup
                    with open(temp_path, "rb") as f:
                        gz_file.write(f.read())

                    # Remove temporary file
                    temp_path.unlink()
            else:
                # Direct backup
                backup_conn = sqlite3.connect(backup_path)
                source_conn.backup(backup_conn)
                backup_conn.close()

            source_conn.close()

            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            self.logger.info(f"Backup created: {backup_path} (checksum: {checksum})")

            # Write checksum file
            checksum_path = backup_path.with_suffix(backup_path.suffix + ".sha256")
            checksum_path.write_text(f"{checksum}  {backup_path.name}\n")

            return backup_path

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            if backup_path.exists():
                backup_path.unlink()
            return None

    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity"""
        checksum_path = backup_path.with_suffix(backup_path.suffix + ".sha256")

        if not checksum_path.exists():
            self.logger.warning(f"No checksum file found for {backup_path}")
            return False

        try:
            # Read expected checksum
            expected_checksum = checksum_path.read_text().split()[0]

            # Calculate actual checksum
            actual_checksum = self._calculate_checksum(backup_path)

            if expected_checksum == actual_checksum:
                self.logger.info(f"Backup verified: {backup_path}")
                return True
            else:
                self.logger.error(
                    f"Checksum mismatch for {backup_path}: "
                    f"expected {expected_checksum}, got {actual_checksum}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        # Find all backup files
        if self.compress:
            pattern = "secref_backup_*.db.gz"
        else:
            pattern = "secref_backup_*.db"

        backups = sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime)

        # Keep only the most recent N backups
        if len(backups) > self.keep_backups:
            for backup in backups[: -self.keep_backups]:
                self.logger.info(f"Removing old backup: {backup}")
                backup.unlink()

                # Remove checksum file
                checksum_path = backup.with_suffix(backup.suffix + ".sha256")
                if checksum_path.exists():
                    checksum_path.unlink()

    def restore_backup(self, backup_path: Path, target_path: Optional[Path] = None) -> bool:
        """Restore a backup"""
        if not backup_path.exists():
            self.logger.error(f"Backup not found: {backup_path}")
            return False

        # Verify backup first
        if not self.verify_backup(backup_path):
            self.logger.error("Backup verification failed, aborting restore")
            return False

        target = target_path or self.db_path

        try:
            # Create backup of current database
            if target.exists():
                temp_backup = target.with_suffix(".backup_temp")
                shutil.copy2(target, temp_backup)
                self.logger.info(f"Created temporary backup: {temp_backup}")

            # Restore the backup
            if backup_path.suffix == ".gz":
                # Decompress first
                with gzip.open(backup_path, "rb") as gz_file:
                    with open(target, "wb") as f:
                        f.write(gz_file.read())
            else:
                shutil.copy2(backup_path, target)

            self.logger.info(f"Restored backup to {target}")

            # Remove temporary backup
            if target.exists() and temp_backup.exists():
                temp_backup.unlink()

            return True

        except Exception as e:
            self.logger.error(f"Restore failed: {e}")

            # Restore from temporary backup
            if temp_backup.exists():
                shutil.copy2(temp_backup, target)
                temp_backup.unlink()
                self.logger.info("Restored from temporary backup")

            return False

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SecRef Database Backup Tool")
    parser.add_argument(
        "--backup-dir",
        default="backups",
        help="Directory to store backups (default: backups)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=7,
        help="Number of backups to keep (default: 7)",
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Disable backup compression",
    )
    parser.add_argument(
        "--restore",
        metavar="BACKUP_FILE",
        help="Restore from specified backup file",
    )
    parser.add_argument(
        "--verify",
        metavar="BACKUP_FILE",
        help="Verify specified backup file",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Get database path from config
    config = Config()
    db_path = config.DATABASE_PATH

    # Create backup manager
    backup_manager = DatabaseBackup(
        db_path=db_path,
        backup_dir=args.backup_dir,
        keep_backups=args.keep,
        compress=not args.no_compress,
    )

    # Handle different operations
    if args.list:
        # List backups
        pattern = "secref_backup_*.db*"
        backups = sorted(
            backup_manager.backup_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if backups:
            print("Available backups:")
            for backup in backups:
                size = backup.stat().st_size / (1024 * 1024)  # MB
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                verified = "✓" if backup_manager.verify_backup(backup) else "✗"
                print(f"  {verified} {backup.name} ({size:.1f} MB) - {mtime}")
        else:
            print("No backups found")

    elif args.verify:
        # Verify backup
        backup_path = Path(args.verify)
        if backup_manager.verify_backup(backup_path):
            print(f"✓ Backup verified: {backup_path}")
            sys.exit(0)
        else:
            print(f"✗ Backup verification failed: {backup_path}")
            sys.exit(1)

    elif args.restore:
        # Restore backup
        backup_path = Path(args.restore)
        if backup_manager.restore_backup(backup_path):
            print(f"✓ Backup restored: {backup_path}")
            sys.exit(0)
        else:
            print(f"✗ Restore failed: {backup_path}")
            sys.exit(1)

    else:
        # Create backup
        backup_path = backup_manager.create_backup()
        if backup_path:
            backup_manager.cleanup_old_backups()
            print(f"✓ Backup created: {backup_path}")
            sys.exit(0)
        else:
            print("✗ Backup failed")
            sys.exit(1)


if __name__ == "__main__":
    main()