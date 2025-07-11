SET mypath=%~dp0

pyreverse -o pdf -d %mypath%auto_generated ^
 --all-associated ^
 --all-ancestors ^
%mypath%room_unit_gateway\

pylint --disable=missing-class-docstring ^
 --disable=missing-function-docstring ^
 --disable=invalid-name ^
 --disable=line-too-long ^
 --disable=logging-fstring-interpolation ^
 --disable=logging-format-interpolation ^
 --disable=logging-not-lazy ^
 --disable=wrong-import-position ^
 --disable=broad-exception-caught ^
 --disable=too-few-public-methods ^
 --disable=fixme ^
 --disable=wrong-import-order ^
 --disable=import-error ^
 --disable=too-many-arguments ^
 --disable=too-many-locals ^
 --disable=attribute-defined-outside-init ^
 --disable=undefined-variable ^
 --disable=not-callable ^
 --disable=too-many-instance-attributes ^
 --disable=wildcard-import ^
 %mypath%room_unit_gateway\
 