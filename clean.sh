find . -name "__pycache__" | xargs rm -r
rm -rf build dist *.egg-info
rm -r tests/mocks/cache
python setup.py update_version