.PHONY: test grade demo

ifneq ($(strip $(PART)),)
ifeq ($(filter $(PART),1 2 3 4 5 6 7),)
$(error PART must be one of 1 2 3 4 5 6 7)
endif
endif

test:
	PYTHONPATH=../.. python3 -m pytest -q tests

grade:
	PYTHONPATH=../.. LAB02_GRADE=1 python3 -m pytest -q tests $(if $(PART),-k part$(PART))

demo:
	python3 part1_des_bruteforce/samples/des_roundtrip.py
