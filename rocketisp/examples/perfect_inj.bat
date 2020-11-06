

rem oxName='N2O4', fuelName='MMH', Fvac=100.0, PcNominal=100.0, epsNominal=100.0)

python.exe plot_PI.py N2O4 MMH 100 100 100
python.exe plot_PI.py N2O4 MMH 100000 2000 10

python.exe plot_PI.py LOX RP1 100000 1000 10
python.exe plot_PI.py LOX RP1 100000 2000 100

python.exe plot_PI.py LOX LH2 100 100 100
python.exe plot_PI.py LOX LH2 100000 2000 10
