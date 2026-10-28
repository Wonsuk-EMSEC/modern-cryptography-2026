.PHONY: test grade

test:
	PYTHONPATH=../.. python3 -m unittest discover -s tests -p 'test_*.py' -v

grade:
	PYTHONPATH=../.. python3 -m labs.lab03.check --part $(PART)
