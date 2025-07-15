SET mypath=%~dp0

pyreverse -o pdf -d %mypath%auto_generated ^
 --all-associated ^
 --all-ancestors ^
%mypath%aiplaning\

pylint --disable=invalid-name ^
 --disable=line-too-long ^
 --disable=missing-function-docstring ^
 --disable=fixme ^
 --disable=too-many-arguments ^
 --disable=too-many-locals ^
 --disable=unnecessary-lambda-assignment ^
 --disable=import-error ^
 %mypath%aiplaning\
