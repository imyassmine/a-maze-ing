# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LAYOUT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEFAULT			= \033[0m
GREEN			= \033[1;32m
CYAN			= \033[1;36m

ARGS			?= config.txt

define ANIMATION
				@for frame in ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏; do \
				printf "$$frame $(1)...\r"; \
				sleep 0.02; \
				done; \
				printf "\n"
endef


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ RULES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

install:
				$(call ANIMATION,Installing project dependencies)
				@uv sync

run:
				@uv run python a_maze_ing.py $(ARGS)

package:
				$(call ANIMATION,Building the mazegen package)
				@uv build

debug:
				@uv run python -m pdb a_maze_ing.py $(ARGS)

clean:
				$(call ANIMATION,Removing compiled files and caches)
				@rm -rf __pycache__ */__pycache__ */*/__pycache__ .pytest_cache .mypy_cache

lint:
				@uv run flake8 a_maze_ing.py mazegen.py src
				@uv run mypy a_maze_ing.py mazegen.py src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
				@uv run flake8 a_maze_ing.py mazegen.py src
				@uv run mypy a_maze_ing.py mazegen.py src --strict


help:
				@printf "Usage: make [target]\n"
				@printf "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
				@printf "$(CYAN)install$(DEFAULT)		- Install project dependencies\n"
				@printf "$(CYAN)run$(DEFAULT)		- Run the maze generator (default config: config.txt, use ARGS=\"<config_file>\" to override)\n"
				@printf "$(CYAN)package$(DEFAULT)		- Build the mazegen pip package (wheel + sdist in dist/)\n"
				@printf "$(CYAN)debug$(DEFAULT)		- Run the maze generator in debug mode (use ARGS=\"<config_file>\" to override)\n"
				@printf "$(CYAN)clean$(DEFAULT)		- Remove compiled Python files and caches\n"
				@printf "$(CYAN)lint$(DEFAULT)		- Run linter and type checker to ensure code quality\n"
				@printf "$(CYAN)lint-strict$(DEFAULT)	- Run linter and type checker with strict settings\n"
				@printf "$(CYAN)help$(DEFAULT)		- Show this help message\n"

.PHONY:			install run package debug clean lint lint-strict help
