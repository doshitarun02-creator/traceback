import logging
import os
import uuid
from io import BytesIO

logger = logging.getLogger(__name__)

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    logger.warning("cloudinary package not installed. CloudinaryFileService will run in stub mode.")


class CloudinaryFileService:

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "mp4", "mov"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        self._configured = False

        if CLOUDINARY_AVAILABLE and cloud_name and api_key and api_secret:
            try:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True,
                )
                self._configured = True
                logger.info(f"CloudinaryFileService configured for cloud='{cloud_name}'")
            except Exception as e:
                logger.error(f"Cloudinary configuration failed: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def upload_evidence(self, file, case_id: str) -> str | None:
        """
        Upload a single evidence file to Cloudinary.

        Args:
            file: A file-like object (Flask request.files item) or a file path str.
            case_id: TraceBack case identifier used to organise the upload folder.

        Returns:
            Cloudinary secure_url string, or None on failure.
        """
        if not self._validate_file(file):
            return None

        folder = f"traceback/evidence/{case_id}"
        public_id = f"{folder}/{uuid.uuid4().hex}"

        if not self._configured:
            logger.warning("Cloudinary not configured — upload skipped (stub mode).")
            return f"https://res.cloudinary.com/{self.cloud_name}/{public_id}_stub"

        try:
            file_data = self._read_file(file)
            result = cloudinary.uploader.upload(
                file_data,
                public_id=public_id,
                resource_type="auto",
                folder=None,        # folder already encoded in public_id
                overwrite=False,
                unique_filename=False,
            )
            secure_url = result.get("secure_url")
            logger.info(f"Uploaded evidence for case {case_id}: {secure_url}")
            return secure_url
        except Exception as e:
            logger.error(f"Cloudinary upload failed for case {case_id}: {e}")
            return None

    def upload_multiple(self, files: list, case_id: str) -> list[str]:
        """
        Upload multiple evidence files for a case.

        Args:
            files: List of file-like objects or file path strings.
            case_id: TraceBack case identifier.

        Returns:
            List of successfully uploaded Cloudinary secure_url strings.
        """
        urls = []
        for file in files:
            url = self.upload_evidence(file, case_id)
            if url:
                urls.append(url)
        return urls

    def delete_evidence(self, public_id: str) -> bool:
        """
        Delete an evidence asset by its Cloudinary public_id.

        Returns True on success, False on failure.
        """
        if not self._configured:
            logger.warning(f"Cloudinary not configured — delete skipped for '{public_id}'.")
            return False
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type="auto")
            success = result.get("result") == "ok"
            if success:
                logger.info(f"Deleted Cloudinary asset: {public_id}")
            else:
                logger.warning(f"Cloudinary delete result for '{public_id}': {result}")
            return success
        except Exception as e:
            logger.error(f"Cloudinary delete failed for '{public_id}': {e}")
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_file(self, file) -> bool:
        """Return True if the file passes extension and size checks."""
        filename = self._get_filename(file)
        if not filename:
            logger.warning("File validation failed: no filename available.")
            return False

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in self.ALLOWED_EXTENSIONS:
            logger.warning(f"Rejected file '{filename}': extension '{ext}' not allowed.")
            return False

        size = self._get_file_size(file)
        if size and size > self.MAX_FILE_SIZE:
            logger.warning(
                f"Rejected file '{filename}': size {size} bytes exceeds "
                f"{self.MAX_FILE_SIZE} byte limit."
            )
            return False

        return True

    def _get_filename(self, file) -> str:
        """Extract filename from a Flask file object or path string."""
        if isinstance(file, str):
            return os.path.basename(file)
        return getattr(file, "filename", "") or ""

    def _get_file_size(self, file) -> int | None:
        """Return file size in bytes without consuming the stream."""
        if isinstance(file, str):
            try:
                return os.path.getsize(file)
            except OSError:
                return None
        # Flask FileStorage / file-like object
        if hasattr(file, "seek") and hasattr(file, "tell"):
            try:
                current = file.tell()
                file.seek(0, 2)  # seek to end
                size = file.tell()
                file.seek(current)  # restore position
                return size
            except Exception:
                return None
        if hasattr(file, "content_length"):
            return file.content_length
        return None

    def _read_file(self, file):
        """
        Return a BytesIO or file path suitable for cloudinary.uploader.upload().
        Rewinds file-like objects before returning.
        """
        if isinstance(file, str):
            return file  # Cloudinary accepts file paths
        if hasattr(file, "read"):
            if hasattr(file, "seek"):
                file.seek(0)
            data = file.read()
            return BytesIO(data)
        return file
