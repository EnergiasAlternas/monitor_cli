
usar uv

uv init 
uv venv	--python 3.10
uv add -r requeriments.txt

source .venv/bin/activate

uv run monitor.py
uv run logger.py
