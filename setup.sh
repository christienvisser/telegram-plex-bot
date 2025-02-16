# setup virtual env if not exists
if [ ! -d ".venv" ]; then
        echo ".venv does not exist. Setting up (might take a while)"
        python -m venv .venv
else
        echo ".venv already present, continuing.."
fi

# activate it
source .venv/bin/activate

# and install dependencies
pip install -r requirements.txt
