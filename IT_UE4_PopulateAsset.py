"""
Script Name: IToys_PopulateAsset
Author: Gabe Wong, Technical Artist

Description:
This tool will read a config INI file from Maya's Export Tool.  This config file will contain a list of sections pertaining to copies of a mesh asset and will have
data on transforms like position, rotation and scale.  This tool run in UE4 will grab those, duplicate the mesh in the level and move/orient those duplicates
using the data in the config ini file.
"""

import unreal
import os, configparser

@unreal.uclass()
class GetEditorLevelLibrary(unreal.EditorLevelLibrary):
    pass

@unreal.uclass()
class EditorUtility(unreal.GlobalEditorUtilityBase):
    pass

editorUtility = EditorUtility()
editorLevelLib = GetEditorLevelLibrary()

# Get and store the path to the data file, and the full path including file name.
dataFilePath = os.path.join( os.path.dirname( __file__ ), '../../../config/' )
dataFile = dataFilePath + 'it_export_dataFile.ini'
config = configparser.ConfigParser()
d = open(dataFile, "r")
config.read(dataFile)
allSections = config.sections()

if not os.path.exists(dataFile):
    unreal.log_error("No data file exists.  Generate one using the Maya IT_ExportData tool.")
    quit()

selectedAssets = editorUtility.get_selected_assets()

if not selectedAssets:
    unreal.log_error("You have nothing selected.  Please select the mesh(es) that you want to populate in the content browser.")
    quit()

for asset in selectedAssets:
    assetName = asset.get_name()
    for section in allSections:
        meshSourceName = config.get(section, 'meshSourceName')

        if assetName == meshSourceName:
            unreal.log(assetName)
            locationX = float(config.get(section, 'translateX'))
            locationY = float(config.get(section, 'translateY'))
            locationZ = float(config.get(section, 'translateZ'))
            rotationX = float(config.get(section, 'rotateX'))
            rotationY = float(config.get(section, 'rotateY'))
            rotationZ = float(config.get(section, 'rotateZ'))
            scaleX = float(config.get(section, 'scaleX'))
            scaleY = float(config.get(section, 'scaleY'))
            scaleZ = float(config.get(section, 'scaleZ'))
            bAssetFromUE4 = str(config.get(section, 'assetFromUE4'))

            if bAssetFromUE4 == "true":
                rotationX = rotationX + 90

            # Call UE C++ function to convert from Maya coordinate system to UE4 coordinate system
            rotatorValues = unreal.ODPython.rotator_from_maya(rotationX, rotationY, rotationZ)

            # Create new actor in the level environment with the adopted location, rotation and scale values taken from the config ini file
            newAsset = editorLevelLib.spawn_actor_from_object(asset, location=[locationX,locationZ,locationY], rotation=rotatorValues)
            newAsset.set_actor_scale3d([scaleX,scaleZ,scaleY])

"""
unreal.ODPython.cpp

FRotator UODPython::RotatorFromMaya(float Rx, float Ry, float Rz)
{
    // Adapted from https://stackoverflow.com/questions/57025469/how-to-convert-euler-rotations-from-one-coordinate-system-to-another-right-hand
    const float Rad = 0.0174532925199444; // FQuat needs Radians. So degree * Pi/180 | Pi/180 = 0.0174532...

    // x, z, y intentionally maps to x, y, z
    FQuat Qx(FVector(1, 0, 0), -Rx * Rad);
    FQuat Qz(FVector(0, 0, 1), -Ry * Rad);
    FQuat Qy(FVector(0, 1, 0), -Rz * Rad);

    FQuat Qu = Qy * Qz * Qx; // This ordering appears to work as expected.

    FRotator Rotation(Qu);
    return Rotation;
}
"""