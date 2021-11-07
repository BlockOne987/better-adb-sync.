#!/usr/bin/env python3

from typing import Iterable, Tuple
import os
import re
import subprocess

from ..SAOLogging import criticalLogExit

from .Base import FileSystem

class LocalFileSystem(FileSystem):
    RE_ADB_FILE_PULLED = re.compile("^.*: 1 file pulled, 0 skipped\\..*$")

    def unlink(self, path: str) -> None:
        os.unlink(path)

    def rmdir(self, path: str) -> None:
        os.rmdir(path)

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok = True)

    def realPath(self, path: str) -> str:
        return os.path.realpath(path)

    def lstat(self, path: str) -> os.stat_result:
        return os.lstat(path)

    def lstat_inDir(self, path: str) -> Iterable[Tuple[str, os.stat_result]]:
        for filename in os.listdir(path):
            yield filename, self.lstat(self.joinPaths(path, filename))

    def utime(self, path: str, times: Tuple[int, int]) -> None:
        os.utime(path, times)

    def joinPaths(self, base: str, leaf: str) -> str:
        return os.path.join(base, leaf)

    def normPath(self, path: str) -> str:
        return os.path.normpath(path)

    def pushFileHere(self, source: str, destination: str) -> None:
        with subprocess.Popen(
            self.adb_arguments + ["pull", source, destination],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT
        ) as proc:
            while adbLine := proc.stdout.readline():
                adbLine = adbLine.decode().rstrip("\r\n")
                if not self.RE_ADB_FILE_PULLED.fullmatch(adbLine):
                    criticalLogExit("Line not captured: '{}'".format(adbLine))
