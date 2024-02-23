# UE4EnvironmentRecreation
Python scripts that take asset orientation from Maya and automatically recreates the scene in UE4

# NOTE THIS!
This tool was developed at my previous position.  It was a life-saver for environment artists as they could build out a scene in Maya, and with just 2 clicks, recreate that entire scene in UE4.

# How this works
In Maya, the 3d artist lays out the scene with an available env. asset kit.
When satisfied, they can use the Maya script to capture the number of unique assets used, and the orientation or each instance of said asset.  The orientation data as well as the source asset name would be written to a local txt file.
So if a chair mesh was used 10 times, the txt file would contain 10 chair entries, each with its own unique locatino, rotation and scale values.  

In UE4, it's important that the unique assets already exist in the content browser (i.e. have already been imported into the editor). 
The 2nd Python script, executed through UE4, will read the txt file.  It will identify the unique assets.  Locate it in the content browser.  Spawn the actors into the world.  Set the orientation on the actor. 
If more instances of the asset exist, it will continue to spawn more actors giving each their own orientation.

If there were 10 chairs in the Maya scene, this tool will create 10 chair actors in UE4 and make sure each of them adopt the same orientation values as they had in Maya (with care given to rotation coordinate system).
