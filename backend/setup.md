# 1. Create a virtual environment named "venv"
python -m venv venv

# 2. Activate the virtual environment
.\venv\Scripts\activate

# 3. Install the dependencies
pip install -r requirements.txt

# 4. Create an empty .env file for your API keys
echo GROQ_API_KEY=your_key_here > .env
echo TAVILY_API_KEY=your_key_here >> .env
echo DEEPGRAM_API_KEY=your_key_here >> .env

echo Setup complete! Open the .env file to add your keys.

Once you run those commands, make sure your .env file is filled out correctly. It should look exactly like this:

GROQ_API_KEY=gsk_your_groq_key_here
TAVILY_API_KEY=tvly_your_tavily_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here