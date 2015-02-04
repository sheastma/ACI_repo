[Environment]::SetEnvironmentVariable("Path", "$env:Path;C:\Python27\;C:\Python27\Scripts\", "User")
python -m pip install --upgrade pip
python ez_setup.py
python get-pip.py
pip uninstall acicobra
pip install --use-wheel pyopenssl
$name = Read-Host 'What version of code are you running i.e. 2j?'

$as = "acicobra-1.0_" + $name + "-py2.7.egg"
$as_2 = "acimodel-1.0_" + $name + "-py2.7.egg"

Get-ChildItem acicobrasdk.egg | Rename-Item -NewName { $_.name -replace "acicobrasdk.egg", $as}
Get-ChildItem acicobramodel.egg | Rename-Item -NewName { $_.name -replace "acicobramodel.egg", $as_2}
easy_install -Z --find-links ./ acicobra
python setup.py install
#python test_connection.py
powershell -noexit .\test_connection.py