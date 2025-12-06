from abc import ABC, abstractmethod
import logging

# ============================
# KONFIGURASI LOGGING
# ============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)


# ============================
# INTERFACE VALIDATION RULE (DIP)
# ============================
class IValidationRule(ABC):
    """Interface untuk aturan validasi dalam proses registrasi."""

    @abstractmethod
    def validate(self, data) -> bool:
        """Memvalidasi data mahasiswa.

        Args:
            data (dict): Data mahasiswa.

        Returns:
            bool: True jika valid, False jika tidak valid.
        """
        pass



# ============================
# RULE 1: Validasi Batas SKS
# ============================
class SksLimitRule(IValidationRule):
    """Rule untuk memvalidasi apakah jumlah SKS tidak melebihi batas."""

    def __init__(self, max_sks: int):
        """Inisialisasi rule batas SKS.

        Args:
            max_sks (int): Batas maksimum SKS.
        """
        self.max_sks = max_sks

    def validate(self, data):
        """Memvalidasi jumlah SKS mahasiswa.

        Args:
            data (dict): Data mahasiswa.

        Returns:
            bool: True jika valid.
        """
        if data['sks'] <= self.max_sks:
            LOGGER.info("SKS %s tidak melebihi batas %s.", data['sks'], self.max_sks)
            return True

        LOGGER.error("SKS %s melebihi batas maksimum %s.", data['sks'], self.max_sks)
        return False


# ============================
# RULE 2: Validasi Prasyarat
# ============================
class PrerequisiteRule(IValidationRule):
    """Rule untuk memvalidasi apakah prasyarat mata kuliah sudah terpenuhi."""

    def validate(self, data):
        """Memvalidasi prasyarat mata kuliah.

        Args:
            data (dict): Data mahasiswa.

        Returns:
            bool: True jika semua prasyarat terpenuhi.
        """
        missing = [
            course for course in data["prasyarat"]
            if course not in data["sudah_lulus"]
        ]

        if not missing:
            LOGGER.info("Semua prasyarat telah terpenuhi.")
            return True

        LOGGER.warning("Prasyarat belum terpenuhi: %s", missing)
        return False


# ============================
# RULE 3: Validasi Jadwal Bentrok (OCP)
# ============================
class JadwalBentrokRule(IValidationRule):
    """Rule untuk memvalidasi apakah terdapat bentrok jadwal."""

    def validate(self, data):
        """Memvalidasi jadwal bentrok.

        Args:
            data (dict): Data mahasiswa.

        Returns:
            bool: True jika tidak ada bentrok.
        """
        jadwal = data["jadwal"]
        hari = jadwal["hari"]
        jam = jadwal["jam"]

        for item in data["jadwal_terambil"]:
            if item["hari"] == hari and item["jam"] == jam:
                LOGGER.error("Jadwal bentrok dengan mata kuliah lain!")
                return False

        LOGGER.info("Tidak ada bentrok jadwal.")
        return True


# ============================
# REGISTRATION SERVICE (SRP + DIP)
# ============================
class RegistrationService:
    """Service utama untuk menjalankan semua rule validasi."""

    def __init__(self, rules: list[IValidationRule]):
        """Inisialisasi RegistrationService.

        Args:
            rules (list[IValidationRule]): Daftar aturan validasi.
        """
        self.rules = rules

    def validate(self, data):
        """Menjalankan seluruh rule validasi.

        Args:
            data (dict): Data mahasiswa.

        Returns:
            bool: True jika semua rule lolos.
        """
        LOGGER.info("=== Menjalankan Validasi Registrasi ===")
        for rule in self.rules:
            if not rule.validate(data):
                LOGGER.error("Registrasi gagal.")
                return False

        LOGGER.info("Registrasi berhasil.")
        return True


# ============================
# EKSEKUSI
# ============================
if __name__ == "__main__":
    student_data = {
        "sks": 20,
        "prasyarat": ["Algoritma", "Struktur Data"],
        "sudah_lulus": ["Algoritma"],
        "jadwal": {"hari": "Senin", "jam": "08:00"},
        "jadwal_terambil": [
            {"hari": "Senin", "jam": "08:00"}
        ]
    }

    rules = [
        SksLimitRule(max_sks=24),
        PrerequisiteRule(),
        JadwalBentrokRule(),
    ]

    service = RegistrationService(rules)
    service.validate(student_data)
