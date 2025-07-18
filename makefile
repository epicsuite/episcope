SCRATCH_DIR=testing/scratch

null:
	@:

clean:
	rm -rf build
	rm -rf episcope.egg-info
	rm -rf dist
	rm -rf $(SCRATCH_DIR)

module:
	rm -rf build
	rm -rf *.egg-info
	rm -rf dist
	python -m build

module-upload:
	twine upload dist/*

module-test-upload:
	twine upload --repository testpypi dist/* 

how-to:
	@echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple episcope" 

