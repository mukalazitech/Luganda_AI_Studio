@echo off
:: ============================================================
:: nightly_harvest.bat — Luganda AI Nightly Data Factory
:: Runs every night via Windows Task Scheduler.
:: Harvests text corpus, then ingests into ChromaDB.
:: ============================================================

SET PROJECT=D:\projects\Luganda_AI_Studio
SET PYTHON=%PROJECT%\venv\Scripts\python.exe
SET LOG=%PROJECT%\data\harvest_run.log

echo. >> "%LOG%"
echo =============================== >> "%LOG%"
echo %DATE% %TIME% — Nightly harvest started >> "%LOG%"
echo =============================== >> "%LOG%"

:: Step 1: Harvest text from all sources
echo [1/2] Harvesting text corpus...
"%PYTHON%" "%PROJECT%\scripts\harvest_text.py" --source all >> "%LOG%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo HARVEST FAILED — check harvest_run.log >> "%LOG%"
    goto :done
)

:: Step 2: Ingest new files into ChromaDB
echo [2/2] Ingesting into ChromaDB...
"%PYTHON%" "%PROJECT%\scripts\ingest_dataset.py" >> "%LOG%" 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo INGEST FAILED — check harvest_run.log >> "%LOG%"
    goto :done
)

:: Step 3: Write briefing line for Hermes morning context
echo [status] Writing corpus briefing line...
"%PYTHON%" "%PROJECT%\scripts\corpus_status.py" --briefing > "%PROJECT%\data\corpus_briefing.txt" 2>&1
"%PYTHON%" "%PROJECT%\scripts\corpus_status.py" --json >> "%LOG%" 2>&1

echo %DATE% %TIME% — Nightly harvest DONE >> "%LOG%"

:done
echo Done.
