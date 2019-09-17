from cx_Freeze import setup, Executable
from datetime import date

#Create a version number for the build (based on the date (YY.MM.DD))
vers = "build-{}".format(date.today().__str__()[2:].replace("-", "."))

exeName = "pex2csv.exe" # The name of the final executable

#The output directory for the build
buildDir = "../pex2csv_exe"

setup(
    name = "pex2csv", #Name of executable
    version = vers,
    description = "Vector Mapper for the AD-EYE platform",
    options = {"build_exe": {"build_exe": buildDir}},
    executables = [Executable("main.py", targetName=exeName)]
)

#Write a .txt file containing the version number next to the exe
with open("{}/version.txt".format(buildDir), "w") as f:
    f.write(vers)
