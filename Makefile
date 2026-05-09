PYTHON=poetry run python

install:
	python -m pipx install poetry
	poetry install

run:
	${PYTHON} ./main.py ./maps/challenger/01_the_impossible_dream.txt --visual

debug:
	${PYTHON} -m pdb ./main.py ./maps/challenger/01_the_impossible_dream.txt --visual


clean:
	rm -rf __pycache__ .mypy_cache


lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

