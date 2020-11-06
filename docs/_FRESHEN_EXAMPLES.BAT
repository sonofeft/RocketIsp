
python copy_example_to_static.py Apollo_SPS.py
python copy_example_to_static.py plot_opt_mr.py
python copy_example_to_static.py hipat_at_opt_mr.py
python copy_example_to_static.py quick_test.py
python copy_example_to_static.py thruster_only.py
python copy_example_to_static.py effdiv_simple.py
python copy_example_to_static.py effdiv_monte.py
python copy_example_to_static.py effdiv_monte_Rthrt.py
python copy_example_to_static.py plot_example_results.py
python copy_example_to_static.py plot_odekf.py
python copy_example_to_static.py plot_eff_mixing_angle.py

rem ======= move to example_scripts area =============
cd .\_static\example_scripts

rem ==================== thruster_only =======================
python thruster_only.py > thruster_only.out

rem ==================== effdiv_simple =======================
python effdiv_simple.py > effdiv_simple.out

rem ==================== effdiv_monte =======================
python effdiv_monte.py > effdiv_monte.out

rem ==================== plot_example_results =======================
python plot_example_results.py > plot_example_results.out

rem ==================== plot_eff_mixing_angle =======================
python plot_eff_mixing_angle.py > plot_eff_mixing_angle.out

rem ==================== plot_odekf =======================
python plot_odekf.py > plot_odekf.out

rem ==================== effdiv_monte_Rthrt =======================
python effdiv_monte_Rthrt.py > effdiv_monte_Rthrt.out

rem ==================== quick_test =======================
python quick_test.py > quick_test.out

rem ====================== Apollo_SPS ==================================================
python Apollo_SPS.py > Apollo_SPS.out

rem ====================== plot_opt_mr --> HiPAT_NTO_N2H4_IspDel.png ===================
python plot_opt_mr.py  > plot_opt_mr.out
copy HiPAT_NTO_N2H4_IspDel.png ..\HiPAT_NTO_N2H4_IspDel.png /y

rem ===================== hipat_at_opt_mr =============================
python hipat_at_opt_mr.py  > hipat_at_opt_mr.out

rem ---------------- return up 2 ---------------------
cd ..
cd ..

rem ==================== xxx =======================
