pre-push: lint

lint: black-lint isort-lint

format: isort-format black-format


git-setup-hooks:
	rm -f .git/hooks/pre-push && ln -s `readlink -f scripts/hooks/pre-push` ".git/hooks/pre-push"


black-lint:
	black --check .

black-format:
	black .


isort-lint:
	isort -c -rc --jobs 10 --diff .

isort-format:
	isort -rc .
