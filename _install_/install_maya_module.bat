
:: copy_paste_overload is determined by the current folder name
for %%I in (.) do set copy_paste_overload=%%~nxI
SET CLEAN_copy_paste_overload=%copy_paste_overload:-=_%

:: Check if modules folder exists
if not exist %UserProfile%\Documents\maya\modules mkdir %UserProfile%\Documents\maya\modules

:: Delete .mod file if it already exists
if exist %UserProfile%\Documents\maya\modules\%copy_paste_overload%.mod del %UserProfile%\Documents\maya\modules\%copy_paste_overload%.mod

:: Create file with contents in users maya/modules folder
(echo|set /p=+ %copy_paste_overload% 1.0 %CD%\_install_ & echo; & echo icons: ..\%CLEAN_copy_paste_overload%\icons)>%UserProfile%\Documents\maya\modules\%copy_paste_overload%.mod

:: end print
echo .mod file created at %UserProfile%\Documents\maya\modules\%copy_paste_overload%.mod


