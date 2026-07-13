@echo off
dir /b *.py > "%temp%\pylist.txt"
type "%temp%\pylist.txt" | clip
del "%temp%\pylist.txt"
