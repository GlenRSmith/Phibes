pytest --basetemp=./basetemp --verbose --capture=no $1
pytest --cov=privacy_playground tests
