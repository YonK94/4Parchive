@echo off
set PYTHONPATH=%~dp0..\..
python -m scripts.data_extractor.extractor %*
pause