# Convenience entrypoint so you can simply run: streamlit run streamlit_app.py
import os
import runpy

# Ensure we run the Home page under app/
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)
runpy.run_path("app/Home.py")
