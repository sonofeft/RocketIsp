
REM save path with setlocal
setlocal

REM --- Save the incoming PATH --- (extra insurance)
set "ORIG_PATH=%PATH%"

echo Altering Environment PATH

SET "MYPYTHONPATH=D:\py_versions\Python314_64" 
set PATH=C:\MinGW\mingw64\bin;C:\MinGW\mingw64\lib;%MYPYTHONPATH%;%MYPYTHONPATH%\Scripts;C:\Windows\System32

cd .\docs
D:\py_versions\Python314_64\Scripts\sphinx-build.exe -b html -d _build/doctrees  . _build/html
cd ..

xcopy /S .\docs\_build\html .\rocketcea\sphinx_html /y

REM --- Restore PATH before exiting ---
set "PATH=%ORIG_PATH%"
echo PATH restored.

REM restore path with endlocal
endlocal

