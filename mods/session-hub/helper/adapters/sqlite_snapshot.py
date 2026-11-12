"""Read-only in-memory SQLite/WAL projection; never opens source with SQLite.

Independent implementation of https://sqlite.org/fileformat2.html#walformat.
Checksums/salts and commit boundaries are validated before deserialization.
The caller validates narrow paths and verifies before/after fingerprints.
"""
import sqlite3
import struct
import time

LIMIT = 128 * 1024 * 1024


def checksum(data, endian, state=(0, 0)):
    a, b = state
    for x, y in struct.iter_unpack(endian + "II", data):
        a = (a + x + b) & 0xffffffff
        b = (b + y + a) & 0xffffffff
    return a, b


def project(database, wal):
    if len(database) < 100 or database[:16] != b"SQLite format 3\0" or len(database) + len(wal) > LIMIT:
        raise ValueError("Invalid or oversized SQLite snapshot")
    page_size = int.from_bytes(database[16:18], "big")
    page_size = 65536 if page_size == 1 else page_size
    if page_size < 512 or page_size > 65536 or page_size & (page_size - 1) or len(database) % page_size:
        raise ValueError("Invalid SQLite page size")
    result = bytearray(database)
    if wal:
        if len(wal) < 32:
            raise ValueError("Incomplete WAL header")
        magic, version, size, _, salt1, salt2, check1, check2 = struct.unpack(">8I", wal[:32])
        if magic not in (0x377f0682, 0x377f0683) or version != 3007000 or size != page_size:
            raise ValueError("Unsupported WAL header")
        endian = "<" if magic == 0x377f0682 else ">"
        state = checksum(wal[:24], endian)
        if state != (check1, check2):
            raise ValueError("Invalid WAL header checksum")
        frame_size, commit_end, pages = 24 + page_size, 32, 0
        deadline = time.monotonic() + 4
        for offset in range(32, len(wal) - frame_size + 1, frame_size):
            if time.monotonic() > deadline:
                raise ValueError("WAL validation time budget exceeded")
            page, count, s1, s2, c1, c2 = struct.unpack(">6I", wal[offset:offset + 24])
            # Old frames can remain after reset; SQLite ignores that suffix.
            if (s1, s2) != (salt1, salt2):
                break
            if not 0 < page <= LIMIT // page_size or count > LIMIT // page_size:
                raise ValueError("WAL page budget exceeded")
            state = checksum(wal[offset:offset + 8], endian, state)
            state = checksum(memoryview(wal)[offset + 24:offset + frame_size], endian, state)
            if state != (c1, c2):
                raise ValueError("Invalid WAL frame checksum")
            if count:
                commit_end, pages = offset + frame_size, count
        if pages:
            target = pages * page_size
            if target > len(result):
                result.extend(bytes(target - len(result)))
            del result[target:]
            for offset in range(32, commit_end, frame_size):
                page = int.from_bytes(wal[offset:offset + 4], "big")
                if page <= pages:
                    result[(page - 1) * page_size:page * page_size] = wal[offset + 24:offset + frame_size]
            result[28:32] = pages.to_bytes(4, "big")
    # In-memory deserialize cannot open a WAL. This alters only the private image.
    result[18:20] = b"\x01\x01"
    return result


def connect(database, wal):
    db = sqlite3.connect(":memory:")
    try:
        db.deserialize(project(database, wal))
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        return db
    except Exception:
        db.close()
        raise
