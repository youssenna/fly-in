PYTHON=poetry run python
MYPY= poetry run mypy
FLAKE8 = poetry run flake8

install:
	python -m pip install poetry
	poetry install

run:
	${PYTHON} ./main.py ./maps/challenger/01_the_impossible_dream.txt --visual

debug:
	${PYTHON} -m pdb ./main.py ./maps/challenger/01_the_impossible_dream.txt --visual


clean:
	rm -rf __pycache__ .mypy_cache


lint:
	${MYPY} . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	${FLAKE8} .

