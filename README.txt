#Install Anaconda distrib via Spyder :
#Firewall might interfere with http connection, if so, type:
conda config --set ssl_verify no
#then
conda install bokeh

#Verifier la version de bokeh
import bokeh 
bokeh.__version__


Dans Windows :

1. Dans le répertoire Python,
Lancer "start.bat"
(execute une cmd qui lance "activate.bat" situé dans
maison :
"C:\Users\cgaro\Anaconda3\Scripts\activate.bat"
travail :
"C:\Users\clementine.garoche\AppData\Local\Continuum\anaconda3\Scripts\activate.bat").

2. Dans la console ainsi ouverte, taper la commande :
"bokeh serve Molecule --show" (lance le server avec Tornado et l'appli, dans "http://localhost:5006/Molecule").

3. Pour terminer l'app, "ctrl-C"