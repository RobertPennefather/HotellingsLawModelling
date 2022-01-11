Simulation 
To start the simulation with 3 companies, having 4, 7 and 2 shops respectively, run
	python projectmain.py 4 7 2

With Limits 
Optional flags exist to include limits. To run with the default customer limit equation;
	python projectmain.py 4 7 2 -l 
The option also exists to set a custom limit. For example, to do so with a limit of 7; 
	python projectmain.py 4 7 2 -l 7
Limits are turned off by default. 

With Colour Pricing 
To enable the grid to display the price level of shops through opacity  (with lighter colours indicating higher prices, 
and darker colours indicating darker prices), add the flag -c;
	python projectmain.py 4 7 2 -c 
This is turned off by default. 

Adjust Grid Size 
To adjust the grid size to view the simulation in different sized worlds, simply add the flag -s followed by an integer. 
For example, grid size of 30 can be achieved with: 
	python projectmain.py 4 7 2 -s 30
The default is 20. 