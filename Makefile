.PHONY: ahmed

all:
	@echo "Targets:"
	@echo "  ahmed     : create ahmed stl files"
	@echo "  calculate : generate database (can take forever)"

ahmed:
	cd ahmed; ./ahmed.sh

calculate:
	cd generator; python3 calculate.py
