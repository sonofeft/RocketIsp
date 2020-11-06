
python copy_example_to_static.py %1.py

rem ======= move to example_scripts area =============
cd .\_static\example_scripts

rem ==================== xxx =======================
python %1.py > %1.out


rem ---------------- return up 2 ---------------------
cd ..
cd ..

