python3 -m coverage run --source CapyBack,board,chat,utils -m pytest --junit-xml=xunit-reports/xunit-result.xml
ret=$?
python3 -m coverage xml -o coverage-reports/coverage.xml
python3 -m coverage report
exit $ret