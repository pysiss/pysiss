# PyPI release checklist

## Make release branch

- [ ] Use git-flow to generate release `git flow release start <version_number>`
- [ ] Update version number in `setup.py`
- [ ] Change badge branch references in `README.md` 
- [ ] Run the tests: `python setup.py test`
- [ ] Commit the changes: `git commit -am "Bump version number, run tests"`

## Make release distribution

- [ ] Build the source distribution: `python setup.py sdist`
- [ ] Test that the sdist installs:
```
mktmpenv
cd dist
tar xzvf my_project-0.1.1.tar.gz
cd my_project-0.1.1/
python setup.py install
<try out my_project>
deactivate
```
- [ ] Merge changes to master and develop `git flow release finish <version_number>`

## Release on PyPI

- [ ] Upload sdist to PyPI: `python setup.py sdist upload` _Todo: need to really do this on pypi testing rather than production_
- [ ] Test that it pip installs:
```
mktmpenv
pip install my_project
<try out my_project>
deactivate
```
- [ ] Check the PyPI listing page to make sure that the README, release notes, and roadmap display properly. If not, copy and paste the RestructuredText into http://rst.ninjs.org/ to find out what broke the formatting.
